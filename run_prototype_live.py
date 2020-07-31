import collections
from datetime import datetime as dt
from datetime import timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import feedparser
import json
from lxml import html
import nltk
nltk.data.path.append('nltk/nltk_data')
import numpy as np
import pandas as pd
import re
import requests
import sec_scraper
import smtplib
import ssl
import time
pd.set_option("display.max_rows", None, "display.max_columns", None)

def get_current_spacs(file_path_current, write=False):
    """Update list of current spac tickers."""
    df_traq = pd.read_csv('https://docs.google.com/spreadsheets/d/14BY8snyHMbUReQVRgZxv4U4l1ak79dWFIymhrLbQpSo/'
                          'export?gid=0&format=csv', header=2)
    df_traq.columns = [x.replace('\n','') for x in df_traq.columns]
    df_spacs_existing = pd.read_csv(file_path_current)
    df_spacs_existing.drop_duplicates(inplace=True)
    combined_spacs = df_spacs_existing['Ticker'].append(df_traq['Issuer Symbol'])
    df_spacs_new = pd.DataFrame(combined_spacs, columns=['Ticker'])
    df_spacs_new.drop_duplicates(inplace=True)
    df_spacs_new.reset_index(inplace=True, drop=True)
    new_added_tickers = [x for x in df_spacs_new['Ticker'].tolist()
                         if x not in df_spacs_existing['Ticker'].tolist()]
    if len(new_added_tickers) > 0:
        print('newly added tickers:', new_added_tickers)
    try: # cannot save file on aws lambda
        if write:
            df_spacs_new.to_csv(file_path_current, index=False)
    except:
        print('Error: could not write new spac list to file')
    print(df_spacs_new.tail())
    return df_spacs_new

def get_ticker_to_cik():
    """Get cik from ticker."""
    ticker_to_cik = pd.read_csv('https://www.sec.gov/include/ticker.txt', sep='\t',
                                header=None, names=['ticker','cik'])
    ticker_to_cik['ticker'] = ticker_to_cik.ticker.str.upper()
    ticker_to_cik['cik'] = ticker_to_cik.cik.astype(str)
    return ticker_to_cik

def get_cik_to_name():
    """Get company name from cik."""
    cik_to_name = pd.read_json('https://www.sec.gov/files/company_tickers.json').transpose()
    cik_to_name['ticker'] = cik_to_name.ticker.str.upper()
    cik_to_name['cik'] = cik_to_name.cik_str.astype(str)
    return cik_to_name

def process_current_spacs(spac_list_current):
    """Process list of new spac tickers."""       
    # get ticker to cik and cik to company name file, then merge
    ticker_to_cik = get_ticker_to_cik()
    cik_to_name = get_cik_to_name()
    spac_list_current = spac_list_current.merge(ticker_to_cik, how='left', left_on='Ticker', right_on='ticker')
    spac_list_current = spac_list_current.merge(cik_to_name[['cik','ticker','title']], how='left', on=['cik','ticker'])
    
    # some current spacs have not split from units to stock + warrants so ticker in sec different
    ticker_unit = pd.DataFrame(spac_list_current[spac_list_current.ticker.isna()]['Ticker'])
    ticker_unit['Ticker'] = ticker_unit.Ticker + 'U'
    ticker_unit = ticker_unit.merge(ticker_to_cik, how='left', left_on='Ticker', right_on='ticker')
    ticker_unit = ticker_unit.merge(cik_to_name[['cik','ticker','title']], how='left', on=['cik','ticker'])
    ticker_unit['Ticker'] = ticker_unit.Ticker.apply(lambda x: x[:-1] if not pd.isnull(x) else x)
    ticker_unit['ticker'] = ticker_unit.ticker.apply(lambda x: x[:-1] if not pd.isnull(x) else x)
    ticker_unit_other = pd.DataFrame(ticker_unit[ticker_unit.ticker.isna()]['Ticker'])
    ticker_unit_other['Ticker'] = ticker_unit_other.Ticker.apply(lambda x: x+'-UN')
    ticker_unit_other = ticker_unit_other.merge(ticker_to_cik, how='left', left_on='Ticker', right_on='ticker')
    ticker_unit_other = ticker_unit_other.merge(cik_to_name[['cik','ticker','title']], how='left', on=['cik','ticker'])
    ticker_unit_other['Ticker'] = ticker_unit_other.Ticker.apply(lambda x: x[:-3] if not pd.isnull(x) else x)
    ticker_unit_other['ticker'] = ticker_unit_other.ticker.apply(lambda x: x[:-3] if not pd.isnull(x) else x)
    ticker_unit = ticker_unit.append(ticker_unit_other)
    ticker_unit.dropna(inplace=True)
    
    # append tickers found using 'U' and '-UN'
    spac_list_current = spac_list_current[~spac_list_current.Ticker.isin(ticker_unit.Ticker)]
    spac_list_current = spac_list_current.append(ticker_unit)
    
    print('count current spacs:', len(spac_list_current))
    print('count nan in current spacs:', len(spac_list_current[spac_list_current.ticker.isna()]), '\n')
    
    return spac_list_current

