"""
	Description:
		Dashboard for SPAC warrant strategy using streamlit.io
	Usage:
		streamlit run spac_app.py
"""


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from spac_historical_stats import plot_cumulative_return, compute_mean_returns, compute_summary_statistics
from spac_machine_learning import (process_warrant_features, split_warrant_train_test, logistic_reg_train, decision_tree_train,
	random_forest_train, svm_train, binary_classification_report, plot_feature_importance, trading_metrics)
from spac_run_live import run_live_model
from spac_web_processing import process_current_spacs, process_past_spacs, load_all_spacs, get_current_spacs


st.title('SPAC Strategy Dashboard')

option_side = st.sidebar.selectbox('Dashboard Type', ['Production Model', 'Historical Returns', 'Machine Learning Models'])

if option_side == 'Production Model':
	expander_live = st.beta_expander('About the model')
	expander_live.write('- Scrapes spactrack.net for all current SPACs')
	expander_live.write('- Scrapes and parses Form 8-K texts from SEC Edgar filings site for all current SPACs')
	expander_live.write('- Applies custom feature engineering function for text classification. For intuition on features, see https://github.com/alandu20/spac/tree/master/notes')
	expander_live.write('- Predicts which SPAC warrants to buy using a modified version of decision tree classifier in machine learning models section')
	expander_live.write('- Runs separately every half hour on AWS Lambda instance and sends buy alerts via email')
	button_live = st.button('Run model')
	if button_live:
		spac_list_current = get_current_spacs(file_path_current='data/spac_list_current.csv')
		st.write('Processing {:.0f} SPACs...'.format(len(spac_list_current)))
		df_new_forms, df_buy = run_live_model(spac_list_current=spac_list_current)
		st.write('New Form 8-Ks filed since {}:'.format(df_new_forms.filing_time.min()[0:10]))
		if len(df_new_forms) == 0:
			st.write('No new 8-Ks')
		else:
			st.write(df_new_forms)
		st.write('Buy warrants for these symbols:')
		if len(df_buy) == 0:
			st.write('No warrants to buy')
		else:
			st.write(df_buy)
