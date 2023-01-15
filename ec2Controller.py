""""
Controls EC2 Services
"""
import boto3
import logging
import os

"""
Ec2 controller: finds ec2 instances that have a devday tag, has the ability to stop, start and to modify their shutdown behaviour - to avoid termination
"""

class ec2Controller:

    STOPBEHAVIOUR = 'stop'

    def __init__(self, region, searchTag):
        self.region = region
        self.client = boto3.client('ec2', region_name= region)
        self.searchTag = searchTag.lower()
        self.logger = logging.getLogger(__name__)
        self.enabledServices = {}
        env = os.environ


    """
    Main entry point to be called from ResourceFinder - finds all EC2 Services that have been tagged
    Returns a  Map [instance id] : {state , platform , name}
    """
    def findResourcesForEC2(self):
        ec2Map = self.findServices(running=False) # Get all EC2 running or not that are tagged
        return ec2Map
    """
    Main entry point to signal a STOP of developer day event
    All tagged and running EC2 servers will be stopped
    """
    def stopDayEvent(self):

        result = True
        totalResult=True


        ec2Map = self.findServices(running=True) # Find all those that are currently running

        if len(ec2Map) ==0:
            self.logger.info("There are currently no active EC2 instances that are tagged - they all seemed stopped or do not exist")
            return True

        self.correctShutDownBehaviour(ec2Map)

        try:

            for ec2instance in ec2Map:
                ec2Dict = ec2Map[ec2instance]
                state = ec2Dict["state"]
                platform = ec2Dict["platform"]
                name = ec2Dict["name"]
                if state=="running":
                    response  = self.client.stop_instances(
                        InstanceIds = [ec2instance]
                    )
                    cs =  response['StoppingInstances'][0]['CurrentState']['Name']
                    self.logger.info(f"Shutting down instance {name} id {ec2instance}, plaform {platform} moving from running --> {cs}")
                    result = ("stopping" == cs)
                    if not result:
                        totalResult = False
        except Exception as e:
            self.logger.error("Could not stop all EC2 instances ")
            self.logger.exception(e)
            totalResult = False

        return totalResult

    """
    Main entry point to signal a START of developer day event
    Finds all tagged Ec2 servers that are currently stopped
    """
    def startDayEvent(self):
        result = True
        totalResult = True

        ec2Map = self.findServices(running=False)  # Find all those that are currently stopped

        if len(ec2Map) == 0:
            self.logger.info(
                "There are currently no stopped EC2 instances that are tagged - they are either running or dont exist")
            return True
        try:

            for ec2instance in ec2Map:
                ec2Dict = ec2Map[ec2instance]
                state = ec2Dict["state"]
                platform = ec2Dict["platform"]
                name = ec2Dict["name"]
                if state=="stopped":
                    response  = self.client.start_instances(
                        InstanceIds = [ec2instance]
                    )
                    cs =  response['StartingInstances'][0]['CurrentState']['Name']
                    self.logger.info(f"Starting up  instance {name} id {ec2instance}, plaform {platform} moving from stopped --> {cs}")
                    result = ("pending" == cs)
                    if not result:
                        totalResult = False
        except Exception as e:
            self.logger.error("Could not start all EC2 instances ")
            self.logger.exception(e)
            totalResult = False

        return totalResult

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
    if the running parameter is set to True only instances that are currently running will be picked up, passing False will flag all those that are stopped
    Returns a MAP of [instance id] : {state , platform , name}
    """
    def findServices(self, running=True):

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
                    name = '(no name)'
                    for tag in tags:
                        k = tag['Key']
                        if k.lower() =='name':
                            name = tag['Value']
                            break

                    if self._checkforTag(tags):
                        self.logger.info(f"EC2: {name} instance-id {instanceId} - platform {platform}, current state {state} is tagged for Developer day/night")
                        if (running and state=="running") or (not running and state=="stopped"):
                            serviceMap[instanceId] = {"state" : state, "platform" : platform, "name": name}
                        else:
                            self.logger.info(f"EC2: skipping  instance_id {instanceId} {name} as it is already in the desired state")
                    else:
                        self.logger.info(f"EC2: skipping untagged instance_id {instanceId} {name}")


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



