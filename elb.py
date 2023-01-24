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
        client =  self.session.client('elasticbeanstalk')
        response = client.list_tags_for_resource(
            ResourceArn=elbarn)

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
        self.session = boto3.session.Session(region_name=region)
        client = self.session.clsoient('elasticbeanstalk')
        response = client.describe_environments()
        nextToken='A'
        self.logger.debug(f"^^^^^ ELASTIC RESPONSE {response} ")
        while  nextToken is not None:
            nextToken = response.get('NextToken',None)
            envList = response.get('Environments', [])

            for environment in envList:
                arn = environment["EnvironmentArn"]
                envid = environment['EnvironmentId']
                if self._isTagged(arn):
                    self.taggedEnvironmentIDList.append(envid)
                    self.logger.info(f"Elastic beanstalk {arn} is tagged, corresponding EID is {envid}")
                else:
                    self.logger.info(f"Elastic beanstalk {arn} is NOT tagged, corresponding EID is {envid}")

            if nextToken is not None:
                response = self.client.describe_environments(NextToken=nextToken)
        self.logger.info(f"******* Elastic Beanstalk tagged environments {region} *******")
        for eid in self.taggedEnvironmentIDList:
            self.logger.info(f"Elastic EID {eid}")
        self.logger.info("----End beantalk init -----")



    """
    Checks to see a given environment ID is tagged for Dev Day / Night action. ie the environment has a DEVDAY : TRUE tag
    """
    def isEnvironmentTagged(self, environmentId):
        result = (environmentId in self.taggedEnvironmentIDList)
        self.logger.info(f"Elastic Beantalk env id {environmentId} - isTagged: {result} ")
        return  result

