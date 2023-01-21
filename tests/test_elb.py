from elb import elb

import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_elb(unittest.TestCase):



    def test_init(self):
        elbins = elb(searchKey=SEARCHTAG,region=REGION)
        count =len(elbins.taggedEnvironmentIDList)
        self.assertEqual(count,1,'There should be 1 tagged environment')

        correctID  ='e-md57fpmpuh'
        self.assertTrue(elbins.isEnvironmentTagged(correctID),"env was not correctly tagged")








if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()