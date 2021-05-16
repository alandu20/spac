"""
    Description:
        Helper functions for web scraper processing
"""


from datetime import datetime as dt
from datetime import timedelta
from edgar import Company
import json
from lxml import html
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import requests
import sec_scraper
import time
pd.options.display.max_rows = 100
pd.options.display.max_columns = 100
pd.options.display.max_colwidth = 100


def get_current_spacs(file_path_current, write=False):
    """Update list of current spac tickers."""
    # existing current spac list
    df_spacs_existing = pd.read_csv(file_path_current)
    df_spacs_existing.drop_duplicates(inplace=True)
    
    # "spac traq" spac list (deprecated)
    # df_traq = pd.read_csv('https://docs.google.com/spreadsheets/d/14BY8snyHMbUReQVRgZxv4U4l1ak79dWFIymhrLbQpSo/'
    #                       'export?gid=0&format=csv', header=2)
    # df_traq.columns = [x.replace('\n','') for x in df_traq.columns]
    # spac_traq_symbols = df_traq['Issuer Symbol']
    
    # "spac track" spac list
    path_spactrack = 'https://sheet2site.com/api/v3/index.php?key=1F7gLiGZP_F4tZgQXgEhsHMqlgqdSds3vO0-4hoL6ROQ&g=1&e=1&g=1'
    page = requests.get(path_spactrack)
    tree = html.fromstring(page.content)
    html_table = tree.xpath('//table[@class="table table-sm"]')
    str_table = html.etree.tostring(html_table[0])
    df_track = pd.read_html(str_table)[0]
    df_track = df_track[df_track['Status-Filter']!='Pre IPO']
    spac_track_symbols = df_track['SPAC Ticker-Filter']
    
    # combine
    combined_spacs = df_spacs_existing['Ticker'].append(spac_track_symbols)
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
    return df_spacs_new


def get_ticker_to_cik(write=False):
    # local copy: data/ticker_to_cik.txt
    ticker_to_cik = pd.read_csv('https://www.sec.gov/include/ticker.txt',
                                sep='\t', header=None, names=['ticker','cik'])
    if write:
        ticker_to_cik.to_csv('data/ticker_to_cik.csv', index=False)
    ticker_to_cik['ticker'] = ticker_to_cik.ticker.str.upper()
    ticker_to_cik['cik'] = ticker_to_cik.cik.astype(str)
    return ticker_to_cik


def get_cik_to_name(write=False):
    # local copy: data/cik_to_name.json
    cik_to_name = requests.get('https://www.sec.gov/files/company_tickers.json')
    cik_to_name = json.dumps(cik_to_name.json())
    cik_to_name = pd.read_json(cik_to_name).transpose()
    cik_to_name['ticker'] = cik_to_name['ticker'].str.upper()
    cik_to_name['cik_str'] = cik_to_name['cik_str'].astype(str)
    cik_to_name.rename(columns={'cik_str':'cik'}, inplace=True)
    return cik_to_name


def process_current_spacs(file_path_current=None, spac_list=None, write=False):
    if file_path_current is not None:
        spac_list_current = pd.read_csv(file_path_current)
        spac_list_current = spac_list_current.Ticker.unique()
        spac_list_current = pd.DataFrame(spac_list_current, columns=['Ticker'])
    else:
        assert spac_list is not None, 'Must pass in spac_list if file_path_current is None'
        spac_list_current = spac_list
    
    # write to file
    if write==True:
        spac_list_current.to_csv('spac_list_current.csv', index=False)
        
    # get ticker to cik and cik to company name file, then merge
    ticker_to_cik = get_ticker_to_cik(write=write)
    cik_to_name = get_cik_to_name(write=write)
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
    print('count nan in current spacs:', len(spac_list_current[spac_list_current.ticker.isna()]))
    
    return spac_list_current


def process_past_spacs(file_path_past, write=False):
    # past spac list (completed business combination)
    spac_list_past = pd.read_csv(file_path_past)
    spac_list_past.fillna('missing', inplace=True)
    spac_list_past['dupe_filter'] = spac_list_past['Old Ticker'] + spac_list_past['New Ticker']
    spac_list_past = spac_list_past[spac_list_past.dupe_filter.isin(spac_list_past.dupe_filter.unique())]
    spac_list_past.drop(columns=['dupe_filter'], inplace=True)
    
    # write to file
    if write==True:
        spac_list_past.to_csv('spac_list_past.csv', index=False)
        
    # get ticker to cik and cik to company name file, then merge
    ticker_to_cik = get_ticker_to_cik(write=write)
    cik_to_name = get_cik_to_name(write=write)
    spac_list_past = spac_list_past.merge(ticker_to_cik, how='left', left_on='New Ticker', right_on='ticker')
    spac_list_past = spac_list_past.merge(ticker_to_cik, how='left', left_on='Old Ticker', right_on='ticker')
    spac_list_past.rename(columns={'ticker_x':'ticker','cik_x':'cik','cik_y':'cik_old'}, inplace=True)
    spac_list_past.drop(columns='ticker_y', inplace=True)
    spac_list_past = spac_list_past.merge(cik_to_name[['cik','ticker','title']], how='left', on=['cik','ticker'])

    print('count past spacs:', len(spac_list_past))
    print('count nan in past spacs:', len(spac_list_past[spac_list_past.ticker.isna()]))
    
    return spac_list_past


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
        filings = c.get_all_filings(filing_type=form_type, no_of_documents=2)
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