def basic_text_cleaning(text):
    """Basic text cleaning."""
    text = text.replace('\n',' ').replace('\xa0',' ') # replace some unicode characters
    text = re.sub(' +', ' ', text) # remove extra spaces
    text = text.lower()
    return text

def get_forms_text(company_name, cik_id, form_type):
    """Returns dataframe of all 8-Ks for a given symbol. Columns: date, accepted_time, form, text."""
    try:
        c = sec_scraper.Company(company_name, cik_id, timeout=20)
        filings = c.get_all_filings(filing_type=form_type, no_of_documents=100)
    except:
        print('timed out')
        return None
    dates = [f.accepted_date.strftime('%Y-%m-%d %H:%M:%S') for f in filings]
    documents = [basic_text_cleaning(f.documents[0]) for f in filings]
    print(company_name, cik_id)
    df = pd.DataFrame(list(zip(dates, documents)), columns=['date','text'])
    df['form'] = '8-K'
    df['accepted_time'] = df.date
    df['date'] = df.date.apply(lambda x: x[0:10])
    return df

def basic_text_match(df_form, substring):
    """Basic text match."""
    df_form[substring.replace(' ','_')+'_found'] = df_form.text.apply(lambda x: 1 if substring in x else 0)
    return df_form

def agg_form_8K(spac_list, write=False):
    """Returns dataframe of 8-Ks for all symbols. Columns: date, accepted_time, symbol, 
    form, text, letter_of_intent_found, business_combination_agreement_found."""
    df_form_8K_agg = pd.DataFrame()
    count_missing_8K = 0
    for ind in range(0, len(spac_list)):
        row = spac_list.iloc[ind]
        print('\nindex:', ind)
        print(row.ticker)

        # get form 8Ks
        df_form_8K = get_forms_text(company_name=row.title, cik_id=row.cik, form_type='8-K')
        if df_form_8K is None or len(df_form_8K)==0:
            print('no 8Ks found (or timed out), skipping...\n')
            count_missing_8K = count_missing_8K + 1
            continue
        else:
            # simple classifier
            df_form_8K = basic_text_match(df_form_8K, 'letter of intent')
            df_form_8K = basic_text_match(df_form_8K, 'business combination agreement')
            if write:
                df_form_8K.to_csv('data/sec_filings_df/'+row.ticker+'_sec_forms.csv', index=False)

        # append to aggregate dataframe
        if len(df_form_8K)!=0:
            df_form_8K['symbol'] = row.ticker
        df_form_8K_agg = df_form_8K_agg.append(df_form_8K)

    print('\ncount symbols missing 8-Ks:', count_missing_8K)
        
    # drop duplicates on date + symbol
    # todo: if date has multipled 8-Ks, concatenate text instead of dropping
    print('count 8-Ks before dropping duplicates:', len(df_form_8K_agg))
    df_form_8K_agg = df_form_8K_agg.drop_duplicates(subset=['date','symbol'])
    print('count 8-Ks after dropping duplicates:', len(df_form_8K_agg))
    
    # drop unused columns and nans and sort
    df_form_8K_agg.drop(columns=['letter_of_intent_found',
                                 'business_combination_agreement_found',
                                 'form'], inplace=True)
    df_form_8K_agg.dropna(inplace=True)
    print('count 8-Ks after dropping nans:', len(df_form_8K_agg))
    df_form_8K_agg.sort_values(by='accepted_time', inplace=True)
    df_form_8K_agg.reset_index(inplace=True, drop=True)
    
    return df_form_8K_agg

