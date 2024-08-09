#####################################################################################################################
#### The following section will need to be run in the Sandbox-Control account and will deploy the code ##############
#### to the s3 bucket ###############################################################################################
#####################################################################################################################

# Name of the zip file
$zipFileName = "sleepsaverlambda.zip"

$CODEBUCKET = 'evg-sleepsaver-cf'
$currentDirectory = Get-Location

# List of files to be zipped
$files = @(
    ".\asgController.py",
    ".\ec2Controller.py",
    ".\ecsController.py",
    ".\elb.py",
    ".\lambda_function.py",
    ".\rdsController.py",
    ".\ResourceFinder.py",
    ".\cloudWatchAlarmController.py"
)

# Remove existing zip file if it exists
if (Test-Path $zipFileName) {
    Remove-Item $zipFileName
}

# Create the zip file and add each file to it
foreach ($file in $files) {
    if (Test-Path $file) {
        Compress-Archive -Path $file -Update -DestinationPath $zipFileName
    } else {
        Write-Host "File not found: $file"
    }
}

Write-Host "Specified files have been zipped into $zipFileName"

aws s3 cp $currentDirectory/CF s3://$CODEBUCKET/ --recursive --profile AWSAdministratorAccess-495799715217
aws s3 cp $currentDirectory/sleepsaverlambda.zip s3://$CODEBUCKET/ --profile AWSAdministratorAccess-495799715217

#####################################################################################################################
# The following section will need to be run in the Origional account to deploy the cloudformation ###################
#####################################################################################################################

#aws cloudformation deploy --stack-name SleepSaverLambdav2 --template-file ./sleepsaverlambda.yml --region eu-west-2 --capabilities CAPABILITY_NAMED_IAM --profile AWSAdministratorAccess-495799715217

