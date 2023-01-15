from ecsController import ecsController
from ec2Controller import ec2Controller
import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_startDayEvent(unittest.TestCase):

    def test_start_ecs(self):
        logger.info("-----Testing start day event method ECS------")

        ecs = ecsController(REGION, SEARCHTAG)
        result = ecs.startDayEvent()
        self.assertTrue(result, msg="Start Day Event didnt work for ecs")

    def test_start_ec2(self):
        logger.info("-----Testing start day event method EC2------")

        ec2 = ec2Controller(REGION, SEARCHTAG)
        result = ec2.startDayEvent()
        self.assertTrue(result, msg="Start Day Event didnt work for ec2")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()