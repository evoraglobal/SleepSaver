import logging
import os
import boto3
from ecsController import ecsContoller





"""
Finds all controllable interfaces that have a tag to indicate that they should be shutdown at the end of the day
"""
class ResourceFinder:

    ECS = "ECS"
    EC2 = "EC2"
    RDS = "RDS"

    def __init__(self,searchTermTag):
        self.logger =logging.getLogger(__name__)
        self.searchTag = searchTermTag




    """
    Catalogue Resources that are being controlled - by searching for the tag. This is used for auditing purposes
    """
    def findResourcesFor(self, region):
        allRecources={}

        ecs = ecsContoller(region, self.searchTag)

        allRecources[ResourceFinder.ECS]= ecs.findResourcesForECS()

        return allRecources

    """
    Start all the resources which has the search tag 
    """
    def startResources(self, region):

        ecs = ecsContoller(region, self.searchTag)
        allok= ecs.startDayEvent()
        if allok:
            self.logger.info("****All ECS Started ok****")
        else:
            self.logger.warning("###### Not All the ECS Started OK #######")

    """
    Stops all the resources which has  the search tag
    """
    def stopResources(self, region):
        ecs = ecsContoller(region, self.searchTag)
        allok = ecs.stopDayEvent()
        if allok:
            self.logger.info("****All ECS Stopped ok****")
        else:
            self.logger.warning("###### Not All the ECS Stopped OK #######")

