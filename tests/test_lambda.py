import lambda_function
import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_lambda(unittest.TestCase):



    def test_lambda(self):
        logger.info("-----Testing stop day event method------")
        ev  = {"event" : "STOP"}
        lambda_function.lambda_handler(ev,None)
        logger.info("-----Testing Start day event method------")
        ev  = {"event" : "START"}
        lambda_function.lambda_handler(ev,None)




if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()