mkdir zippackage
cp *.py ./zippackage

cd zippackage
zip -r ../lambda.zip .
cd ..
aws lambda update-function-code --function-name sleepsaver --zip-file fileb://lambda.zip --region eu-west-2 --no-paginate