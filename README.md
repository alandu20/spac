SPAC Warrant Strategy

<img width="1398" alt="spac_app_screenshot" src="https://user-images.githubusercontent.com/7809658/118424233-d3d07080-b694-11eb-99cf-f366059ceb06.png">

Dashboard app deployed to Streamlit share: https://share.streamlit.io/alandu20/spac/spac_app.py

Demo: https://user-images.githubusercontent.com/7809658/118423227-881cc780-b692-11eb-863c-04ab4a163866.mp4

Streamlit Dashboard Setup:
1. Install streamlit: pip install streamlit
2. Launch app: streamlit run spac_app.py

Streamlit Dashboard Usage:
1. Production Model
- Scrapes spactrack.net for all current SPACs
- Scrapes and parses Form 8-K texts from SEC Edgar filings site for all current SPACs
- Applies custom feature engineering function for text classification. For intuition on features, see notes directory
- Predicts which SPAC warrants to buy using a modified version of decision tree classifier in machine learning models section
- Runs separately every half hour on AWS Lambda instance and sends buy alerts via email
2. Historical Returns
- Cumulative return plots trading on all Form 8-Ks
- Breakdown of returns by SPAC
3. Machine Learning Models
- Train logistic regression, decision tree, SVM, or random forest classifier to predict whether warrant return after *n* days is negative or positive
- Option to change *n* in output variable
- Outputs CV regularization path, classification report, ROC curve, precision-recall curve, feature importance, and trading metrics

AWS Lambda:
1. Install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
2. (First time) Create new admin IAM user group https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html. Then create access keys for IAM user https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds. Access key ID and Secret Access key found in Administrator_accessKeys.csv (saved locally)
3. Create a lambda function “my-function”: https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html. Change “Timeout” setting to max setting of 15 minutes
4. Save dependencies in aws_lambda/package directory (create if d.n.e.). Need to install versions compatible with AWS Linux, see https://medium.com/@korniichuk/lambda-with-pandas-fd81aa2ff25e. Download the version named *manylinux1_x86_64.whl and save in aws_lambda/package. If there is not a linux-specific distribution (e.g. https://pypi.org/project/feedparser/#files), then just pip install into aws_lambda/package (e.g. pip install -t . feedparser). Can delete the dist-info directory for either installation approach
5. Special instructions for NLTK.
- Install in aws_lambda/package: pip install --target nltk
- Weird nltk issue (related to installing on Mac while AWS is linux), need to replace the regex package with regex-2020.7.14-cp36-cp36m-manylinux1_x86_64.whl found here: https://pypi.org/project/regex/#files. Otherwise will get error No module named 'regex._regex'
- To use stopwords corpus, download here: http://www.nltk.org/nltk_data/. Copy into aws_lambda/nltk/nltk_data/corpora (create nltk_data/corpora if d.n.e.). Then add path to python script: nltk.data.path.append('nltk/nltk_data')
6. cd into aws_lambda/package and create zip archive: zip -r9 ${OLDPWD}/function.zip .
7. cd into aws_lambda and add lambda_function.py (this is the script that's run by lambda) to archive: zip -g function.zip lambda_function.py
8. Add aws_lambda/data/spac_list_current.csv (create if d.n.e.) to archive: zip -r function.zip data. Note that you cannot save persistent data in lambda (would need S3 to do so). Need to manually copy+paste updated spac_list_current.csv into aws_lambda/data
8. Upload package to lambda function “my-function”: aws lambda update-function-code --function-name my-function --zip-file fileb://function.zip
9. View updated lambda function: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions
10. To cron, add new trigger -> EventBridge (CloudWatch Events) -> schedule expression. CloudWatch cron rules here: https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html

AWS SES:
1. Obtain SES SMTP credentials: https://docs.aws.amazon.com/ses/latest/DeveloperGuide/smtp-credentials.html
2. Verify email address: https://docs.aws.amazon.com/ses/latest/DeveloperGuide/verify-email-addresses-procedure.html
3. Send email using SES interface: https://docs.aws.amazon.com/ses/latest/DeveloperGuide/examples-send-using-smtp.html

TD API (used to download historical daily and minute prices):
1. Create app here: https://developer.tdameritrade.com/user/me/apps. CONSUMER_KEY found here
2. Authentication (need to do this every 90 days):
- Start localhost server: sudo apachectl start
- Follow https://developer.tdameritrade.com/content/simple-auth-local-apps. Step 4 client_id should be CONSUMER_KEY@AMER.OAUTHAP and redirect_uri should be http://localhost/. Refresh token can be used to use API without server

Current SPAC data sources:
1. https://docs.google.com/spreadsheets/d/14BY8snyHMbUReQVRgZxv4U4l1ak79dWFIymhrLbQpSo/edit#gid=0. Seems like this is no longer updated
2. https://docs.google.com/spreadsheets/d/1LQLUy21Y14CcYyuYgKJcf9OQ4QWCs_w6PX-jDqhcejQ/edit#gid=0. This one has export options disabled
3. https://spactrack.net/ (https://sheet2site.com/api/v3/index.php?key=1F7gLiGZP_F4tZgQXgEhsHMqlgqdSds3vO0-4hoL6ROQ&g=1&e=1&g=1)

Interactive Brokers:
1. Unzip interactive_brokers/clientportal.gw.zip
2. In interactive_brokers/clientportal.gw directory start client portal login java app: bin/run.sh root/conf.yaml
3. Open https://localhost:5000 and enter login info
4. API: https://www.interactivebrokers.com/api/doc.html, https://interactivebrokers.github.io/cpwebapi/, https://github.com/areed1192/interactive-broker-python-api

Known data issues:
1. Some TD price data missing, e.g. data/prices_td/daily_data/ACAMW.csv skips from 2019-06-19 to 2019-07-02 (perhaps due to no volume between those days but unlikely)
2. Some TD price data just straight up wrong, e.g. data/prices_td/daily_data/HOFV.csv 2020-06-15 close price is 7.88, but according to Yahoo and Google Finance close price was above 10, which makes sense since GPAQ->HOFV on 2020-07-01. Could be an issue with how TD migrated prices for completed spacs following ticker change.
