from asgController import asgController

import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_asgDB(unittest.TestCase):



    def test_loadState(self):

        asg  = asgController(REGION, SEARCHTAG)

        serviceMAp = asg._loadState()
        logger.info(f"Enabled ASG:  {serviceMAp}")

    def test_DeleteState(self):
        asg = asgController(REGION, SEARCHTAG)

        map1 = asg._loadState()
        logger.info(f"Loaded State map:  {map1}")
        logger.info("Deleteing state in db")
        asg._deleteState(map1)
        map2 = asg._loadState()
        self.assertEqual(len(map2),0,"There shouldnt be any records in this region Db")
        logger.info("Restoring state back into the DB")
        asg._storeState(map1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()