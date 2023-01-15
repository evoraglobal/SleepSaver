from ecsController import ecsController
from ec2Controller import ec2Controller

import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_stopDayEvent(unittest.TestCase):



    def test_stop_ecs(self):
        logger.info("-----Testing stop day event method FOR ECS------")

        ecs = ecsController(REGION, SEARCHTAG)
        result= ecs.stopDayEvent()
        self.assertTrue(result, msg="Stop Day Event didnt work for ECS")

    def test_stop_ec2(self):
        logger.info("-----Testing stop day event method FOR EC2------")

        ecs = ec2Controller(REGION, SEARCHTAG)
        result = ecs.stopDayEvent()
        self.assertTrue(result, msg="Stop Day Event didnt work for EC2")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()