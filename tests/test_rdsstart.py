from rdsController import rdsController

import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_rdsstart(unittest.TestCase):



    def test_start(self):
        rbs = rdsController(searchKey=SEARCHTAG,region=REGION)
        result = rbs.startDayEvent()
        self.assertTrue(result,"Expecting all servers to start")



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()