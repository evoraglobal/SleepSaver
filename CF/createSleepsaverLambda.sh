# Set the location of the Code Bucket in S3. This needs to be set in SleepSaverLambda.yml and the CodeBucket Parameter
# Or just rune the single Line install shell instead - if you are running on your own account and you want to use the publised binaries.
export CODEBUCKET=evg-sleepsaver-cf

aws s3 cp *.yml s3://$CODEBUCKET/
aws s3 cp *.json  s3://$CODEBUCKET/
aws s3 cp singleLineInstall.sh s3://$CODEBUCKET/
aws s3 cp ../sleepsaverlambda.zip s3://$CODEBUCKET/
# change the cron times in the --parameter override to signal start and end times of the day
aws cloudformation deploy --stack-name SleepSaverLambdav2 --template-file ./sleepsaverlambda.yml --region eu-west-2 --capabilities CAPABILITY_NAMED_IAM  --parameter-overrides "DayScheduleExpression=cron(29 1 ? * 2-6 *)" "NightScheduleExpression=cron(45 18 * * ? *)"


