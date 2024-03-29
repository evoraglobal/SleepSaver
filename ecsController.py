""""
Controls ECS Services
"""
import boto3
import logging
import os

DBTABLEENV = "ECSDYNTABLE"
DBREGION = "ECSDBREGION"

class ecsController:

    def __init__(self, region, searchTag):
        self.region = region
        self.client = boto3.client('ecs', region_name= region)
        self.searchTag = searchTag.lower()
        self.logger = logging.getLogger(__name__)
        self.enabledServices = {}
        env = os.environ
        self.ecsTable = env.get(DBTABLEENV, "ecsStatev2")
        self.dbregion = env.get(DBREGION, "eu-west-2")

    """
    Main entry point to be called from ResourceFinder - finds all ECS Services that have a Task running
    Returns a MAP[ClusterARN] = [ list of Service ARNS] or []
    """
    def findResourcesForECS(self):
        clusterServiceMap = self.findServices() # Get all ECS running
        return clusterServiceMap
    """
    Main entry point to signal a STOP of developer day event
    The current running ECS services  will have their current desired count stored into a database and then their desired count will be set to 0 in the ecs clusters
    """
    def stopDayEvent(self):




        clusterServiceMap = self.findServices()  # Get all ECS running
        clusterServiceStateMap = self.getDesiredState(clusterServiceMap) # find current desired Map Levels

        if len(clusterServiceStateMap) ==0:
            self.logger.info("There are currently no active ECS Services - they all seemed stopped or do not exist")
            return True

        # clean out what is currenty in the database
        clusterStoredMap = self.loadState()
        self._deleteState(clusterStoredMap)


        self.storeState(clusterServiceStateMap) # store in the db the current levels
        result= self.setState(clusterServiceStateMap,overrideDesiredCount=0)
        if result:
            self.logger.info("All the running services have been updated to have 0 desired state - all stopping")
        else:
            self.logger.warning("Not all services could have their desired state updated")
        return result

    """
    Main entry point to signal a START of developer day event
    """
    def startDayEvent(self):
        clusterStoredMap = self.loadState()

        if len(clusterStoredMap)==0:
            self.logger.info("There was no stored desired Stated for ECS Services in the database - so nothing requires starting")
            return True

        result = self.setState(clusterStoredMap)
        if result:
            self.logger.info("All the running services have been updated to their original desired State levels")
        else:
            self.logger.warning("Not all services could have their desired state updated")
        return result

    """
    Checks the SERVICE ARN for the special searchTag - and see if the Tag is set to TRUE
    return True or False
    """
    def _checkforTag(self,serviceArn):
        response = self.client.list_tags_for_resource(
                                                            resourceArn=serviceArn
                                                            )
        tagList  = response.get('tags')
        for tag in tagList:
            key = tag['key']
            value=tag['value'].lower()
            if key.lower() == self.searchTag and value=='true':
                self.logger.info(f"---------- Service {serviceArn} has {self.searchTag} enabled")
                return True

        return False

    """
    Gets the current Desired  number of Running tasks for a given service List - providing a service as atleast one running task
    Pass in a MAP of clusters --> [Service Arns]
    Returns a MAP of clusters --- [ [Service Arns,Service Name, desired state]]
    """
    def  getDesiredState(self,serviceArnClusterMap):
        resultMap = {}
        for cluster in serviceArnClusterMap:
            serviceArnList = serviceArnClusterMap[cluster]
            itemCount= len(serviceArnList)
            partialList = serviceArnList[0:10]
            # need to take the ecs list 10 at a time
            while len(partialList) >0:
                # remove the current 10 from the list
                serviceArnList=serviceArnList[10:]

                response = self.client.describe_services(
                                                        cluster=cluster,
                                                        services=partialList
                         )
                partialList = serviceArnList[0:10]
                serviceList = response.get("services" ,[])
                for serviceMap in serviceList:
                    sarn = serviceMap["serviceArn"]
                    runningCount = serviceMap["runningCount"]
                    sname  = serviceMap["serviceName"]
                    if runningCount  >0:

                        # Ok there is something running so we had better make a results entry for this cluster
                        if cluster not in resultMap:
                            resultMap[cluster] = []

                        desiredCount = serviceMap["desiredCount"]
                        self.logger.info(f"Cluster {cluster} - Service Name  {sname} ARN {sarn} has Task desired Count {desiredCount} ")
                        resultMap[cluster].append([sarn,sname, desiredCount])
                    else:
                        self.logger.warning(f"Service Name {sname} has no task running - so ignoring")


        return resultMap

    """
    Delete all records passed from the database 
    expects a MAP of clusters --- [ [Service Arns, service Name, desired state]]
    """
    def _deleteState(self, clusterMap):

        client = boto3.client('dynamodb', region_name=self.dbregion)

        for cluster in clusterMap:
            serviceList = clusterMap[cluster]
            for service in serviceList:
                sarn = service[0]
                sname = service[1]

                self.logger.info(f"Clearing out DB Records {sname} --> service arn {sarn}")
                response = client.delete_item(
                                                TableName=self.ecsTable,
                                                Key={
                                                    'ecsArn': {'S': sarn},
                                                    'region' : {'S' : self.region}
                                                    })

    """"
    Writes the cluster/service desired state into the dynamoDB table.
    expects a MAP of clusters --- [ [Service Arns, service Name, desired state]]
    returns True if was all stored ok
    """
    def storeState(self, clusterMap):

        if len(clusterMap) ==0:
            self.logger.warning("There are no ClusterMap is empty - meaning nothing is  running - so there is nothing to store")
            return False

        client = boto3.client('dynamodb', region_name=self.dbregion)
        try:

            for cluster in clusterMap:
                serviceList = clusterMap[cluster]
                for service in serviceList:
                    sarn = service[0]
                    sname = service[1]
                    desired = service[2]
                    response = client.put_item(
                        TableName=self.ecsTable,
                        Item={
                            'ecsArn': {'S': sarn},
                            'region' : {'S' : self.dbregion},
                            'servicename' : {'S': sname},
                            'clusterArn' : {'S':cluster},
                            'desiredCount' : {'N': f'{desired}'}
                        })
        except Exception as e:
            self.logger.exception(f"Failed to store state inside dynamodb. \nPayload was {clusterMap}")
            self.logger.exception(e)
            return False

        return True

    """
    Loads the stored state relating to cluster --> Service desired count numbers 
    Returns:   a MAP of clusters --- [ [Service Arns, service Name, desired state]]
    """
    def loadState(self):
        client = boto3.client('dynamodb', region_name=self.dbregion)
        response = client.scan(
            TableName=self.ecsTable,
            AttributesToGet=[
                'ecsArn','region', 'servicename', 'clusterArn' , 'desiredCount'
            ],
            Limit=999)
        items = response.get("Items",[])
        clusterMap = {}
        for item in items:
            region = item['region']['S']
            clusterARN = item["clusterArn"]['S']
            serviceArn = item["ecsArn"]['S']
            sname = item["servicename"]['S']
            if region == self.region:
                desiredCount = int(item["desiredCount"]['N'])
                self.logger.info(f"restoring state: cluster Arn: {clusterARN}, Service Name {sname}--> desired Count {desiredCount}")
                if clusterARN not in clusterMap:
                    clusterMap[clusterARN] = []

                clusterMap[clusterARN].append([serviceArn, sname, desiredCount])
            else:
                self.logger.info(f"loading data Ignoring region {region} ")

        return clusterMap


    """
    Takes a cluster map and sets the desired count for all the services to the value in the map
    This will cause a scaling value
    There is an override value that will set all listed serviced to the override value. used if to set them all to zero
    The clustermap has format:  a MAP of clusters --- [ [Service Arns, service Name, desired state]]
    Returns Boolean if all changes were made ok to the all the services in the cluster map.
    """
    def setState(self,clusterMap, overrideDesiredCount=None):
        passed = True

        self.logger.info(f"----------Setting the State of the cluster map: overrideDesiredCount {overrideDesiredCount}---------- \n {clusterMap} \n------------------------")
        for cluster in clusterMap:
            self.logger.info(f"Setting state for cluster {cluster}")
            serviceList = clusterMap[cluster]
            for service in serviceList:
                serArn = "none"

                try:
                    serArn = service[0]
                    sername = service[1]

                    if overrideDesiredCount is None:
                        desiredCount = service[2]
                    else:
                        desiredCount = overrideDesiredCount

                    self.logger.info(f"Setting desired count level to {desiredCount} for cluster {cluster}, service Name {sername}")

                    response = self.client.update_service(
                        cluster=cluster,
                        service=serArn,
                        desiredCount=desiredCount)
                except Exception as e:
                    self.logger.error(f"Failed to set the service ARN {serArn} for cluster {cluster} to the desired state level")
                    self.logger.exception(e)
                    passed = False

        return passed




    """
    Get the Services that have an enabled DEVDAY TAG. This service will search across all clusters in the given region
    Returns a MAP[ClusterARN] = [ list of Service ARNS] or []
    """
    def findServices(self):
        clusterList = []
        try:
            response = self.client.list_clusters()
            nextToken = "A"
            # iterate through the clusters with pagination - just incase there are many
            while nextToken is not None:
                nextToken = response.get(nextToken)
                self.logger.debug(f"cluster reponse> {response}")
                cl = response.get('clusterArns',[])
                clusterList = clusterList + cl

                if nextToken is not None:
                    response = self.client.list_clusters(nextToken=nextToken)
        except Exception as e:
            self.logger.warning(f"could not access the clusters for region {self.region}")
            self.enabledServices={}
            return self.enabledServices

        # for each cluster get the list of the services
        for cluster in clusterList:
            self.logger.info(f"Examining ECS Cluster {cluster}")
            self.enabledServices[cluster]=[]
            response = self.client.list_services(
                cluster=cluster,
                maxResults=100
            )
            serviceArnList = response.get("serviceArns")
            for serviceArn in serviceArnList:
                self.logger.info(f"----- Looking at Service {serviceArn}")
                if serviceArn is not None and self._checkforTag(serviceArn):
                    self.enabledServices[cluster].append(serviceArn)



        return self.enabledServices
