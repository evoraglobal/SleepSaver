import boto3
import logging

class cloudWatchAlarmController:
    def __init__(self, region, searchTag):
        self.region = region
        self.searchTag = searchTag.lower()
        self.client = boto3.client('cloudwatch', region_name=region)
        self.logger = logging.getLogger(__name__)

    """
    Main entry point to find all CloudWatch alarms with the specified tag
    Returns a list of alarm names
    """
    def findAlarms(self):
        paginator = self.client.get_paginator('describe_alarms')
        alarm_names = []

        for page in paginator.paginate():
            for alarm in page['MetricAlarms']:
                alarm_arn = alarm['AlarmArn']
                if self._check_for_tag(alarm_arn):
                    alarm_names.append(alarm['AlarmName'])

        return alarm_names

    """
    Disables all alarms with the specified tag
    """
    def disableAlarms(self):
        alarm_names = self.findAlarms()

        if not alarm_names:
            self.logger.info("No alarms found with the specified tag.")
            return True

        response = self.client.disable_alarm_actions(AlarmNames=alarm_names)
        self.logger.info(f"Disabled alarms: {alarm_names}")
        return response

    """
    Enables all alarms with the specified tag
    """
    def enableAlarms(self):
        alarm_names = self.findAlarms()

        if not alarm_names:
            self.logger.info("No alarms found with the specified tag.")
            return True

        response = self.client.enable_alarm_actions(AlarmNames=alarm_names)
        self.logger.info(f"Enabled alarms: {alarm_names}")
        return response

    """
    Checks the Alarm ARN for the specified tag
    Returns True if the tag is found, False otherwise
    """
    def _check_for_tag(self, alarm_arn):
        response = self.client.list_tags_for_resource(ResourceARN=alarm_arn)
        tags = response.get('Tags', [])

        for tag in tags:
            key = tag['Key'].lower()
            value = tag['Value'].lower()
            if key == self.searchTag and value == 'true':
                return True

        return False
