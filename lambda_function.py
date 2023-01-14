import json
import os
import logging
from ResourceFinder import ResourceFinder


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

# Comma separated list of regions to monitor
regionstr = env.get(REGIONLISTENV, "eu-west-2,eu-west-1")
regionlist = regionstr.split(',')

SEARCHTAG = "DEVDAYTERM"

START = "START"
STOP = "STOP"

EVENTLIST = [ START , STOP]


searchTerm = env.get(SEARCHTAG, "DEVDAY")

def lambda_handler(event, context):

    ev = event["event"]
    if ev not in EVENTLIST:
        logger.error(f"Unknown Action event: {ev}, was expecting something in {EVENTLIST}")
        return {
            'statusCode': 406,
            'body': json.dumps(f'unexpected event passed as parameter {ev}')
        }


    rf = ResourceFinder(searchTerm)
    for region in regionlist:
        region = region.strip()
        logger.info(f"-----Searching for resources {region}-----------")
        controlledResources = rf.findResourcesFor(region)
        if ev == START:
            rf.startResources(region)
        else:
            rf.stopResources(region)

        logger.info(f">>>>>>> Finished {ev} Operation For Following Resources<<<<<<<<")
        for crType in controlledResources:
            arnList = controlledResources[crType]
            for arn in arnList:
                logger.info(f"Resource Type {crType} - ARN {arn}")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
