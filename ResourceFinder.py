import logging
import os
import boto3





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





    def findResourcesFor(self, region):
        allRecources={}

        allRecources[ResourceFinder.ECS]=
