from ec2Controller import ec2Controller

import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_ec2Controller(unittest.TestCase):



    def test_findServices(self):

        ec2  = ec2Controller(REGION, SEARCHTAG)

        serviceMAp = ec2.findServices()
        logger.info(f"Enabled Ec2 Services  {serviceMAp}")


    def test_correctBehaviour(self):
        logger.info("------------ TEST CorrectBehaviour ----------------")
        ec2 = ec2Controller(REGION, SEARCHTAG)

        serviceMAp = ec2.findServices(running=False)
        ec2.correctShutDownBehaviour(serviceMAp)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()