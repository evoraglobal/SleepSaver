import logging
import os
import boto3
from ecsController import ecsController
from ec2Controller import ec2Controller
from asgController import asgController
from rdsController import rdsController
from cloudWatchAlarmController import cloudWatchAlarmController

class ResourceFinder:

    ECS = "ECS"
    EC2 = "EC2"
    RDS = "RDS"
    ASG = "ASG"
    CW_ALARM = "CW_ALARM"

    def __init__(self, searchTermTag):
        self.logger = logging.getLogger(__name__)
        self.searchTag = searchTermTag

    def findResourcesFor(self, region):
        allResources = {}

        ecs = ecsController(region, self.searchTag)
        allResources[ResourceFinder.ECS] = ecs.findResourcesForECS()

        ec2 = ec2Controller(region, self.searchTag)
        allResources[ResourceFinder.EC2] = ec2.findResourcesForEC2()

        asg = asgController(region, self.searchTag)
        allResources[ResourceFinder.ASG] = asg.findResourcesForASG()

        rds = rdsController(region, self.searchTag)
        allResources[ResourceFinder.RDS] = rds.findResourcesForRDS(True)

        cw_alarm = cloudWatchAlarmController(region, self.searchTag)
        allResources[ResourceFinder.CW_ALARM] = cw_alarm.findAlarms()

        return allResources

    def startResources(self, region, DBWarm=False):
        if not DBWarm:
            self.logger.info("Starting Application Tier Resources ")
            ecs = ecsController(region, self.searchTag)
            allok = ecs.startDayEvent()
            if allok:
                self.logger.info(f"****All ECS Started ok for region {region} ****")
            else:
                self.logger.warning(f"###### Not All the ECS Started OK for region {region} #######")

            ec2 = ec2Controller(region, self.searchTag)
            allok = ec2.startDayEvent()
            if allok:
                self.logger.info(f"****All EC2 Started ok**** for region {region}")
            else:
                self.logger.warning(f"###### Not All the EC2 Started OK for region {region }#######")

            asg = asgController(region, self.searchTag)
            allok = asg.startDayEvent()
            if allok:
                self.logger.info(f"****All ASG Started ok**** for region {region}")
            else:
                self.logger.warning(f"###### Not All the ASG Started OK for region {region}#######")
        else:
            self.logger.info("Starting RDS Resources - RDS PREWARM flag set")
            rds = rdsController(region, self.searchTag)
            allok = rds.startDayEvent()
            if allok:
                self.logger.info(f"****All RDS Started ok**** for region {region}")
            else:
                self.logger.warning(f"###### Not All the RDS Started OK for region {region}#######")
        
        # Enable alarms after starting services
        cw_alarm = cloudWatchAlarmController(region, self.searchTag)
        cw_alarm.enableAlarms()

    def stopResources(self, region):
        cw_alarm = cloudWatchAlarmController(region, self.searchTag)
        cw_alarm.disableAlarms()

        ecs = ecsController(region, self.searchTag)
        allok = ecs.stopDayEvent()
        if allok:
            self.logger.info("****All ECS Stopped ok****")
        else:
            self.logger.warning("###### Not All the ECS Stopped OK #######")

        ec2 = ec2Controller(region, self.searchTag)
        allok = ec2.stopDayEvent()
        if allok:
            self.logger.info("****All EC2 Stopped ok****")
        else:
            self.logger.warning("###### Not All the EC2 Stopped OK #######")

        asg = asgController(region, self.searchTag)
        allok = asg.stopDayEvent()
        if allok:
            self.logger.info(f"****All ASG Stopped ok**** for region {region}")
        else:
            self.logger.warning(f"###### Not All the ASG Stopped OK for region {region} #######")

        rds = rdsController(region, self.searchTag)
        allok = rds.stopDayEvent()
        if allok:
            self.logger.info(f"****All RDS Stopped ok**** for region {region}")
        else:
            self.logger.warning(f"###### Not All the RDS Stopped OK for region {region}#######")
