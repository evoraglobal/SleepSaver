mkdir zippackage
cp *.py ./zippackage

cd zippackage
zip -r ../sleepsaverlambda.zip .
cd ..
aws s3 cp ./sleepsaverlambda.zip s3://evg-sleepsaver-cf/
aws lambda update-function-code --function-name SleepSaverProd --zip-file fileb://sleepsaverlambda.zip --region eu-west-2 --no-paginate