def remove_header_footer(text):
    """Remove standard header and footer from 8-K and clean text further."""
    # remove/replace some unicode characters
    text = text.replace('\t','') # remove tabs
    text = text.replace('\x93','"') # 1st quotation mark type
    text = text.replace('\x94','"') # 2nd quotation mark type
    text = text.replace('”', '"') # weird unicode/ascii conversion issue (1st quotation mark type)
    text = text.replace('“', '"') # weird unicode/ascii conversion issue (2nd quotation mark type)
    
    # remove forward looking statement section
    forward_looking_statement_start = ['forward-looking statements this current report',
                                       'forward looking statements certain statements',
                                       'forward-looking statements this report',
                                       'forward-looking statements the company makes',
                                       'forward-looking statements certain of the matters',
                                       'forward-looking statements this communication']
    forward_looking_statement_end = ['undue reliance should not be placed upon the forward-looking statements',
                                     'whether as a result of new information, future events or otherwise, except as required by law',
                                     'conditions or circumstances on which any such statement is based, except as required by applicable law']
    for forward_start in forward_looking_statement_start:
        for forward_end in forward_looking_statement_end:
            ind_start = text.find(forward_start)
            ind_end = text.find(forward_end)
            if ind_start!=-1 and ind_end!=-1:
                text = text[0:ind_start] + text[ind_end+len(forward_end):]

    # remove everything in header and footer
    ind_start = text.find('financial accounting standards provided pursuant to section 13(a) of the exchange act')
    ind_end = text.find('signature pursuant to the requirements of the securities exchange act of 1934')
    text = text[ind_start:ind_end]
    
    # additional text to remove
    text_to_remove = [
        'financial accounting standards provided pursuant to section 13(a) of the exchange act'
    ]
    for rm in text_to_remove:
        text = text.replace(rm,'')
    
    return text

def get_item_subheaders(text, subheaders_only):
    """Returns either list of subheaders in 8-K or list of subheaders content."""
    subheaders = re.findall('item [0-9]+\.[0-9]+', text)
    subheaders = list(collections.OrderedDict.fromkeys(subheaders)) # handle cases where subheader mentioned in content
    subtexts = []
    for i in range(0,len(subheaders)):
        if i+1==len(subheaders):
            subtext = text[text.find(subheaders[i]):]
        else:
            subtext = text[text.find(subheaders[i]):text.find(subheaders[i+1])]
        if 'item 9.01 financial statements and exhibits' in subtext:
            continue
        else:
            subtexts.append(subtext)
    
    # drop these items (useless text)
    drop_item_list = ['item 9.01']
    
    if subheaders_only:
        return [x for x in subheaders if x not in drop_item_list]
    return subtexts

def count_keywords(x, keywords):
    """Count number of occurences of keywords in keyword list."""
    count = 0
    for keyword in keywords:
        count = count + x.count(keyword)
    return count

def add_subheader_item_features(df_ret, item_features):
    """Add binary subheader features, 1 if subheader in text and 0 otherwise."""
    for col in item_features:
        df_ret[col] = 0
    for i in range(0, len(df_ret)):
        text = df_ret.loc[i]['text']
        items = get_item_subheaders(text, subheaders_only=True)
        for item in items:
            df_ret.loc[i,item] = 1
    return df_ret

def convert_vote_count_to_int(x):
    """Convert vote string to int."""
    # to indicate 0 votes, sometimes 8-K has dash (two types) instead of 0
    if '—' in x or '-' in x or 'n/a' in x:
        return 0
    try:
        x = int(x.replace(',',''))
    except:
        return np.nan
    return x

def parse_vote_results(x):
    """Return votes for, votes against, abstain and broker non-votes."""
    vote_string = 'for against abstain broker non-votes'
    ind_vote = x['text'].find(vote_string)
    if ind_vote == -1:
        vote_string = 'for against abstentions broker non-votes'
        ind_vote = x['text'].find(vote_string)
    if ind_vote != -1:
        text_split = x['text'][(ind_vote+len(vote_string)):].lstrip().split(' ')
        votes_for = convert_vote_count_to_int(text_split[0])
        votes_against = convert_vote_count_to_int(text_split[1])
        votes_abstain = convert_vote_count_to_int(text_split[2])
        votes_broker_non_votes = convert_vote_count_to_int(text_split[3])
        if np.isnan(votes_for) or np.isnan(votes_against) or np.isnan(votes_abstain) or np.isnan(votes_broker_non_votes):
            print('something wrong with parse_vote_results for', x.symbol, 'on', x.date)
        return pd.Series([votes_for, votes_against, votes_abstain, votes_broker_non_votes])
    return pd.Series([np.nan, np.nan, np.nan, np.nan])