else:
	# Load saved returns with returns calculated from open on form filing date + 1 day (conservative)
	df_returns_past, df_returns_current, df_returns_past_warrants_newticker, df_returns_current_warrants = load_all_spacs(use_saved_df=True, conservative_est=True)
	df_returns_all_warrants = df_returns_past_warrants_newticker.append(df_returns_current_warrants)
	df_returns_all_warrants = df_returns_all_warrants.replace([np.inf, -np.inf], np.nan)
	df_returns_all_stock = df_returns_past.append(df_returns_current)

	if option_side == 'Historical Returns':
		st.header('Warrant vs Stock Historical Returns')
		expander_ret = st.beta_expander('Definitions')
		expander_ret.write('- open\_close_t+{n}\_%chg is the return if we buy at opening price on the day the Form 8-K is released and sell at closing price n days later.')
		expander_ret.write('- open\_completion\_%chg is the return if we buy at opening price on the day the Form 8-K is released and sell at ticker change (de-spac).')
		expander_ret.write('- See https://www.sec.gov/files/form8-k.pdf for more information on Form 8-K. Price data pulled using TD Ameritrade API.')

		# Warrant cumulative return plots
		fig_cumsum_warrant = plot_cumulative_return(df_returns_all_warrants, symbolType='Warrant')
		st.plotly_chart(fig_cumsum_warrant, use_container_width=True)

		# Warrant stats
		expander_warrant = st.beta_expander('Show stats per warrant')
		expander_warrant.write(compute_mean_returns(df_returns_all_warrants, corrupt_symbols=['LAZYW']))
		expander_warrant.write(compute_summary_statistics(df_returns_all_warrants, corrupt_symbols=['LAZYW']))

		# Stock cumulative return plots
		fig_cumsum_stock = plot_cumulative_return(df_returns_all_stock, symbolType='Stock')
		st.plotly_chart(fig_cumsum_stock, use_container_width=True)

		# Stock stats
		expander_stock = st.beta_expander('Show stats per stock')
		expander_stock.write(compute_mean_returns(df_returns_all_stock, corrupt_symbols=['ACEL']))
		expander_stock.write(compute_summary_statistics(df_returns_all_stock, corrupt_symbols=['ACEL']))

	if option_side == 'Machine Learning Models':
		st.header('Predicting Warrant Returns Using Text from SEC Filings')
		expander_ml = st.beta_expander('FAQ')
		expander_ml.write('- What are we predicting? Whether the warrant return after n days is negative (label=0) or positive (label=1).')
		expander_ml.write('- Why not regression models? Binary classification results are more promising.')
		expander_ml.write('- What about multi-class classification? See https://github.com/alandu20/spac/blob/master/prototype.ipynb.')
		ml_algos = ['Logistic Regression', 'Decision Tree', 'Support Vector Machine', 'Random Forest']
		option_ml = st.selectbox('Select machine learning model:', ml_algos)
		y_variables = ['open_close_t+1_%chg', 'open_close_t+3_%chg', 'open_close_t+5_%chg', 'open_close_t+7_%chg',
					   'open_close_t+10_%chg', 'open_close_t+12_%chg']
		option_y = st.selectbox('Select output variable:', y_variables)
		pressed_ml = st.button('Train model')
		if pressed_ml:
			df_returns = process_warrant_features(df_returns_warrants=df_returns_all_warrants, y_variable=option_y)
			X, X_train, X_test, y, y_train, y_test = split_warrant_train_test(df_returns_warrants=df_returns, y_variable=option_y)
			
			st.subheader('Training set')
			if option_ml == 'Logistic Regression':
				cv_grid_result, fig_reg_path, model = logistic_reg_train(X_train, y_train)
			elif option_ml == 'Decision Tree':
				cv_grid_result, fig_reg_path, model = decision_tree_train(X_train, y_train)
			elif option_ml == 'Support Vector Machine':
				cv_grid_result, fig_reg_path, model = svm_train(X_train, y_train)
			elif option_ml == 'Random Forest':
				cv_grid_result, model = random_forest_train(X_train, y_train)
			else:
				assert option_ml in ml_algos
			st.write('Best 5-fold CV (TimeSeriesSplit) score: {:.2f} using {}'.format(cv_grid_result.best_score_, cv_grid_result.best_params_))
			if option_ml is not 'Random Forest':
				st.pyplot(fig_reg_path, use_container_width=True)
			y_train_pred = model.predict(X_train)
			cm, cr, fig_eval_curves = binary_classification_report(model, X_train, y_train, y_train_pred)
			st.write('Confusion matrix:\n', cm)
			st.write(cr)
			st.pyplot(fig_eval_curves, use_container_width=True)

			st.subheader('Test set')
			y_test_pred = model.predict(X_test)
			cm, cr, fig_eval_curves = binary_classification_report(model, X_test, y_test, y_test_pred)
			st.write('Confusion matrix:\n', cm)
			st.write(cr)
			st.pyplot(fig_eval_curves, use_container_width=True)

			st.subheader('Feature importance')
			st.pyplot(plot_feature_importance(model, X), use_container_width=True)

			st.subheader('Trading metrics')
			y_all_pred = model.predict(X)
			trades_per_month, sum_returns, mean_return, sd_return, sd_return_dn, sharpe_ratio, sortino_ratio = trading_metrics(df_returns, option_y, y_all_pred)
			st.write('Trades / month: {:.1f}'.format(trades_per_month))
			st.write('Sum return: {:.0f}%'.format(sum_returns*100))
			st.write('Mean return: {:.0f}%'.format(mean_return*100))
			st.write('Std dev: {:.0f}%'.format(sd_return*100))
			st.write('Downside std dev: {:.0f}%'.format(sd_return_dn*100))
			st.write('Sharpe ratio: {:.2f}'.format(sharpe_ratio))
			st.write('Sortino ratio: {:.2f}'.format(sortino_ratio))
