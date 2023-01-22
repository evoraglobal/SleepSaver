import json
import os
import logging
from ResourceFinder import ResourceFinder
import boto3


env = os.environ
REGIONLISTENV = "REGIONLIST"


logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)20s() ] %(name)s - %(levelname)s - %(message)s')
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)



SEARCHTAG = "DEVDAYTERM"

START = "START"
STOP = "STOP"

EVENTLIST = [ START , STOP]

def getRegions():
    # find the valid regions
    lregionlist = []

    ec2 = boto3.client("ec2", "eu-west-2")
    response = ec2.describe_regions(AllRegions=False, Filters=[{
        "Name": "opt-in-status",
        "Values": ["opt-in-not-required", "opted-in"]
    }])
    regionlong = response['Regions']
    for region in regionlong:
        regionName = region['RegionName']
        lregionlist.append(regionName)
    return lregionlist




searchTerm = env.get(SEARCHTAG, "DEVDAY")
specifiedRegions = env.get(REGIONLISTENV,None)


# check to see if the precise regions have been specified - if not set then all regions will be processed

if specifiedRegions is None:
    regionlist = getRegions()
else:
    regionlist = specifiedRegions.split(',')



def lambda_handler(event, context):

    ev = event["event"]
    if ev not in EVENTLIST:
        logger.error(f"Unknown Action event: {ev}, was expecting something in {EVENTLIST}")
        return {
            'statusCode': 406,
            'body': json.dumps(f'unexpected event passed as parameter {ev}')
        }


    logger.info(f"Available regions are {regionlist}")

    rf = ResourceFinder(searchTerm)


    for region in regionlist:
        region = region.strip()
        logger.info(f"-----Searching for resources in region: {region} -----------")

        if ev == START:
            rf.startResources(region)
        else:
            rf.stopResources(region)

        logger.info(f">>>>>>> Finished {ev} Operation For Following Resources for region {region}<<<<<<<<")

    return {
        'statusCode': 200,
        'body': json.dumps('All ok')
    }
