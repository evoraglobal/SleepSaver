from ecsController import ecsContoller
import unittest
import logging

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'

class test_deleteState(unittest.TestCase):



    def test_delete(self):
        logger.info("-----Testing delete State method------")

        ecs = ecsContoller(REGION, SEARCHTAG)
        clustermap  =ecs.loadState()
        orig = len(clustermap)
        self.assertTrue(orig>0, msg="database should not have been empty")

        logger.info(f"******LOADED MAP > {clustermap} ")
        ecs._deleteState(clustermap)
        nomap = ecs.loadState()
        items = len(nomap)
        self.assertEqual(items,0,msg="there should be no items in the database")

        logger.info("restoring the database state")
        ecs.storeState(clustermap)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger =logging.getLogger()
    unittest.main()