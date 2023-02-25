aws s3 cp stepsyntax.json s3://evg-sleepsaver-cf --region eu-west-2

aws cloudformation deploy --stack-name SleepSaverStepFunction --template-file ./stepfunction.yml --region eu-west-2 --capabilities CAPABILITY_NAMED_IAM
