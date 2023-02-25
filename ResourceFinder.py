import logging
import os
import boto3
from ecsController import ecsController
from ec2Controller import ec2Controller
from asgController import asgController
from rdsController import rdsController





"""
Finds all controllable interfaces that have a tag to indicate that they should be shutdown at the end of the day
"""
class ResourceFinder:

    ECS = "ECS"
    EC2 = "EC2"
    RDS = "RDS"
    ASG  = "ASG"

    def __init__(self,searchTermTag):
        self.logger =logging.getLogger(__name__)
        self.searchTag = searchTermTag





    """
    Catalogue Resources that are being controlled - by searching for the tag. This is used for auditing purposes
    """
    def findResourcesFor(self, region):
        allRecources={}

        ecs = ecsController(region, self.searchTag)


        allRecources[ResourceFinder.ECS]= ecs.findResourcesForECS()

        ec2 = ec2Controller(region, self.searchTag)
        allRecources[ResourceFinder.EC2] = ec2.findResourcesForEC2()

        asg  = asgController(region, self.searchTag)
        allRecources[ResourceFinder.ASG] = asg.findResourcesForASG()

        rds = rdsController(region, self.searchTag)
        allRecources[ResourceFinder.RDS] = rds.findResourcesForRDS(True)


        return allRecources

    """
    Start all the resources which has the search tag 
    :parameter DBWarm means that only the databases shall be started - as they take longer to start up. If this value is false everything but databases shall be started
    """
    def startResources(self, region, DBWarm=False):

        if not DBWarm:
            self.logger.info("Starting Application Tier Resources ")
            ecs = ecsController(region, self.searchTag)
            allok= ecs.startDayEvent()
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


            asg = asgController(region, self.searchTag )
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


    """
    Stops all the resources which has  the search tag
    """
    def stopResources(self, region):
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



