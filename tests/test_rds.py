from rdsController import rdsController

import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_rds(unittest.TestCase):



    def test_init(self):
        rbs = rdsController(searchKey=SEARCHTAG,region=REGION)
        map = rbs.findResourcesForRDS(True)
        logger.info(f"RDS Instances Map {map}")

        instances = map[rbs.INSTANCE]
        count =len(instances)
        self.assertEqual(count,1,'There should be 1 tagged RDS instance')

        clusters = map[rbs.CLUSTER]
        count = len(clusters)
        self.assertEqual(count, 1, 'There should be 1 tagged RDS cluster')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()