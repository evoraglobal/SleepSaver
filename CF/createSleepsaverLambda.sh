# Set the location of the Code Bucket in S3. This needs to be set in SleepSaverLambda.yml as the CodeBucket Parameter
export CODEBUCKET=evg-sleepsaver-cf

aws s3 sync . s3://$CODEBUCKET --region eu-west-2
aws s3 cp ../sleepsaverlambda.zip s3://evg-sleepsaver-cf/
aws cloudformation deploy --stack-name SleepSaverLambdav2 --template-file ./sleepsaverlambda.yml --region eu-west-2 --capabilities CAPABILITY_NAMED_IAM