def parse_redemptions(x):
    """Return number of redeemed shares."""
    string_redemption_1 = 'in connection with the extension'
    string_redemption_2 = 'in connection with the closing'
    string_redemption_3 = 'in advance of the special meeting'
    string_redemption_4 = 'in connection with the special meeting'
    redemption_sentence = [sentence for sentence in x.text.split('.') if
                           string_redemption_1 in sentence
                           and ('redeem' in sentence or 'redemp' in sentence)]
    if len(redemption_sentence)==0:
        redemption_sentence = [sentence for sentence in x.text.split('.') if
                               string_redemption_2 in sentence
                               and ('redeem' in sentence or 'redemp' in sentence)]
    if len(redemption_sentence)==0:
        redemption_sentence = [sentence for sentence in x.text.split('.') if
                               string_redemption_3 in sentence
                               and ('redeem' in sentence or 'redemp' in sentence)]
    if len(redemption_sentence)==0:
        redemption_sentence = [sentence for sentence in x.text.split('.') if
                               string_redemption_4 in sentence
                               and ('redeem' in sentence or 'redemp' in sentence)]
    if len(redemption_sentence)==0:
        return np.nan
    redemption_sentence = redemption_sentence[0].lstrip().replace(',','')
    redemption_sentence = re.sub(r'[\$]{1}[\d,]+\.?\d{0,2}', '', redemption_sentence) # replace $_#_
    shares_regex_strong = re.findall('[0-9]+ shares', redemption_sentence)
    shares_regex_weak = re.findall('[0-9]+', redemption_sentence)
    if len(shares_regex_weak)==1:
        if len(shares_regex_strong)==1:
            shares = int(shares_regex_strong[0].replace('shares','').replace(' ',''))
        elif len(shares_regex_strong)==0:
            shares = int(shares_regex_weak[0])
        else:
            shares = np.nan
    else:
        if 'none' in redemption_sentence:
            shares = 0
        else:
            shares = np.nan
    return shares

def add_self_engineered_features(df_ret):
    """Add self engineered features from keyword lists."""
    # define key word lists
    keywords_list_loi = ['letter of intent','entry into a definitive agreement','enter into a definitive agreement',
    'entering into a definitive agreement','entered into a definitive agreement']
    keywords_list_business_combination_agreement = ['(the "business combination agreement")', '("business combination")']
    keywords_list_extension = ['(the "extension")']
    keywords_list_consummation = ['announcing the consummation']
    keywords_list_ipo = ['consummated its initial public offering ("ipo")', 'consummated its initial public offering (the "ipo")',
    'consummated an initial public offering ("ipo")', 'consummated an initial public offering (the "ipo")',
    'consummated the initial public offering ("ipo")', 'consummated the initial public offering (the "ipo")',
    'completed its initial public offering ("ipo")', 'completed its initial public offering (the "ipo")',
    'in connection with its initial public offering ("ipo") was declared effective',
    'in connection with its initial public offering (the "ipo") was declared effective']
    
    # compute counts
    df_ret['keywords_loi'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_loi))
    df_ret['keywords_business_combination_agreement'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_business_combination_agreement))
    df_ret['keywords_extension'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_extension))
    df_ret['keywords_consummation'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_consummation))
    df_ret['keywords_ipo'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_ipo))

    # add vote results (d.n.e for most 8-Ks, fill with nan)
    df_ret['votes_for'] = np.nan
    df_ret['votes_against'] = np.nan
    df_ret['votes_abstain'] = np.nan
    df_ret['votes_broker_non_votes'] = np.nan
    df_ret[['votes_for', 'votes_against', 'votes_abstain', 'votes_broker_non_votes']] = df_ret.apply(lambda x: parse_vote_results(x), axis=1)
    df_ret['vote_total'] = df_ret['votes_for'] + df_ret['votes_against'] + df_ret['votes_abstain'] + df_ret['votes_broker_non_votes']
    df_ret['%votes_for'] = df_ret['votes_for'] / df_ret['vote_total']
    df_ret['%vote_against'] = df_ret['votes_against'] / df_ret['vote_total']
    df_ret['%votes_abstain'] = df_ret['votes_abstain'] / df_ret['vote_total']
    df_ret['%votes_broker_non_votes'] = df_ret['votes_broker_non_votes'] / df_ret['vote_total']
    
    # add shares redeemed (d.n.e for most 8-Ks, fill with nan)
    df_ret['redeemed_shares'] = df_ret.apply(lambda x: parse_redemptions(x), axis=1)
    df_ret[r'%redeemed'] = df_ret['redeemed_shares'] / df_ret['vote_total']
    
    return df_ret

