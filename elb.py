import boto3
import logging

""" 
Finds DEVDAY tags for elastic BeanStalks and builds a map of AutoScale Group names that correspond to the tagged environments
"""
class elb:

    """
    Returns true if the search tag is present and is set to True
    """
    def _isTagged(self,elbarn):
        self.logger.info(f"Checking ELB Arn {elbarn} for search tag")
        response = self.client.list_tags_for_resource(
            ResourceArn='arn:aws:elasticbeanstalk:eu-west-2:307494535005:environment/SleepSaverTest/Sleepsavertest-env')

        tagList = response.get("ResourceTags",[])
        for tag in tagList:
            name = tag['Key'].lower()
            value = tag['Value'].lower()
            if name == self.searchKey and value=='true':
                self.logger.info(f"elb arn {elbarn} is tagged for Dev Day/Night")
                return True
        return False


    def __init__(self, searchKey, region):
        self.logger = logging.getLogger(__name__)
        self.searchKey = searchKey.lower()
        self.taggedEnvironmentIDList = []

        self.client = boto3.client('elasticbeanstalk', region_name=region)
        response = self.client.describe_environments()
        nextToken='A'
        while  nextToken is not None:
            nextToken = response.get('NextToken',None)
            envList = response.get('Environments', [])
            for environment in envList:
                arn = environment["EnvironmentArn"]
                envid = environment['EnvironmentId']
                if self._isTagged(arn):
                    self.taggedEnvironmentIDList.append(envid)

            if nextToken is not None:
                response = self.client.describe_environments(NextToken=nextToken)


    """
    Checks to see a given environment ID is tagged for Dev Day / Night action. ie the environment has a DEVDAY : TRUE tag
    """
    def isEnvironmentTagged(self, environmentId):
        result = environmentId in self.taggedEnvironmentIDList
        self.logger.info(f"Elastic Beantalk env id {environmentId} - isTagged: {result} ")
        return  result

