SPAC strategy

AWS Lambda:
1. Install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
2. (First time) Create new admin IAM user group https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html. Username: Administrator, PW: p***7. Then create access keys for IAM user https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds. Access key ID and Secret Access key found in Administrator_accessKeys.csv (saved locally). Set 
3. Create a lambda function “my-function”: https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html. Change “Timeout” setting to max setting of 15 minutes
4. Install dependencies in a new “package” directory. Need to install versions compatible with AWS Linux, see https://medium.com/@korniichuk/lambda-with-pandas-fd81aa2ff25e: pip install --target ./package nltk Weird nltk issue on AWS, need to replace the regex package with https://pypi.org/project/regex/#files regex-2020.7.14-cp36-cp36m-manylinux1_x86_64.whl, otherwise will get error No module named 'regex._regex'
5. Create zip archive of the dependencies: zip -r9 ${OLDPWD}/function.zip .
6. Add lambda_function.py to archive: zip -g function.zip lambda_function.py
7. Upload package to lambda function “my-function”: aws lambda update-function-code --function-name my-function --zip-file fileb://function.zip
8. View updated lambda function: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions
