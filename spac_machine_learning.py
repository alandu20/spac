"""
    Description:
        Helper functions for machine learning algos for predicting warrant returns based on SEC form text
"""


import collections
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
from sklearn import metrics
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import ElasticNet, LinearRegression, LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, GridSearchCV, TimeSeriesSplit, train_test_split
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.svm import SVC


# define item features
# item definitions: https://www.sec.gov/fast-answers/answersform8khtm.html
# item faq: https://media2.mofo.com/documents/faq-form-8-k.pdf
FEATURES_ITEMS = ['item 1.01','item 1.02','item 1.03','item 1.04','item 2.01','item 2.02','item 2.03','item 2.04',
                  'item 2.05','item 2.06','item 3.01','item 3.02','item 3.03','item 4.01','item 4.02','item 5.01',
                  'item 5.02','item 5.03','item 5.04','item 5.05','item 5.06','item 5.07','item 5.08','item 6.01',
                  'item 6.02','item 6.03','item 6.04','item 6.05','item 7.01','item 8.01']


def remove_header_footer(text):
    """Remove standard header and footer from 8-K and clean text further."""
    # remove/replace some unicode characters
    text = text.replace('\t','') # remove tabs
    text = text.replace('\x93','"') # 1st quotation mark type
    text = text.replace('\x94','"') # 2nd quotation mark type
    text = text.replace('”', '"') # weird unicode/ascii conversion issue (1st quotation mark type)
    text = text.replace('“', '"') # weird unicode/ascii conversion issue (2nd quotation mark type)
    
    # remove forward looking statement section
    FLS_START = [
    'forward-looking statements this current report',
    'forward looking statements certain statements',
    'forward-looking statements this report',
    'forward-looking statements the company makes',
    'forward-looking statements certain of the matters',
    'forward-looking statements this communication',
    'forward-looking statements this document'
    ]
    FLS_END = [
    'undue reliance should not be placed upon the forward-looking statements',
    'whether as a result of new information, future events or otherwise, except as required by law',
    'conditions or circumstances on which any such statement is based, except as required by applicable law',
    'whether as a result of new information, future events, or otherwise'
    ]
    for forward_start in FLS_START:
        for forward_end in FLS_END:
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
    
    # drop these items
    drop_item_list = ['item 9.01']
    
    if subheaders_only:
        return [x for x in subheaders if x not in drop_item_list]
    return subtexts


def count_keywords(x, keywords):
    count = 0
    for keyword in keywords:
        count = count + x.count(keyword)
    return count


def text_processing(text, item_features, stemming=True):
    subtexts = get_item_subheaders(text, subheaders_only=False)
    tokens = []
    for subtext in subtexts:
        # remove item subheaders. todo: probably should remove text of subheader too
        for item in item_features:
            subtext = subtext.replace(item,'')

        # tokenize, only keeping alphanumeric
        subtokens = nltk.tokenize.RegexpTokenizer(r'\w+').tokenize(subtext)

        # remove stop words
        stop_words = set(nltk.corpus.stopwords.words('english'))
        subtokens = [w for w in subtokens if not w in stop_words]

        # remove numbers and chinese/other non-english characters for now
        # (todo: revisit later for vote count processing)
        subtokens = [w for w in subtokens if w.encode('utf-8').isalpha()]

        # stemming
        if stemming:
            stems = [nltk.stem.porter.PorterStemmer().stem(w) for w in subtokens]
            tokens.extend(stems)
        else:
            tokens.extend(subtokens)

    processed_text = ' '.join(tokens)
    return processed_text


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


def add_bagofwords_features(df_ret, vectorizer_type, response_variable):
    # process text and create bigram, trigram features
    corpus = []
    for text in df_ret['text']:
        corpus.append(text_processing(text))
    print('vectorizer:', vectorizer_type, '\n')
    if vectorizer_type=='CountVectorizer':
        vectorizer = CountVectorizer(analyzer='word', ngram_range=(2, 3)) # Total Frequency
    elif vectorizer_type=='TfidfVectorizer':
        vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(2, 3)) # TF-IDF
    else:
        print('vectorizer_type d.n.e')
    X_corpus = vectorizer.fit_transform(corpus)
    df_bagofwords = pd.DataFrame(X_corpus.toarray())
    df_bagofwords.columns = vectorizer.get_feature_names()
    
    # concatenate
    df_ret = pd.concat([df_ret, df_bagofwords], axis=1)

    # example features
    print('letter intent features:', [x for x in df_bagofwords.columns if 'letter intent' in x])

    # histogram
    (n, bins, patches) = plt.hist(df_ret[response_variable], bins=10, label=response_variable)
    plt.title('Histogram of ' + response_variable)
    plt.show()
    print('bins', np.round(bins,2))
    print('counts', n)
    
    return df_ret


def convert_vote_count_to_int(x):
    if '—' in x or '-' in x or 'n/a' in x:
        return 0
    try:
        x = int(x.replace(',',''))
    except:
        return np.nan
    return x


# does not handle: https://www.sec.gov/Archives/edgar/data/1704760/000161577419006723/s117785_8k.htm (no broker non-votes)
def parse_vote_results(x):
    # find strings in text. use first if multiple matches
    VOTE_HEADER = [
        'for against abstain broker non-votes',
        'for against abstain broker non-vote',
        'for against abstention broker non-votes',
        'for against abstention broker non-vote',
        'for against abstentions broker non-votes',
        'for against abstentions broker non-vote'
    ]
    # find phrases preceding vote results in text
    vote_strings = [vote_string for vote_string in VOTE_HEADER if vote_string in x['text']]

    # parse votes for, votes against, votes abstain, votes broker non votes
    if len(vote_strings)==0:
        return pd.Series([np.nan, np.nan, np.nan, np.nan])
    else:
        vote_string = vote_strings[0] # use first if multiple matches
        vote_index = x['text'].find(vote_string)
        vote_data = x['text'][(vote_index + len(vote_string)):].lstrip().split(' ')
        votes_for = convert_vote_count_to_int(vote_data[0])
        votes_against = convert_vote_count_to_int(vote_data[1])
        votes_abstain = convert_vote_count_to_int(vote_data[2])
        votes_broker_non_votes = convert_vote_count_to_int(vote_data[3])
        if np.isnan(votes_for) or np.isnan(votes_against) or np.isnan(votes_abstain) or np.isnan(votes_broker_non_votes):
            print('something wrong with parse_vote_results for', x.symbol, 'on', x.date)
        return pd.Series([votes_for, votes_against, votes_abstain, votes_broker_non_votes])
    return pd.Series([np.nan, np.nan, np.nan, np.nan])


def parse_redemptions(x):
    REDEMPTION_HEADER = [
        'in connection with the extension',
        'in connection with the closing',
        'in advance of the special meeting',
        'in connection with the special meeting',
        'exercised their right'
    ]
    for redemption_phrase in REDEMPTION_HEADER:
        redemption_sentence = [sentence for sentence in x.text.split('.') if
                               redemption_phrase in sentence
                               and ('redeem' in sentence or 'redemp' in sentence)]
        if len(redemption_sentence)>0:
            break
    if len(redemption_sentence)==0:
        return np.nan
    redemption_sentence = redemption_sentence[0].lstrip().replace(',','')
    redemption_sentence = re.sub(r'[\$]{1}[\d,]+\.?\d{0,2}', '', redemption_sentence) # replace $_#_
    shares_regex_strong = re.findall('[0-9]+ shares', redemption_sentence)
    shares_regex_weak = re.findall('[0-9]+', redemption_sentence)
    # case: just one number in sentence. assume this number is redemption number
    if len(shares_regex_weak)==1:
        shares = int(shares_regex_weak[0])
    # case: more than one number in sentence. if '[0-9]+ shares' then assume this is redemption number, otherwise nan
    elif len(shares_regex_weak)>1:
        if len(shares_regex_strong)==1:
            shares = int(shares_regex_strong[0].replace('shares','').replace(' ',''))
        else:
            shares = np.nan
    # case: no numbers in sentence.
    else:
        if 'none' in redemption_sentence:
            shares = 0
        else:
            shares = np.nan
    return shares


def compute_self_engineered_feature_metrics(df_ret, col_name, response_variable):
    print('count', col_name, '> 0:', np.sum(df_ret[col_name]>0),
          '; count', response_variable, '> 0:', len(df_ret[df_ret[col_name]>0][df_ret[response_variable]>0]),
          '; count unique symbols:', len(df_ret[df_ret[col_name]>0]['symbol'].unique()))


