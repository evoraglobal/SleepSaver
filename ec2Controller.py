""""
Controls EC2 Services
"""
import boto3
import logging
import os

"""
Ec2 controller: finds ec2 instances that have a devday tag, has the ability to stop, start and to modify their shutdown behaviour - to avoid termination
"""

class ec2Contoller:

    STOPBEHAVIOUR = 'stop'

    def __init__(self, region, searchTag):
        self.region = region
        self.client = boto3.client('ec2', region_name= region)
        self.searchTag = searchTag.lower()
        self.logger = logging.getLogger(__name__)
        self.enabledServices = {}
        env = os.environ


    """
    Main entry point to be called from ResourceFinder - finds all EC2 Services that have a Task running
    Returns a MAP[InstanceId] = [ list of Instance ARNS] or []
    """
    def findResourcesForECS(self):
        clusterServiceMap = self.findServices() # Get all EC2 running
        return clusterServiceMap
    """
    Main entry point to signal a STOP of developer day event
    The current running ECS services  will have their current desired count stored into a database and then their desired count will be set to 0 in the ecs clusters
    """
    def stopDayEvent(self):

        result = True


        ec2Map = self.findServices()  # Get all ECS running

        if len(ec2Map) ==0:
            self.logger.info("There are currently no active EC2 instances that are tagged - they all seemed stopped or do not exist")
            return True


        return result

    """
    Main entry point to signal a START of developer day event
    """
    def startDayEvent(self):
        result = True

        return result

    """
    Checks the SERVICE ARN for the special searchTag - and see if the Tag is set to TRUE
    return True or False
    """
    def _checkforTag(self,tagsDict):
        self.logger.debug(f"Tags are {tagsDict}")
        for tag in tagsDict:
            key = tag.get('Key')
            if key is not None:
                value=tag['Value'].lower()
                if key.lower() == self.searchTag and value=='true':
                    return True

        return False
    """
    Finds all Ec2 instances that exist with a dev day tag
    Returns a MAP of [instance id] : {state , platform etc}
    """
    def findServices(self):

        serviceMap = {}
        response = self.client.describe_instances()
        nextToken = "A"
        while nextToken is not None:

            nextToken = response.get("NextToken")
            reservationL = response.get("Reservations",[])
            for reservation in reservationL:
                instanceL = reservation.get("Instances",[])
                for ins in instanceL:
                    self.logger.debug(f"Instance Details: {ins} ")
                    instanceId = ins["InstanceId"]
                    platform = ins.get("Platform","Linux")
                    state = ins["State"]['Name']
                    tags = ins.get('Tags',[])
                    if self._checkforTag(tags):
                        self.logger.info(f"EC2: instance-id {instanceId} - platform {platform}, current state {state} is tagged for Developer day/night")
                        serviceMap[instanceId] = {"state" : state, "platform" : platform}
                    else:
                        self.logger.info(f"EC2: skipping untagged instance_id {instanceId}")


            if nextToken is not None:
                response = self.client.describe_instances(NextToken=nextToken)
        return serviceMap


    """
    Makes sure the instances are not terminated when they are shutdown - this method returns the behaviour
    """
    def _getShutdownBehavior(self, instanceID):

        response = self.client.describe_instance_attribute(
            Attribute= 'instanceInitiatedShutdownBehavior' ,
            InstanceId=instanceID)

        behaviour = response['InstanceInitiatedShutdownBehavior']['Value']
        self.logger.info(f"instance {instanceID}, shutdown behaviour is currently set to {behaviour}")

        return behaviour

    def correctShutDownBehaviour(self, serviceMap):
        self.logger.info("EC2: Checking and correcting the shutdown behaviour to avoid instance termination when sleeping")
        for instance in serviceMap:
            behaviour = self._getShutdownBehavior(instance)
            if not behaviour == self.STOPBEHAVIOUR:
                self.logger.info(f"EC2: Correcting Shutdown behaviour.... on instance {instance}")
                response =self.client.modify_instance_attribute(
                    InstanceId = instance,
                    InstanceInitiatedShutdownBehavior={"Value" : self.STOPBEHAVIOUR})
            else:
                self.logger.info(f"EC2: shutdown behaviour on instance {instance} already correctly set to STOP")