def classifier(x):
    """Rule based model to classify 8-K as 1 (buy warrant) or 0 (do nothing)."""
    if ~np.isnan(x['%vote_against']) & (x['%vote_against'] > .10):
        return 0
    elif x['keywords_ipo'] > 0:
        return 0
    else:
        if (x['keywords_loi'] > 0) & (x['item 2.03'] == 0):
            return 1
        elif (x['keywords_business_combination_agreement'] > 0) & (x['item 2.03'] == 0):
            return 1
        elif (x['keywords_consummation'] > 0) & (x['item 2.03'] == 0):
            return 1
        elif (x['keywords_extension'] > 0) & (x['item 2.03'] == 0):
            return 1
        else:
            return 0

def scrape_gnn(spac_list_current):
    """Parse Global Newswire RSS feed. Returns dataframe of articles containing SPAC tickers."""
    # parse global newswire rss feed
    rss_feed = feedparser.parse('https://www.globenewswire.com/RssFeed/orgclass/1/feedTitle/'
                                'GlobeNewswire%20-%20News%20about%20Public%20Companies')

    # get body (span[@class="article-body"]) for each entry. add to dataframe if body contains ticker
    df_gnn = pd.DataFrame(columns=['symbol','published_time', 'text'])
    for entry in rss_feed.entries:
        page = requests.get(entry['id'])
        tree = html.fromstring(page.content)
        body_paragraphs = tree.xpath('//span[@class="article-body"]//*/text()')
        body = ' '.join(body_paragraphs)

        for ticker in spac_list_current['Ticker']:
            if ticker in body:
                df_gnn = df_gnn.append(pd.Series({'symbol': ticker,
                                                  'published_time': entry['published'],
                                                  'text': body}), ignore_index=True)
    print('\nfinished searching all {} globalnewswire posts'.format(len(rss_feed.entries)))
    if len(df_gnn)==0:
        print('No SPAC aticles found\n')
        return None
    df_gnn = add_self_engineered_features(df_gnn)
    output_columns = ['symbol','published_time','keywords_loi','keywords_business_combination_agreement',
    'keywords_consummation','keywords_extension','%vote_against',r'%redeemed']
    df_gnn = df_gnn[output_columns]
    df_gnn.rename(columns={'keywords_business_combination_agreement':'keywords_bca'}, inplace=True)
    print('SPAC articles found:')   
    print(df_gnn, '\n')
    return df_gnn

def send_email(df_new_8Ks, df_pred_pos, df_gnn):
    """Send email with list of warrants to buy."""
    sender_email = 'wordquakeme2@gmail.com'
    receiver_email = 'wordquakeme2@gmail.com'
    host = 'email-smtp.us-east-1.amazonaws.com'
    port = 587
    smtp_username = 'AKIA3DFLMOEPQVDHFWFD'
    smtp_password = 'BKhl0+QS8NQujcuXpx3Bl7JyYbXm6wR/VxkqljR6EeCc'
    context = ssl.create_default_context()
    message = MIMEMultipart()
    message['Subject'] = 'BUY ALERT'
    if df_gnn is None:
        html = """\
        <html>
          <head></head>
          <body>
            8-Ks since yesterday:<br><br>
            {0}
            <br><br>
            Buy warrants for these symbols:<br><br>
            {1}
          </body>
        </html>
        """.format(df_new_8Ks.to_html(), df_pred_pos.to_html())
    else:
        html = """\
        <html>
          <head></head>
          <body>
            8-Ks since yesterday:<br><br>
            {0}
            <br><br>
            Buy warrants for these symbols:<br><br>
            {1}
            Global Newswire articles:<br><br>
            {2}
          </body>
        </html>
        """.format(df_new_8Ks.to_html(), df_pred_pos.to_html(), df_gnn.to_html())
    body = MIMEText(html, 'html')
    message.attach(body)
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls(context=context) # secure connection
        server.ehlo()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.close()
    except Exception as e:
        print('\nerror sending email:', e)
    else:
        print('\nemail sent')

