from elb import elb


import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_elb2(unittest.TestCase):



    def test_init(self):

        elbins = elb(SEARCHTAG,REGION)

        self.assertTrue(elbins.isEnvironmentTagged('e-md57fpmpuh'),"elastic beanstalk should have been tagged")


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)20s() ] %(name)s - %(levelname)s - %(message)s')
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)


    unittest.main()