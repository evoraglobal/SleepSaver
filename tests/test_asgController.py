from asgController import asgController

import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_asgController(unittest.TestCase):



    def test_findServices(self):

        asg  = asgController(REGION, SEARCHTAG)

        serviceMAp = asg.findResourcesForASG()
        logger.info(f"Enabled ASG:  {serviceMAp}")


    def test_stopDay(self):
        asg = asgController(REGION, SEARCHTAG)

        result = asg.stopDayEvent()
        self.assertTrue(result,"Not all ASG could be silenced")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()