def agg_spac_returns(spac_list, price_source, is_warrant=False, write=False, conservative_est=False):
    df_returns_agg = pd.DataFrame()
    count_missing_8K = 0
    for ind in range(0, len(spac_list)):
        row = spac_list.iloc[ind]
        print('index:', ind)
        print(row.ticker)
        
        broken_current_spacs = ['GNRS','KBLM','LGC','LIVE','NOVS']
        if is_warrant:
            broken_current_spacs = [x + 'W' for x in broken_current_spacs]
        if row.ticker in broken_current_spacs:
            print('in broken spac list, skipping...')
            continue

        # get form 8Ks
        df_form_8K = get_forms_text(company_name=row.title, cik_id=row.cik, form_type='8-K')
        if df_form_8K is None or len(df_form_8K)==0:
            print('no 8Ks found, trying cik_old...')
            if 'cik_old' in row.index:
                df_form_8K = get_forms_text(company_name=row.title, cik_id=row.cik_old, form_type='8-K')
        if df_form_8K is None or len(df_form_8K)==0:
            print('no 8Ks found, skipping...\n')
            count_missing_8K = count_missing_8K + 1
            continue
        else:
            if write:
                df_form_8K.to_csv('data/sec_filings_df/'+row.ticker+'_sec_forms.csv', index=False)
            # simple classifier
            df_form_8K = basic_text_match(df_form_8K, 'letter of intent')
            df_form_8K = basic_text_match(df_form_8K, 'business combination agreement')

        # get stock or warrant prices
        try:
            # load saved data
            df_prices = pd.read_csv('data/prices_'+price_source+'/daily_data/'+row.ticker+'_prices.csv') 
            print('price data min date:', df_prices.date.min())
            print('price data max date:', df_prices.date.max())
        except:
            df_prices = get_historical_prices(symbol=row.ticker,
                                              start_date='2018-01-01',
                                              end_date=dt.today().strftime('%Y-%m-%d'),
                                              price_source=price_source,
                                              is_warrant=is_warrant)
        if df_prices is None:
            print('prices for', row.ticker, 'not found. skipping...\n')
            continue
        df_prices = process_historical_prices(df_prices, conservative_est)
        
        # add completion (de-spac) date price if past spac
        if 'Completion Date' in spac_list.columns:
            if is_warrant:
                ticker_match = row.ticker[:-1]
            else:
                ticker_match = row.ticker
            if len(spac_list[spac_list['New Ticker']==ticker_match])!=0:
                completion_date = spac_list[spac_list['New Ticker']==ticker_match]['Completion Date'].iloc[0]
            elif len(spac_list[spac_list['Old Ticker']==ticker_match])!=0:
                completion_date = spac_list[spac_list['Old Ticker']==ticker_match]['Completion Date'].iloc[0]
            else:
                completion_date = np.nan
                print('could not find completion (de-spac) date')
            print('completion (de-spac) date:', completion_date)
            completion_row = df_prices[df_prices['date']==completion_date]
            if len(completion_row)==0 or pd.isna(completion_date):
                df_prices['open_completion_%chg'] = np.nan
                print('could not find price for completion (de-spac) date')
            else:
                completion_price = completion_row['close'].iloc[0]
                df_prices['completion_price'] = completion_price
                print('completion (de-spac) price:', completion_price)
                # for conservative estimate, mark return from open_t+1
                if conservative_est:
                    df_prices['open_completion_%chg'] = (df_prices['completion_price'] - df_prices['open_t+1']) / df_prices['open_t+1']
                # if not conservative estimate, mark return from open_t
                else:
                    df_prices['open_completion_%chg'] = (df_prices['completion_price'] - df_prices['open']) / df_prices['open']  
                # set to nan if date >= completion_date
                df_prices['open_completion_%chg'] = np.where(df_prices['date']>=completion_date, np.nan, np.round(df_prices['open_completion_%chg'], 2))
        else:
            df_prices['open_completion_%chg'] = np.nan

        # merge sec forms and price data on date
        cols = ['date']
        cols_pct_chg = [col for col in df_prices.columns if '%chg' in col]
        cols.extend(cols_pct_chg)
        df_returns = df_form_8K.merge(df_prices[cols], how='left', on='date') # some dates missing
        display(df_returns)

        # append
        if len(df_returns)!=0:
            df_returns['symbol'] = row.ticker
        df_returns_agg = df_returns_agg.append(df_returns)
        
        # sec site sometimes will timeout
        if ind%10==0 and ind!=0:
            time.sleep(30) # set to at least 120 loading sec forms from scratch
        
    # drop duplicates on date + symbol
    # todo: if date has multipled 8-Ks, concatenate instead of dropping
    print('count sec forms before dropping duplicates:', len(df_returns_agg))
    df_returns_agg = df_returns_agg.drop_duplicates(subset=['date','symbol'])
    print('count sec forms after dropping duplicates:', len(df_returns_agg))
    
    print('\n##############\ncount symbols missing 8-Ks:', count_missing_8K, '\n##############\n')
    
    return df_returns_agg


