mkdir zippackage
cp *.py ./zippackage

cd zippackage
zip -r ../sleepsaverlambda.zip .
cd ..
aws lambda update-function-code --function-name sleepsaver --zip-file fileb://sleepsaverlambda.zip --region eu-west-2 --no-paginate
