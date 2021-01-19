from schema.aws.events.scheduledjson import Marshaller
from schema.aws.events.scheduledjson import AWSEvent
from schema.aws.events.scheduledjson import ScheduledEvent

import json
import os
import sys
import boto3

client = boto3.client('resourcegroupstaggingapi')

def lambda_handler(event, context):
    """Sample Lambda function reacting to EventBridge events

    Parameters
    ----------
    event: dict, required
        Event Bridge Events Format

        Event doc: https://docs.aws.amazon.com/eventbridge/latest/userguide/event-types.html

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
        The same input event file
    """

    #Deserialize event into strongly typed object
    awsEvent:AWSEvent = Marshaller.unmarshall(event, AWSEvent)
    detail:ScheduledEvent = awsEvent.detail

    #Execute business logic

    #Make updates to event payload, if desired
    awsEvent.detail_type = str(awsEvent);
    print(os.environ['Bucket'])
    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/resourcegroupstaggingapi.html#ResourceGroupsTaggingAPI.Client.start_report_creation
    try:
        response = client.start_report_creation(
            S3Bucket=os.environ['Bucket']
        )
        print(response)
    except:
        print(str(sys.exc_info()))

    #consider following in order to support account names mapping for human friendly
    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/organizations.html#Organizations.Client.list_accounts

    #TODO:enable bucket object lifecycle(scheduled auto deletion) for cost saving
    #Generated CSVs may not be necessary forever

    #Return event for further processing
    return Marshaller.marshall(awsEvent)
