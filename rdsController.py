""""
Controls RDS Services: Both individual instances and also CLusters
"""
import boto3
import logging
import os

"""
RDS controller: finds RDS instances / clusters that have a devday tag, has the ability to stop, start the asset for the working day
"""

class rdsController:

    STOPBEHAVIOUR = 'stop'

    INSTANCE  = "INSTANCE"
    CLUSTER = "CLUSTER"

    STOPPABLESTATUS = ["available","rebooting","starting","storage-full"]
    STARTABLESTATUS = ["stopped"]
    STORAGETYPE = 'StorageType'
    AURORA = 'aurora'

    def __init__(self, region, searchKey ):
        self.region = region
        self.client = boto3.client('rds', region_name= region)
        self.searchTag = searchKey.lower()
        self.logger = logging.getLogger(__name__)
        self.enabledServices = {}
        env = os.environ
        self.rdsMap = {}
        self.rdsMap[self.INSTANCE] ={}
        self.rdsMap[self.CLUSTER] = {}






    """
    Main entry point to be called from ResourceFinder - finds all RDS Services (instances and clusters) that have been tagged
    :parameter running : filters only running or not running instances into the results map
    Returns a  Map [INSTANCE | CLUSTER][instance id] :{ "id" : dbid,
                    "name" : name,
                    "engine" : engine,
                    "status" : status,
                    "maz" : maz,
                    "arn" : dbarn}
    """
    def findResourcesForRDS(self, running):

        self.rdsMap={}
        instanceMap  = self._findInstances(running)

        if len(instanceMap)> 0:
            self.rdsMap[self.INSTANCE]= instanceMap


        clusterMap  = self._findClusters(running)
        if len(clusterMap) > 0:
            self.rdsMap[self.CLUSTER] = clusterMap

        return self.rdsMap

    """
       Specialised for DBInstances (not MultiAZ) - finds all RDS that have been tagged
       :parameter running : filters only running or not running instances into the results map
       Returns a  Map [instance id] :{ "id" : dbid,
                       "name" : name,
                       "engine" : engine,
                       "status" : status,
                       "maz" : maz,
                       "arn" : dbarn}
       """
    def _findInstances(self,running):

        # find the standalone instances
        instanceMap = {}
        response = self.client.describe_db_instances()
        marker = "A"
        while marker is not None:

            marker = response.get("Marker", None)

            instanceList = response.get("DBInstances",[])
            for instance in instanceList:
                self.logger.debug(f"RDS Instance = {instance}")
                dbid = instance["DBInstanceIdentifier"]
                dbarn   = instance["DBInstanceArn"]
                maz  = instance["MultiAZ"]
                st = instance[self.STORAGETYPE]
                status = instance["DBInstanceStatus"].lower()
                if "DBName" in instance:
                    name = instance["DBName"]
                else:
                    name = dbid
                engine = instance["Engine"]
                tagList = instance.get("TagList",[])
                rdsDict = {
                    "id" : dbid,
                    "name" : name,
                    "engine" : engine,
                    "status" : status,
                    "maz" : maz,
                    "arn" : dbarn

                }
                # Aurora type works in a cluster so cannot be dealt with at an instance level
                if self._checkforTag(tagList) and not st==self.AURORA :
                    self.logger.info(f"Found tagged RDS: {rdsDict}")
                    if not maz:
                        # checks to see if the RDS is in the correct status for the action
                        if (running and status in self.STOPPABLESTATUS) or ((not running) and status in self.STARTABLESTATUS) :
                            instanceMap[dbid]=rdsDict
                        else:
                            self.logger.info(f"instance is not in the correct status (current status {status}) - ignoring")
                    else:
                        self.logger.info("RDS is Multi-AZ therefore only the cluster and not instance can be stopped/started - ignoring")
                else:
                    self.logger.info(f"Found untagged RDS or an Aurora instance so ignoring: {rdsDict}")

            if marker is not None:
                response = self.client.describe_db_instances(Marker=marker)



        return instanceMap

    """
          Specialised for DBClusters ( MultiAZ) - finds all RDS that have been tagged
          :parameter running : filters only running or not running instances into the results map
          Returns a  Map [instance id] :{ "id" : dbid,
                          "name" : name,
                          "engine" : engine,
                          "status" : status,
                          "maz" : maz,
                          "arn" : dbarn}
    """

    def _findClusters(self, running):

        # find the standalone instances
        clusterMap = {}
        response = self.client.describe_db_clusters()
        marker = "A"
        while marker is not None:

            marker = response.get("Marker", None)

            clusterList = response.get("DBClusters", [])
            for cluster in clusterList:
                self.logger.debug(f"Clusters >> {cluster}")
                serverless = False
                if "Capacity" in cluster or "ServerlessV2ScalingConfiguration" in cluster:
                    serverless = True
                    self.logger.info(f"RDS cluster {cluster} is Serverless - so ignoring")
                else:

                    dbid = cluster["DBClusterIdentifier"]
                    dbarn = cluster["DBClusterArn"]
                    maz = cluster["MultiAZ"]
                    status = cluster["Status"]
                    if "DatabaseName"  in cluster:
                        name = cluster["DatabaseName"]
                    else:
                        name = dbid
                    engine = cluster["Engine"]
                    tagList = cluster.get("TagList", [])
                    rdsDict = {
                        "id": dbid,
                        "name": name,
                        "engine": engine,
                        "status": status,
                        "maz": maz,
                        "arn": dbarn

                    }
                    if self._checkforTag(tagList):
                        self.logger.info(f"Found tagged RDS CLUSTER: {rdsDict}")

                        # checks to see if the RDS is in the correct status for the action
                        if (running and status in self.STOPPABLESTATUS) or (
                                (not running) and status in self.STARTABLESTATUS):
                            clusterMap[dbid] = rdsDict
                        else:
                            self.logger.info(f"cluster is not in the correct status (current status {status}) - ignoring")

                    else:
                        self.logger.info(f"Found untagged RDS cluster so ignoring: {rdsDict}")

            if marker is not None:
                response = self.client.describe_db_clusters(Marker=marker)

        return clusterMap


    """
    Main entry point to signal a STOP of developer day event
    All tagged and running EC2 servers will be stopped
    """
    def stopDayEvent(self):


        rdsMap = self.findResourcesForRDS(running=True)  # Find all those that are currently running

        if len(rdsMap) == 0:
            self.logger.info(
                "There are currently no started RDS instances that are tagged - they are either running or dont exist")
            return True

        instanceMap = rdsMap.get(self.INSTANCE, [])
        clusterMap = rdsMap.get(self.CLUSTER, [])

        instresult = self._stopIntances(instanceMap)
        clusresult = self._stopClusters(clusterMap)
        totalResult = instresult and clusresult

        return totalResult

    """
    Main entry point to signal a START of developer day event
    Finds all tagged Ec2 servers that are currently stopped
    """
    def startDayEvent(self):

        rdsMap = self.findResourcesForRDS(running=False)  # Find all those that are currently stopped

        if len(rdsMap) == 0:
            self.logger.info(
                "There are currently no stopped RDS instances that are tagged - they are either running or dont exist")
            return True

        instanceMap  = rdsMap.get(self.INSTANCE,[])
        clusterMap  = rdsMap.get(self.CLUSTER,[])


        instresult = self._startIntances(instanceMap)
        clusresult = self._startClusters(clusterMap)
        totalResult = instresult and clusresult

        return totalResult

    """
        Starts a list of instances
        returns True if all Databases started without an exception
    """
    def _startIntances(self, instanceMap):

        totalResult = True

        for rdsinstance in instanceMap:
            rdsDict = instanceMap[rdsinstance]
            dbid = rdsDict["id"]

            try:
                response = self.client.start_db_instance(
                    DBInstanceIdentifier=dbid)
                self.logger.info(f"Starting RDS instance {dbid}")

            except Exception as e:
                self.logger.error(f"Could not start  RDS instance: {dbid} ")
                self.logger.exception(e)
                totalResult = False

        return totalResult




    """
     Stops a list of instances
     returns True if all Databases stopped without an exception
    """
    def _stopIntances(self,instanceMap):

        totalResult = True

        for rdsinstance in instanceMap:
            rdsDict = instanceMap[rdsinstance]
            dbid = rdsDict["id"]

            try:
                response = self.client.stop_db_instance(
                                            DBInstanceIdentifier=dbid)
                self.logger.info(f"Stopping RDS instance {dbid}")

            except Exception as e:
                self.logger.error(f"Could not stop  RDS instance: {dbid} ")
                self.logger.exception(e)
                totalResult = False

        return totalResult

    """
        Stops a list of instances
        returns True if all Databases stopped without an exception
        """

    def _stopClusters(self, clusterMap):

        totalResult = True

        for cluster in clusterMap:
            clustDict = clusterMap[cluster]
            dbid = clustDict["id"]

            try:
                response = self.client.stop_db_cluster(
                    DBClusterIdentifier=dbid)
                self.logger.info(f"Stopping RDS cluster {dbid}")

            except Exception as e:
                self.logger.error(f"Could not stop  RDS cluster: {dbid} ")
                self.logger.exception(e)
                totalResult = False

        return totalResult

    def _startClusters(self, clusterMap):

        totalResult = True

        for cluster in clusterMap:
            clustDict = clusterMap[cluster]
            dbid = clustDict["id"]

            try:
                response = self.client.start_db_cluster(
                    DBClusterIdentifier=dbid)
                self.logger.info(f"Starting RDS cluster {dbid}")

            except Exception as e:
                self.logger.error(f"Could not start  RDS cluster: {dbid} ")
                self.logger.exception(e)
                totalResult = False

        return totalResult

    """
    Checks the TagList from RDS for the special searchTag - and see if the Tag is set to TRUE
    return True or False
    """
    def _checkforTag(self,tagList):
        self.logger.debug(f"Tags are {tagList}")
        for tag in tagList:
            key = tag.get('Key')
            if key is not None:
                value=tag['Value'].lower()
                if key.lower() == self.searchTag and value=='true':
                    return True

        return False


