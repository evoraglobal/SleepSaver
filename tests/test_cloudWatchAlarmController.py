from cloudWatchAlarmController import cloudWatchAlarmController

import unittest
import logging
from moto import mock_cloudwatch
import boto3
from cloudWatchAlarmController import CloudWatchAlarmController

REGION = 'eu-west-2'
SEARCHTAG = 'DEVDAY'
class TestCloudWatchAlarmController(unittest.TestCase):

    @mock_cloudwatch
    def setUp(self):
        self.region = REGION
        self.search_tag = SEARCHTAG
        self.tag_value = "True"

        # Initialize boto3 client with mocked CloudWatch
        self.cloudwatch = boto3.client('cloudwatch', region_name=self.region)

        # Create a mock alarm
        self.cloudwatch.put_metric_alarm(
            AlarmName='TestAlarm',
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=1,
            MetricName='CPUUtilization',
            Namespace='AWS/EC2',
            Period=60,
            Threshold=70.0,
            ActionsEnabled=True,
            AlarmActions=[],
            Tags=[
                {
                    'Key': self.search_tag,
                    'Value': self.tag_value
                }
            ]
        )

        # Initialize CloudWatchAlarmController
        self.alarm_controller = CloudWatchAlarmController(self.region, self.search_tag)

    @mock_cloudwatch
    def test_init(self):
        # Check if the controller initializes correctly
        self.assertIsInstance(self.alarm_controller, CloudWatchAlarmController)
        self.assertEqual(self.alarm_controller.region, self.region)
        self.assertEqual(self.alarm_controller.search_tag, self.search_tag)

    @mock_cloudwatch
    def test_disable_alarms(self):
        # Run disable alarms method
        result = self.alarm_controller.disable_alarms()

        # Check if alarms are disabled
        alarms = self.cloudwatch.describe_alarms(AlarmNames=['TestAlarm'])['MetricAlarms']
        self.assertFalse(alarms[0]['ActionsEnabled'])
        self.assertTrue(result)

    @mock_cloudwatch
    def test_enable_alarms(self):
        # First disable the alarms
        self.alarm_controller.disable_alarms()

        # Then enable the alarms
        result = self.alarm_controller.enable_alarms()

        # Check if alarms are enabled
        alarms = self.cloudwatch.describe_alarms(AlarmNames=['TestAlarm'])['MetricAlarms']
        self.assertTrue(alarms[0]['ActionsEnabled'])
        self.assertTrue(result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    unittest.main()
