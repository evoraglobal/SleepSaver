from ecsController import ecsContoller
import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_stopDayEvent(unittest.TestCase):



    def test_stop(self):
        logger.info("-----Testing stop day event method------")

        ecs = ecsContoller(REGION, SEARCHTAG)
        result= ecs.stopDayEvent()
        self.assertTrue(result, msg="Stop Day Event didnt work")



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()