def load_all_spacs(use_saved_df=True, write=False, warrants_only=False, conservative_est=False):
    if conservative_est:
        path_returns = 'data/returns/conservative/'
    else:
        path_returns = 'data/returns/'
    if use_saved_df:
        df_returns_past_warrants_newticker = pd.read_csv(path_returns+'df_returns_past_warrants_newticker.csv')
        df_returns_past_warrants_oldticker = pd.read_csv(path_returns+'df_returns_past_warrants_oldticker.csv')
        df_returns_current_warrants = pd.read_csv(path_returns+'df_returns_current_warrants.csv')
        if warrants_only:
            return df_returns_past_warrants_newticker, df_returns_past_warrants_oldticker, df_returns_current_warrants
        df_returns_past = pd.read_csv(path_returns+'df_returns_past.csv')
        df_returns_current = pd.read_csv(path_returns+'df_returns_current.csv')
        return df_returns_past, df_returns_current, df_returns_past_warrants_newticker, df_returns_current_warrants
    else:
        # get returns following 8-Ks for past spac warrants (new and old tickers)
        spac_list_past_warrants_newticker = spac_list_past.copy()
        spac_list_past_warrants_newticker['ticker'] = spac_list_past_warrants_newticker['New Ticker'] + 'W' # warrants
        df_returns_past_warrants_newticker = agg_spac_returns(spac_list_past_warrants_newticker,
                                                              price_source='td',
                                                              is_warrant=True,
                                                              write=write,
                                                              conservative_est=conservative_est)
        spac_list_past_warrants_oldticker = spac_list_past.copy()
        spac_list_past_warrants_oldticker['ticker'] = spac_list_past_warrants_oldticker['Old Ticker'] + 'W' # warrants
        df_returns_past_warrants_oldticker = agg_spac_returns(spac_list_past_warrants_oldticker,
                                                              price_source='td',
                                                              is_warrant=True,
                                                              write=write,
                                                              conservative_est=conservative_est)

        # get returns following 8-Ks for current spac warrants
        spac_list_current_warrants = spac_list_current.copy()
        spac_list_current_warrants['ticker'] = spac_list_current_warrants.Ticker + 'W' # warrants
        df_returns_current_warrants = agg_spac_returns(spac_list_current_warrants,
                                                       price_source='td',
                                                       is_warrant=True,
                                                       write=write,
                                                       conservative_est=conservative_est)
        if warrants_only:
            return df_returns_past_warrants_newticker, df_returns_past_warrants_oldticker, df_returns_current_warrants
        
        # get returns following 8-Ks for past spacs
        df_returns_past = agg_spac_returns(spac_list_past,
                                           price_source='td',
                                           is_warrant=False,
                                           write=write,
                                           conservative_est=conservative_est)

        # get returns following 8-Ks for current spacs
        df_returns_current = agg_spac_returns(spac_list_current,
                                              price_source='td',
                                              is_warrant=False,
                                              write=write,
                                              conservative_est=conservative_est)

        if write:
            df_returns_past.to_csv(path_returns+'df_returns_past.csv', index=False)
            df_returns_current.to_csv(path_returns+'df_returns_current.csv', index=False)
            df_returns_past_warrants_newticker.to_csv(path_returns+'df_returns_past_warrants_newticker.csv', index=False)
            df_returns_past_warrants_oldticker.to_csv(path_returns+'df_returns_past_warrants_oldticker.csv', index=False)
            df_returns_current_warrants.to_csv(path_returns+'df_returns_current_warrants.csv', index=False)
            
    return df_returns_past, df_returns_current, df_returns_past_warrants_newticker, df_returns_past_warrants_oldticker, df_returns_current_warrants


def get_spac_track_table(path_spactrack):
    page = requests.get(path_spactrack)
    tree = html.fromstring(page.content)
    html_table = tree.xpath('//table[@class="table table-sm"]')
    str_table = html.etree.tostring(html_table[0])
    df_track = pd.read_html(str_table)[0]
    return df_track

