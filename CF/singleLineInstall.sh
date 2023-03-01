# start of day is define as 7.29 am, end of day is configured for 6.45pm UTC. Use --parameter-override switch to configure
aws cloudformation deploy --stack-name SleepSaverLambdav2 --template-file ./sleepsaverlambda.yml --region eu-west-2 --capabilities CAPABILITY_NAMED_IAM  --parameter-overrides "DayScheduleExpression=cron(29 7 ? * 2-6 *)" "NightScheduleExpression=cron(45 18 * * ? *)"

