from rdsController import rdsController

import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_rdsstop(unittest.TestCase):



    def test_stop(self):
        rbs = rdsController(searchKey=SEARCHTAG,region=REGION)
        result = rbs.stopDayEvent()
        self.assertTrue(result,"Expecting all servers to stop")



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()