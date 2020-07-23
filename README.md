SPAC strategy

AWS Lambda:
1. Install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
2. (First time) Create new admin IAM user group https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html. Username: Administrator, PW: p***7. Then create access keys for IAM user https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds. Access key ID and Secret Access key found in Administrator_accessKeys.csv (saved locally)
3. Create a lambda function “my-function”: https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html. Change “Timeout” setting to max setting of 15 minutes
4. Save dependencies in aws_lambda/package directory (create if d.n.e.). Need to install versions compatible with AWS Linux, see https://medium.com/@korniichuk/lambda-with-pandas-fd81aa2ff25e. Download the version named *manylinux1_x86_64.whl and save in aws_lambda/package.
5. Special instructions for NLTK.
- Install in aws_lambda/package: pip install --target nltk 
- Weird nltk issue (related to installing on Mac while AWS is linux), need to replace the regex package with regex-2020.7.14-cp36-cp36m-manylinux1_x86_64.whl found here: https://pypi.org/project/regex/#files. Otherwise will get error No module named 'regex._regex'
- To use stopwords corpus, download here: http://www.nltk.org/nltk_data/. Then copy into aws_lambda/nltk/nltk_data/corpora (create nltk_data/corpora if d.n.e.)
6. Create zip archive of aws_lambda/package: zip -r9 ${OLDPWD}/function.zip .
7. Add lambda_function.py to archive: zip -g function.zip lambda_function.py
8. Add aws_lambda/data/spac_list_current.csv (create if d.n.e.) to archive: zip -r function.zip data
8. Upload package to lambda function “my-function”: aws lambda update-function-code --function-name my-function --zip-file fileb://function.zip
9. View updated lambda function: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions