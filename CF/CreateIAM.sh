aws s3 sync . s3://evg-sleepsaver-cf --region eu-west-2
aws cloudformation create-stack --stack-name SleepSaverPolicies --template-url https://evg-sleepsaver-cf.s3.eu-west-2.amazonaws.com/IAMPoliciesRole.yml --region eu-west-2
