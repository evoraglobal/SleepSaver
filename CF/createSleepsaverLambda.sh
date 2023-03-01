# Set the location of the Code Bucket in S3. This needs to be set in SleepSaverLambda.yml and the CodeBucket Parameter
export CODEBUCKET=evg-sleepsaver-cf

aws s3 cp *.yml s3://$CODEBUCKET/
aws s3 cp *.json  s3://$CODEBUCKET/
aws s3 cp ../sleepsaverlambda.zip s3://$CODEBUCKET/
aws cloudformation deploy --stack-name SleepSaverLambdav2 --template-file ./sleepsaverlambda.yml --s3-bucket $CODEBUCKET --region eu-west-2 --capabilities CAPABILITY_NAMED_IAM


