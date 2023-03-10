# AWSleepSaver

AWSleepSaver is a tool that allows you to easily manage your AWS resources and reduce costs by shutting down unused resources during non-working hours. It could save you up to 60/70% of your AWS development  costs and carbon footprint as resources won’t be running without any good use.

## How it works

AWSleepSaver uses AWS Event Bridge Schedule and upon installation adds two rules to your environment: `SleepSaverDayRule` and `SleepSaverNightRule`. These two rules include a programmable cronjob expression which declares when day start and end times of each workday are. 

:warning: Only UTC time is supported. Change your cron expression for clocks going forward/back.

The rules interface with the logic lambda function, `SleepSaverProd`and state machine `sleepSaverDelayedAppTierCF`. These targets go through the process of waking up/shutting down the services which include the tag `DEVDAY: TRUE`.

The lambda has an environment variable called REGIONLIST which limits the number of regions that are scanned for tagged resources. If you remove this environment variable all accessible regions will be scanned.


The tool supports the following AWS services :

- EC2s
- ECS
- RDS (at both a cluster and instance level)
- Elastic Beanstalks (works on an environment level)
- Autoscale groups (ASGs)

Note: For ASGs , Elastic beanstalks and ECS environments the number of instances will be restored to whatever level were running the night before.
DynamoDB is used to retain this state information.

As there can be transient errors if the application tier wakes up before the RDS databases become available. The RDS instances will be started 40 minutes before the application tier.
The RDS are started at the time -defined by the cron expression. The Application tier T+40 minutes. This offset can be configured by changing the **Seconds** parameter in the **stepsyntax.json**  
If you are not using any RDS databases is recommended to reduce this figure - as there is little need to wait the 40 minutes.


## Prerequesites

- AWS Account (With ** programatic IAM credentials**)
- AWS CLI v2 or higher

## Installation

1. From the environment you want to install on, procure AWS creds for AWS CLI usage
2. Using AWS CLI, ensure you are in the correct bucket directory and run `singleLineInstall.sh`
3. Add the tag, `DEVDAY' setting its value to TRUE` for the resources you wish to be controlled  by AWSleepSaver

Note: This quick installation method uses our version of the packaged code located in the public bucket evg-sleepsaver-cf. If you wish 
to modify code you will have to package the code yourself and store it in your own private bucket. This can be done by using the createSleepSaverLambda.sh.

### Installation Parameters

| Parameters | Description | Input |
| --- | --- | --- |
| `--stack-name` | defines cloud formation name | Any String |
| `--template-file` | local setup file to build environment | Defaults to `./sleepsaverlambda.yml` |
| `--region` | Set environment region | Choose predefined [region](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html#Concepts.RegionsAndAvailabilityZones.Regions) |
| `--parameter-overrides` | programmable option housing a cronjob expression for changing default shutoff and start times | There are two available options: <br />- "DayScheduleExpression" <br />- "NightScheduleExpression" |

`--parameter-overrides` Examples:

```bash
--parameter-overrides = "DayScheduleExpression=cron(29 7 ? * 2-6 *)" # Read as "at 07:29 turn on, when on days 2-6" (Monday-Friday).
--parameter-overrides = "NightScheduleExpression=cron(45 18 * * ? *)" # Read as "at 18:45, turn off every day".
```

## How to use

It is easy to incorporate AWSleepSaver. Simply add the `DEVDAY` tag and set it's boolean status. When the option is set to `true`, AWSleepSaver finds when that resource is set to end for the working day and shuts it down. Similarly, when the next working day starts, it boots back up. For example, shuts down on Friday at 18:00 and reboots on Monday at 08:00.
The use of tags reduces developer friction as it is set up decentralised with other developers not needing to interact with AWSleepSaver directly. 

The tool can be overwritten globally by disabling the EventBridge rules, or for individual tagged resources by setting the DEVDAY status to FALSE.

## Diagram

<!--Waiting on advice-->

