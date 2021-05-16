"""
    Description:
        Helper functions for running live model
"""


from datetime import datetime as dt, timedelta
import numpy as np
import pandas as pd
from spac_web_processing import get_current_spacs, process_current_spacs, get_forms_text, basic_text_match
from spac_machine_learning import FEATURES_ITEMS, remove_header_footer, add_subheader_item_features, add_self_engineered_features
import time


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
        time.sleep(.2) # edgar allows no more than 10 requests per second
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
    df_form_8K_agg.drop(columns=['letter_of_intent_found', 'business_combination_agreement_found', 'form'], inplace=True)
    df_form_8K_agg.dropna(inplace=True)
    print('count 8-Ks after dropping nans:', len(df_form_8K_agg))
    df_form_8K_agg.sort_values(by='accepted_time', inplace=True)
    df_form_8K_agg.reset_index(inplace=True, drop=True)
    
    return df_form_8K_agg


def classifier(x):
    """Rule based model to classify 8-K as 1 (buy warrant) or 0 (do nothing)."""
    if ~np.isnan(x['%vote_against']) and (x['%vote_against'] > .10):
        return 0
    elif x['keywords_ipo'] > 0:
        return 0
    else:
        if (x['keywords_loi'] > 0) and (x['item 2.03'] == 0):
            return 1
        elif (x['keywords_business_combination_agreement'] > 0) and (x['item 2.03'] == 0):
            return 1
        elif (x['keywords_consummation'] > 0) and (x['item 2.03'] == 0):
            return 1
        elif (x['keywords_extension'] > 0) and (x['item 2.03'] == 0):
            return 1
        elif (x['keywords_trust'] > 0) and (x['item 2.03'] == 0):
            return 1
        else:
            return 0


def run_live_model(spac_list_current):
    # process current spac list
    spac_list_current = process_current_spacs(spac_list=spac_list_current)

    # get returns following 8-Ks for current spacs
    df_form_8K_agg = agg_form_8K(spac_list=spac_list_current, write=False)

    # get 8-Ks added yesterday or today
    min_date = (dt.today()-timedelta(days=2)).strftime('%Y-%m-%d')
    df_new_8Ks = df_form_8K_agg[df_form_8K_agg.date>=min_date][['symbol','accepted_time']].reset_index(drop=True)
    df_new_8Ks.rename(columns={'accepted_time':'filing_time'}, inplace=True)

    # features dataframe
    df_features = df_form_8K_agg.copy()

    # remove header and footer
    df_features['text'] = df_features.text.apply(lambda x: remove_header_footer(x))

    # add subheader item binary features
    df_features = add_subheader_item_features(df_ret=df_features, item_features=FEATURES_ITEMS)

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
    				  'keywords_consummation','keywords_extension','keywords_trust','item 2.03','%vote_against',r'%redeemed']
    df_pred_pos = df_pred_pos[df_pred_pos['date'] >= min_date][output_columns]
    df_pred_pos.reset_index(drop=True, inplace=True)
    df_pred_pos.rename(columns={'keywords_business_combination_agreement':'keywords_bca', 'accepted_time':'filing_time'}, inplace=True)
    df_pred_pos['%vote_against'] = df_pred_pos['%vote_against'].apply(lambda x: None if np.isnan(x) else '{:.2%}'.format(x))
    df_pred_pos[r'%redeemed'] = df_pred_pos[r'%redeemed'].apply(lambda x: None if np.isnan(x) else '{:.2%}'.format(x))

    return df_new_8Ks, df_pred_pos
