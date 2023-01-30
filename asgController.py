""
import boto3
import logging
import os
from elb import elb

DBTABLEENV = "ASGDYNTABLE"
DBREGION = "ASGREGION"

ENVTAGNAME = "elasticbeanstalk:environment-id"

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
        self.elbins = elb(searchTag,region)

    """
        Checks The tags for the DevDay search tag
        for the special searchTag - and see if the Tag is set to TRUE
        return True or False
    """
    def _checkforTag(self, tagList):

        for tag in tagList:
            key = tag['Key']
            value = tag['Value']
            if key.lower() == self.searchTag and value.lower() == 'true':
                return True
            # check to see if this an elastic beanstalk controlled ASG
            if key == ENVTAGNAME:
                return self.elbins.isEnvironmentTagged(value)

        return False


    """
       Main entry point to be called from ResourceFinder - finds all ASG Auto Scale Groups that are active
       if Running is set to True then only those with desiredSize > 0 will be returned
       Returns a MAP[asgName] = {minSize: x, desiredSize, y , maxSize z}
    """
    def findResourcesForASG(self, running=False):
        asgMap = {}
        try:
            response = self.client.describe_auto_scaling_groups(MaxRecords=100)
            nextToken = "A"

            while nextToken is not None:
                asgList = response.get("AutoScalingGroups", [])
                for asg in asgList:
                    asgName = asg["AutoScalingGroupName"]
                    minSize = int(asg["MinSize"])
                    maxSize = int(asg["MaxSize"])
                    desiredSize = int(asg["DesiredCapacity"])
                    tags = asg.get("Tags",[])
                    if self._checkforTag(tags):
                        if running and desiredSize>0 or not running:
                            self.logger.info(f"Adding tagged ASG {asgName}")
                            asgMap[asgName]={"minSize" : minSize,
                                             "desiredSize" : desiredSize,
                                             "maxSize" : maxSize}
                    else:
                        self.logger.info(f"Skipping untagged ASG {asgName}")
                nextToken = response.get("NextToken", None)
                if nextToken is not None:
                    response = self.client.describe_auto_scaling_groups(NextToken=nextToken,MaxRecords=100)

        except Exception as e:
            self.logger.warning(f"Could not access ASG in resources in {self.region}")
            self.logger.exception(e)

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


        # Loads whats currently in the database and clear it out
        oldMap = self._loadState()
        self._deleteState(oldMap)

        self._storeState(asgMap)

        for asgName in asgMap:
            # time to sleep the EC2 attached to the ASG
            result = self._setCapacity(asgName,0,0,0)
            if not result:
                self.logger.warning(f"Could not set the Capacity to sleep for {asgName} ")
                totalResult = False

        return totalResult

    """
       Main entry point to signal a START of developer day event
       Loads previously stored state from the database and if the ASG still exists - it restores it
       """

    def startDayEvent(self):
        result = True
        totalResult = True

        asgMap = self.findResourcesForASG(running=False)  # Find all those that are currently stopped

        if len(asgMap) == 0:
            self.logger.info(
                "There are currently no ASG that are tagged - they are either running or dont exist")
            return True

        loadedMap = self._loadState()
        if len(loadedMap) ==0:
            self.logger.warning(f"The ASG State is no longer in the database table {self.asgTable} - so the ASG can not be reactivated")
            return False

        for asg in asgMap:
            max = asgMap[asg]["maxSize"]
            if asg in loadedMap:
                dimensions = loadedMap[asg]
                if max==0:
                    self.logger.info(f"Waking up ASG - with the following dimensions {dimensions}")
                    result = self._setCapacity(asg,dimensions["minSize"], dimensions["desiredSize"], dimensions["maxSize"])
                    if not result:
                        totalResult = False
            else:
                self.logger.warning(f"The ASG {asg} was not found in the database {self.asgTable}")
        return totalResult



    """
    Set the capacity limits on a given ASG
    returns boolean - based on success
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
    expects a a MAP[asgName] = {minSize: x, desiredSize, y , maxSize z}
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
                self.logger.info(f"Storing current capacity state for {asg} min {min}, desired {desired}, Max {max}")

                response = client.put_item(
                    TableName=self.asgTable,
                    Item={
                        'asgName': {'S': asg},
                        'region' : {'S' : self.region},
                        'min' : {'N': f'{min}'},
                        'max' : {'N': f'{max}'},
                        'desired' : {'N': f'{desired}'}
                    })
        except Exception as e:
            self.logger.exception(f"Failed to store state inside dynamodb Table {self.asgTable}. \nPayload was {asgMap}")
            self.logger.exception(e)
            return False

        return True

    """
       Loads the stored state relating to ASGs --> Service desired count numbers 
       Returns:    a MAP[asgName] = {minSize: x, desiredSize, y , maxSize z}
       """

    def _loadState(self):
        client = boto3.client('dynamodb', region_name=self.dbregion)
        response = client.scan(
            TableName=self.asgTable,
            AttributesToGet=[
                'asgName', 'region', 'min', 'max', 'desired'
            ],
            Limit=999)
        items = response.get("Items", [])
        asgMap = {}
        for item in items:
            region = item['region']['S']
            asgName = item["asgName"]['S']
            min = int(item["min"]['N'])
            max = int(item["max"]['N'])
            desired =int( item["desired"]['N'])

            if region == self.region:

                self.logger.info(
                    f"restoring state: ASG  Name: {asgName}, capacity min {min }, desired {desired}, max {max}")

                asgMap[asgName] = {"minSize": min,
                                   "desiredSize": desired,
                                   "maxSize": max}


            else:
                self.logger.info(f"loading data Ignoring region {region} ")

        return asgMap

    """
       Delete all records passed from the database  for a given record
       expects a MAP[asgName] = {minSize: x, desiredSize, y , maxSize z}
       """

    """
    Deletes the ASG Maps in the database 
    """
    def _deleteState(self, asgMap):

        client = boto3.client('dynamodb', region_name=self.dbregion)

        for asg in asgMap:

                self.logger.info(f"Clearing out DB Records from the Table {self.asgTable}  -> {asg}")
                response = client.delete_item(
                    TableName=self.asgTable,
                    Key={
                        'asgName': {'S': asg},
                        'region': {'S': self.region}
                    })