def main():
    # load and update current spac list
    spac_list_current = get_current_spacs(file_path_current='data/spac_list_current.csv', write=True)

    # process current spac list
    spac_list_current = process_current_spacs(spac_list_current)

    # get returns following 8-Ks for current spacs
    start_time = time.time()
    df_form_8K_agg = agg_form_8K(spac_list_current, write=False)
    print('\nfinished scraping 8-Ks, time elapsed:', np.round(time.time() - start_time, 0), 'seconds')

    # get 8-Ks added yesterday or today
    min_date = (dt.today()-timedelta(days=1)).strftime('%Y-%m-%d')
    print('\noutput min date:', min_date)
    print('\n8-Ks since min date:')
    df_new_8Ks = df_form_8K_agg[df_form_8K_agg.date>=min_date][['symbol','accepted_time']]
    if len(df_new_8Ks)==0:
        print('none\n')
    else:
        print(df_new_8Ks, '\n')

    # features dataframe
    df_features = df_form_8K_agg.copy()

    # remove header and footer
    df_features['text'] = df_features.text.apply(lambda x: remove_header_footer(x))

    # define item features
    # item definitions: https://www.sec.gov/fast-answers/answersform8khtm.html
    # item faq: https://media2.mofo.com/documents/faq-form-8-k.pdf
    item_features = ['item 1.01','item 1.02','item 1.03','item 1.04','item 2.01','item 2.02','item 2.03',
                     'item 2.04','item 2.05','item 2.06','item 3.01','item 3.02','item 3.03','item 4.01',
                     'item 4.02','item 5.01','item 5.02','item 5.03','item 5.04','item 5.05','item 5.06',
                     'item 5.07','item 5.08','item 6.01','item 6.02','item 6.03','item 6.04','item 6.05',
                     'item 7.01','item 8.01']

    # add subheader item binary features
    df_features = add_subheader_item_features(df_ret=df_features, item_features=item_features)

    # add self engineered features
    df_features = add_self_engineered_features(df_ret=df_features)

    # drop unused features for prediction step
    df_features = df_features.drop(['symbol','date','accepted_time','text'], axis=1)

    # prediction step
    y_pred = df_features.apply(lambda x: classifier(x), axis=1)

    # positive label predictions
    df_pred_pos = df_form_8K_agg.loc[np.where(y_pred==1)[0],]
    df_pred_pos = pd.concat([df_pred_pos, df_features.loc[np.where(y_pred==1)[0],]], axis=1)

    # process positive label predictions where date >= min_date
    output_columns = ['symbol','accepted_time','keywords_loi','keywords_business_combination_agreement',
    'keywords_consummation','keywords_extension','item 2.03','%vote_against',r'%redeemed']
    df_pred_pos = df_pred_pos[df_pred_pos['date'] >= min_date][output_columns]
    df_pred_pos.reset_index(drop=True, inplace=True)
    df_pred_pos.rename(columns={'keywords_business_combination_agreement':'keywords_bca'}, inplace=True)
    df_pred_pos['%vote_against'] = df_pred_pos['%vote_against'].apply(lambda x: x if np.isnan(x) else '{:.2%}'.format(x))
    df_pred_pos[r'%redeemed'] = df_pred_pos[r'%redeemed'].apply(lambda x: x if np.isnan(x) else '{:.2%}'.format(x))

    # scrape global newswire rss feed for articles containing spac tickers
    df_gnn = scrape_gnn(spac_list_current)

    # print positive label predictions and send email
    print('\nbuy warrants for these symbols:')
    if len(df_pred_pos)==0:
        print('none\n')
    else:
        # output dataframe of warrants to buy
        print(df_pred_pos)

        # send email
        send_email(df_new_8Ks, df_pred_pos, df_gnn)

def lambda_handler(event, context):
    """AWS Lambda requires a lambda_handler function."""
    main()
    message = 'Finished running. Now go make some $$$'
    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }

if __name__ == "__main__":
    main()