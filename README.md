# AWSleepSaver

AWSleepSaver is a tool that allows you to easily manage your AWS resources and reduce costs by shutting down unused resources during non-working hours. It could save you up to 60/70% of AWS costs and carbon footprint as resources won’t be running without any good use.

## How it works

AWSleepSaver uses AWS Event Bridge and upon installation adds two rules to your environment: `SleepSaverDayRule` and `SleepSaverNightRule`. These two rules include a programmable cronjob expression which declares when day start and end times are. 

:warning: Only UTC time is supported. Change your cronexpression for clocks going forward/back.

The rules interface with the logic lambda function, `SleepSaverProd`and state machine `sleepSaverDelayedAppTierCF`. These targets go through the process of waking up/shutting down the services which include the tag `DevDay: true`.

The tool supports the following AWS services at both a cluster and instance level:

- EC2s
- ECS
- RDS
- Elastic Beanstalks (works on an environment level)
- Autoscale groups belonging to load balancers

## Prerequesites

- AWS Account (With **IAM credentials** and **IAM access key pair**)
- AWS CLI v2 or higher

## Installation

1. From the environment you want to install on, procure AWS creds for AWS CLI usage
2. Using AWS CLI, ensure you are in the correct bucket directory and run `singleLineInstall.sh`
3. Add the tag, `DevDay: true` to the environment you wish to use AWSleepSaver

| Parameters | Description | Input |
| --- | --- | --- |
| `--stack-name` | defines cloud formation name | Any String |
| `--template-file` | local setup file to build environment | Defaults to `./sleepsaverlambda.yml` |
| `--region` | Set environment region | Choose predefined [region](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html#Concepts.RegionsAndAvailabilityZones.Regions) |
| `--parameter-overrides` | programmable option housing a cronjob expression for changing default shutoff and start times | There are two available options: <br />- "DayScheuldeExpression" <br />- "NightScheuldeExpression" |

`--parameter-overrides` Examples:

```bash
--parameter-overrides = "DayScheuldeExpression=cron(29 7 ? * 2-6 *)" # Read as "at 07:29 turn on, when on days 2-6" (Monday-Friday).
--parameter-overrides = "NightScheuldeExpression=cron(45 18 * * ? *)" # Read as "at 18:45, turn off every day".
```

## How to use

It is easy to incorporate AWSleepSaver. Simply add the `DevDay` tag and set it's boolean status. When the option is set to `true`, AWSleepSaver finds when that resource is set to end for the working day and shuts it down. Similarly, when the next working day starts, it boots back up. For example, shuts down on Friday at 18:00 and reboots on Monday at 08:00.

The tool can be overwritten manually using regular methods to turn off/on, and it reduces developer friction as it is set up decentralised with other developers not needing to interact with SleepSaver. There is no need to know install paths or setup restrictions.

The functionality can be temporarily unregistered without removing it by setting the tag to `false`.

## Diagram

<!--Waiting on advice-->

## Note

If the user wants to create an updated bucket version separate from Evora, they must create a copy of evg-sleepsaver-cf under their CodeBucket and rename it under Sleepsaverlambda.yml.
