""
import boto3
import logging
import os

DBTABLEENV = "ELBDYNTABLE"
DBREGION = "ELBREGION"

class asgController:

    def __init__(self, region, searchTag):
        env = os.environ
        self.asgTable = env.get(DBTABLEENV, "asgState")
        self.dbregion = env.get(DBREGION, "eu-west-2")
        self.region = region
        self.client = boto3.client('autoscaling', region_name= region)
        self.searchTag = searchTag.lower()
        self.logger = logging.getLogger(__name__)
        self.enabledServices = {}
        env = os.environ
        self.ecsTable = env.get(DBTABLEENV, "ecsState")
        self.dbregion = env.get(DBREGION, "eu-west-2")

    """
        Checks The tags for the DevDay search tag
        for the special searchTag - and see if the Tag is set to TRUE
        return True or False
    """
    def _checkforTag(self, tagList):

        for tag in tagList:
            key = tag['Key']
            value = tag['Value'].lower()
            if key.lower() == self.searchTag and value == 'true':
                return True

        return False


    """
       Main entry point to be called from ResourceFinder - finds all ASG Auto Scale Groups that are active
       if Running is set to True then only those with desiredSize > 0 will be returned
       Returns a MAP[asgName] = {minSize: x, desiredSize, y , maxSize z}
    """
    def findResourcesForASG(self, running=False):
        asgMap = {}
        response = self.client.describe_auto_scaling_groups()
        asgList = response.get("AutoScalingGroups",[])
        for asg in asgList:
            asgName = asg["AutoScalingGroupName"]
            minSize = asg["MinSize"]
            maxSize = asg["MaxSize"]
            desiredSize = asg["DesiredCapacity"]
            tags = asg.get("Tags",[])
            if self._checkforTag(tags):
                if running and desiredSize>0 or not running:
                    self.logger.info(f"Adding tagged ASG {asgName}")
                    asgMap[asgName]={"minSize" : minSize,
                                     "desiredSize" : desiredSize,
                                     "maxSize" : maxSize}
            else:
                self.logger.info(f"Skipping untagged ASG {asgName}")
        return asgMap

    """
       Main entry point to signal a STOP of developer day event
       All tagged and running EC2 servers will be stopped if they belong to an ASG
    """

    def stopDayEvent(self):

        result = True
        totalResult = True

        asgMap = self.findResourcesForASG(running=True)  # Find all those that are currently running

        if len(asgMap) == 0:
            self.logger.info(
                "There are currently no active ASG instances that are tagged - they all seemed stopped or do not exist")
            return True

        self._storeState(asgMap)

        for asgName in asgMap:
            # time to sleep the EC2 attached to the ASG
            result = self._setCapacity(asgName,0,0,0)
            if not result:
                self.logger.warning(f"Could not set the Capacity to sleep for {asgName} ")
                totalResult = False

        return totalResult

    """
    Set the capacity limits on a given ASG
    """
    def _setCapacity(self,asgName, min ,desired, max):
        if min > desired:
            self.logger.error("min cannot be more than desired capcity")
            return False
        if desired> max:
            self.logger.error("desired capacity cannot be more than max")
            return False
        if min > max:
            self.logger.error("Min capacity cannot be more max")
            return False

        try:
            self.logger.info(f"Setting the capacity level of ASG {asgName} to MinSize {min}m DesiredCapacity {desired}, Max {max}")
            self.client.update_auto_scaling_group(AutoScalingGroupName=asgName,MinSize=min, MaxSize=max, DesiredCapacity=desired)
            return True
        except Exception as e:
            self.logger.error(f"Updating ASG capacity for {asgName} to min:{min} desired{desired} max:{max} caused an exception")
            self.logger.exception(e)
        return  False


    """"
    Writes the ASG instance dimensions desired state into the dynamoDB table.
    expects a MAP of clusters --- [ [Service Arns, service Name, desired state]]
    returns True if was all stored ok
    """
    def _storeState(self, asgMap):

        if len(asgMap) ==0:
            self.logger.warning("ASGMap is empty - meaning nothing is  running - so there is nothing to store")
            return False

        client = boto3.client('dynamodb', region_name=self.dbregion)
        try:

            for asg in asgMap:
                dimensions = asgMap[asg]
                min = dimensions["minSize"]
                max = dimensions["maxSize"]
                desired = dimensions["desiredSize"]
                self.logger.info(f"fStoring current capacity state for {asg} min {min}, desired {desired}, Max {max}")

                response = client.put_item(
                    TableName=self.asgTable,
                    Item={
                        'asgName': {'S': asg},
                        'region' : {'S' : self.dbregion},
                        'min' : {'N': f'{min}'},
                        'max' : {'N': f'{max}'},
                        'desired' : {'N': f'{desired}'}
                    })
        except Exception as e:
            self.logger.exception(f"Failed to store state inside dynamodb Table {self.asgTable}. \nPayload was {asgMap}")
            self.logger.exception(e)
            return False

        return True