def add_self_engineered_features(df_ret, response_variable=None):
    """Add self engineered features from keyword lists."""
    # keywords lists
    keywords_list_loi = [
    'entry into a letter of intent',
    'entry into a non-binding letter of intent',
    'enter into a letter of intent',
    'enter into a non-binding letter of intent',
    'entered into a letter of intent',
    'entered into a non-binding letter of intent',
    'entering into a letter of intent',
    'entering into a non-binding letter of intent',
    'execution of a letter of intent',
    'execution of a non-binding letter of intent',
    'execute a letter of intent',
    'execute a non-binding letter of intent',
    'executed a letter of intent',
    'executed a non-binding letter of intent',
    'executing a letter of intent',
    'executing a non-binding letter of intent'
    ]
    keywords_list_business_combination_agreement = [
    '("business combination agreement")',
    '(the "business combination agreement")',
    '("business combination")',
    '(the "business combination")',
    'entry into a definitive agreement',
    'enter into a definitive agreement',
    'entered into a definitive agreement',
    'entering into a definitive agreement',
    'business combination proposal was approved'
    ]
    keywords_list_merger_agreement = ['(the "merger agreement")']
    keywords_list_purchase_agreement = ['(the "purchase agreement")']
    keywords_list_extension = [
    '(the "extension")',
    '(the "extension amendment")',
    'extended the termination date',
    'extend the date by which the company must consummate',
    'extend the date by which the company has to complete',
    '(the "extension amendment proposal")',
    '(the "extended termination date")'
    ]
    keywords_list_meeting = ['("special meeting")', '(the "meeting")']
    keywords_list_record = ['(the "record date")']
    keywords_list_consummation = [
    'announcing the consummation',
    'consummated the previously announced business combination'
    ]
    keywords_list_ipo = [
    'consummated its initial public offering ("ipo")',
    'consummated its initial public offering (the "ipo")',
    'consummated an initial public offering ("ipo")',
    'consummated an initial public offering (the "ipo")',
    'consummated the initial public offering ("ipo")',
    'consummated the initial public offering (the "ipo")',
    'completed its initial public offering ("ipo")',
    'completed its initial public offering (the "ipo")',
    'in connection with its initial public offering ("ipo") was declared effective',
    'in connection with its initial public offering (the "ipo") was declared effective',
    'consummated the ipo',
    'in connection with the closing of the ipo',
    'closing of the initial public offering (the "ipo")',
    'consummation of the ipo'
    ]
    keywords_list_trust = [
    'trust account'
    ]
    
    # keywords counts
    df_ret['keywords_loi'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_loi))
    df_ret['keywords_business_combination_agreement'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_business_combination_agreement))
    df_ret['keywords_merger_agreement'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_merger_agreement))
    df_ret['keywords_purchase_agreement'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_purchase_agreement))
    df_ret['keywords_extension'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_extension))
    df_ret['keywords_meeting'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_meeting))
    df_ret['keywords_record'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_record))
    df_ret['keywords_consummation'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_consummation))
    df_ret['keywords_ipo'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_ipo))
    df_ret['keywords_trust'] = df_ret.text.apply(lambda x: count_keywords(x, keywords_list_trust))
    
    # compute metrics
    if response_variable is not None:
        keywords_name_list = ['keywords_loi','keywords_business_combination_agreement','keywords_merger_agreement',
                              'keywords_purchase_agreement','keywords_extension','keywords_meeting','keywords_record',
                              'keywords_consummation','keywords_ipo','keywords_trust','item 5.07','item 3.01','item 2.03']
        for keywords_name in keywords_name_list:
            compute_self_engineered_feature_metrics(df_ret, keywords_name, response_variable)

    # vote results
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
    
    # shares redeemed
    df_ret['redeemed_shares'] = df_ret.apply(lambda x: parse_redemptions(x), axis=1)
    df_ret['%redeemed'] = df_ret['redeemed_shares'] / df_ret['vote_total']
    
    return df_ret


