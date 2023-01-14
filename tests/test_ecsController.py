from ecsController import ecsContoller
import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_ecsController(unittest.TestCase):



    def test_findServices(self):

        ecs  = ecsContoller(REGION, SEARCHTAG)

        serviceArns = ecs.findServices()
        logger.info(f"Enabled Service ARNS {serviceArns}")

    def test_getDesiredState(self):
        ecs = ecsContoller(REGION, SEARCHTAG)

        serviceArns = ecs.findServices()
        logger.info("---------About to get the Desired States ---------")
        resultMap = ecs.getDesiredState(serviceArns)
        logger.info(f"Current Desired States {resultMap}")

    def test_storeState(self):
        logger.info("-----Testing Store State method------")
        ecs = ecsContoller(REGION, SEARCHTAG)

        serviceArns = ecs.findServices()
        logger.info("---------About to get the Desired States ---------")
        resultMap = ecs.getDesiredState(serviceArns)
        logger.info(f"Current Desired States {resultMap}")
        logger.info("----------- ABOUT TO STORE--------")
        result = ecs.storeState(resultMap)
        self.assertTrue(resultMap,msg="The clustermap didnt store to the database")

    def test_loadState(self):
        logger.info("------Testing the load state method------")
        ecs = ecsContoller(REGION, SEARCHTAG)
        clustermap  =ecs.loadState()
        logger.info(f"******LOADED MAP > {clustermap} ")
        keys = list(clustermap.keys())
        nokeys = len(keys)
        self.assertTrue(nokeys>1,msg=" We didnt get the expected rows from the database")
        ecs = ecsContoller("us-east-2", SEARCHTAG)
        clustermap  =ecs.loadState()
        keys = list(clustermap.keys())
        nokeys = len(keys)
        self.assertTrue(nokeys == 0,msg= "we should not have been able to load anything for this region")

    def test_setState(self):
        logger.info("-----Aboout to Set the STATE for the cluster to 2 services")
        clustermap =  {'arn:aws:ecs:eu-west-2:307494535005:cluster/Cheddar2': [['arn:aws:ecs:eu-west-2:307494535005:service/Cheddar2/TestCon', 'TestCon', 2]], 'arn:aws:ecs:eu-west-2:307494535005:cluster/Cheddar4': [['arn:aws:ecs:eu-west-2:307494535005:service/Cheddar4/EnvTest', 'EnvTest', 2]]}
        ecs = ecsContoller(REGION, SEARCHTAG)
        result = ecs.setState(clustermap)
        self.assertTrue(result, msg="could not set the desired count on all servers")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()