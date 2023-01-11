from ecsController import ecsContoller
import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_startDayEvent(unittest.TestCase):

    def test_start(self):
        logger.info("-----Testing start day event method------")

        ecs = ecsContoller(REGION, SEARCHTAG)
        result = ecs.startDayEvent()
        self.assertTrue(result, msg="Start Day Event didnt work")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()