def process_warrant_features(df_returns_warrants, y_variable):
    # get all warrants and drop nan and corrupt symbols
    df_returns_warrants.drop(columns=['letter_of_intent_found','business_combination_agreement_found','form','open_completion_%chg'], inplace=True)
    df_returns_warrants.dropna(inplace=True)
    df_returns_warrants = df_returns_warrants[~df_returns_warrants.symbol.isin(['ACELW','LAZYW'])]
    df_returns_warrants.sort_values(by='accepted_time', inplace=True) # need to sort for TimeSeriesSplit
    df_returns_warrants.reset_index(inplace=True, drop=True)

    # remove header and footer
    df_returns_warrants['text'] = df_returns_warrants.text.apply(lambda x: remove_header_footer(x))

    # add subheader item binary features
    df_returns_warrants = add_subheader_item_features(df_ret=df_returns_warrants, item_features=FEATURES_ITEMS)

    # add bag of words features
    # df_returns_warrants = add_bagofwords_features(df_ret=df_returns_warrants,
    #                                               vectorizer_type='CountVectorizer', # CountVectorizer or TfidfVectorizer
    #                                               response_variable=y_variable)

    # add self engineered features
    df_returns_warrants = add_self_engineered_features(df_ret=df_returns_warrants, response_variable=y_variable)

    return df_returns_warrants


def apply_lsa_dim_reduction(X, n_lsa):
    lsa = TruncatedSVD(n_components=n_lsa, n_iter=10, random_state=123)
    X = pd.DataFrame(lsa.fit_transform(X), columns=['lsa'+str(i) for i in range(0,n_lsa)])
    print('count feature after LSA:', len(X.columns), '\n')
    return X


def split_warrant_train_test(df_returns_warrants, y_variable):
    # inputs
    label_threshold = 0
    min_word_freq = 0
    n_lsa = None # None or int

    # split
    cols_drop = ['symbol','date','accepted_time','text','url','votes_for','votes_against',
                 'votes_abstain','votes_broker_non_votes','vote_total','%votes_for',
                 '%votes_abstain','%votes_broker_non_votes','redeemed_shares']
    cols_drop.extend([col for col in df_returns_warrants.columns if '%chg' in col])
    X = df_returns_warrants.drop(cols_drop, axis=1)
    X[['%vote_against','%redeemed']] = X[['%vote_against','%redeemed']].fillna(0)
    X = X[X.columns[X.sum() >= min_word_freq].tolist()] # min word frequency
    if n_lsa is not None:
        X = apply_lsa_dim_reduction(X, n_lsa) # lsa dimension reduction
    y = np.where(df_returns_warrants[y_variable] > label_threshold, 1, 0) # label threshold
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

    return X, X_train, X_test, y, y_train, y_test


def binary_classification_report(model, X, y_actual, y_pred):
    cm = confusion_matrix(y_actual, y_pred)
    cr = classification_report(y_actual, y_pred, target_names=['0','1'], output_dict=True, digits=2)
    cr = pd.DataFrame.from_dict({key: cr[key] for key in ['0','1']}, orient='index')
    fig = plt.figure()
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)
    metrics.plot_roc_curve(model, X, y_actual, ax=ax1)
    metrics.plot_precision_recall_curve(model, X, y_actual, ax=ax2)
    return cm, cr, fig


def plot_feature_importance(model, X):
    try:
        coefs = model.coef_[0]
    except:
        coefs = model.feature_importances_
    indices = np.argsort(np.abs(coefs))[::-1]
    count_nonzero_features = len(X.columns[coefs!=0])
    if count_nonzero_features < 10:
        top_n_features = count_nonzero_features
    else:
        top_n_features = 10
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.bar(range(top_n_features), coefs[indices[:top_n_features]], align='center')
    # ax.xticks(range(top_n_features), X.columns[indices[:top_n_features]], rotation=45, ha='right')
    ax.set_xticks(range(top_n_features))
    ax.set_xticklabels(X.columns[indices[:top_n_features]], rotation = 45, ha='right')
    # ax.subplots_adjust(bottom=0.3)
    # plt.title('Feature importance')
    return fig


