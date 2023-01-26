#Create a folder called "zippackage"
New-Item -ItemType Directory -Path "zippackage"

#Copy all files with the .py extension to the "zippackage" folder
Get-ChildItem -Filter "*.py" | Copy-Item -Destination "zippackage"

#Change the current directory to "zippackage"
Set-Location -Path "zippackage"

#Create a zip file of the "zippackage" folder and save it as "sleepsaverlambda.zip" in the parent directory
Compress-Archive -Path * -DestinationPath "..\sleepsaverlambda.zip"

#Change the current directory back to the parent directory
Set-Location -Path ".."

#Copy the zip into  s3 bucket
aws s3 cp ./sleepsaverlambda.zip s3://evg-sleepsaver-cf/

#Update the lambda to read code from zip
aws lambda update-function-code --function-name SleepSaverProd --zip-file fileb://sleepsaverlambda.zip --region eu-west-2 --no-paginate