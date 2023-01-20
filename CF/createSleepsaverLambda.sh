aws s3 sync . s3://evg-sleepsaver-cf --region eu-west-2
aws s3 cp ../sleepsaverlambda.zip s3://evg-sleepsaver-cf/

aws cloudformation deploy --stack-name SleepSaverLambdav2 --template-file ./sleepsaverlambda.yml --region eu-west-2 --capabilities CAPABILITY_NAMED_IAM