def logistic_reg_train(X_train, y_train):
    model_lr = LogisticRegression(penalty='l1', solver='liblinear', max_iter=1000)
    C = [.01, .1, 1, 10, 100, 1000]
    param_grid = dict(C=C)
    kfold = TimeSeriesSplit(n_splits=5) # in each split test indices must be higher than before
    grid_search = GridSearchCV(model_lr, param_grid, scoring='precision', cv=kfold, verbose=0, n_jobs=5)
    grid_result = grid_search.fit(X_train, y_train)
    reg_path = pd.DataFrame({'score': grid_result.cv_results_['mean_test_score'], 'C': C})
    reg_path['C'] = np.log10(reg_path['C'])
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    reg_path.plot(x='C', ax=ax)
    ax.xaxis.set_label_text('log10(C)')
    model = LogisticRegression(penalty='l1', solver='liblinear', C=grid_result.best_params_['C'], max_iter=1000)
    model.fit(X_train, y_train)
    return grid_result, fig, model


def decision_tree_train(X_train, y_train):
    model_dt = DecisionTreeClassifier()
    max_depth = list(range(1, 20))
    param_grid = dict(max_depth=max_depth)
    kfold = TimeSeriesSplit(n_splits=5) # in each split test indices must be higher than before
    grid_search = GridSearchCV(model_dt, param_grid, scoring='f1', cv=kfold, verbose=0, n_jobs=5)
    grid_result = grid_search.fit(X_train, y_train)
    reg_path = pd.DataFrame({'score': grid_result.cv_results_['mean_test_score'], 'max_depth': max_depth})
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    reg_path.plot(x='max_depth', ax=ax)
    model = DecisionTreeClassifier(max_depth=grid_result.best_params_['max_depth'])
    model.fit(X_train, y_train)
    return grid_result, fig, model


def random_forest_train(X_train, y_train):
    model_rf = RandomForestClassifier()
    n_estimators = list(range(1, 10))
    max_depth = list(range(1, 10))
    min_samples_leaf = [.01, .05, .1, .2]
    param_grid = dict(n_estimators=n_estimators,max_depth=max_depth,
                      min_samples_leaf=min_samples_leaf)
    kfold = TimeSeriesSplit(n_splits=5) # in each split test indices must be higher than before
    grid_search = GridSearchCV(model_rf, param_grid, scoring='f1', cv=kfold, verbose=0, n_jobs=5)
    grid_result = grid_search.fit(X_train, y_train)
    model = RandomForestClassifier(n_estimators=grid_result.best_params_['n_estimators'],
                                   max_depth=grid_result.best_params_['max_depth'],
                                   min_samples_leaf=grid_result.best_params_['min_samples_leaf'])
    model.fit(X_train, y_train)
    return grid_result, model


def svm_train(X_train, y_train):
    kernel_type = 'linear'
    model_svm = SVC(kernel=kernel_type)
    C = [.01, .1, 1, 10, 100, 1000, 10000]
    param_grid = dict(C=C)
    kfold = TimeSeriesSplit(n_splits=5) # in each split test indices must be higher than before
    grid_search = GridSearchCV(model_svm, param_grid, scoring='f1', cv=kfold, verbose=0, n_jobs=5)
    grid_result = grid_search.fit(X_train, y_train)
    reg_path = pd.DataFrame({'score': grid_result.cv_results_['mean_test_score'], 'C': C})
    reg_path['C'] = np.log10(reg_path['C'])
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    reg_path.plot(x='C', ax=ax)
    ax.xaxis.set_label_text('log10(C)')
    model = SVC(kernel=kernel_type, C=grid_result.best_params_['C'])
    model.fit(X_train, y_train)
    return grid_result, fig, model


def trading_metrics(df_returns_warrants, y_variable, y_all_pred):
    count_months = int(np.round((dt.strptime(df_returns_warrants.date.max(),'%Y-%m-%d') -
                                 dt.strptime(df_returns_warrants.date.min(),'%Y-%m-%d')).days / 365. * 12, 0))
    trades_per_month = y_all_pred.sum()/count_months
    df_pred_pos = df_returns_warrants.loc[np.where(y_all_pred==1)[0],]
    sum_returns = df_pred_pos[y_variable].sum()
    mean_return = df_pred_pos[y_variable].mean()
    sd_return = df_pred_pos[y_variable].std()
    sd_return_dn = df_pred_pos[y_variable][df_pred_pos[y_variable]<0].std()
    sharpe_ratio = mean_return / sd_return
    sortino_ratio = mean_return / sd_return_dn
    return trades_per_month, sum_returns, mean_return, sd_return, sd_return_dn, sharpe_ratio, sortino_ratio

