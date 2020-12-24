from schema.aws.events.scheduledjson import Marshaller
from schema.aws.events.scheduledjson import AWSEvent
from schema.aws.events.scheduledjson import ScheduledEvent

import json
import os

import urllib3 
import json
http = urllib3.PoolManager() 

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

    #https://stackoverflow.com/a/39550486
    with open(os.environ['LAMBDA_TASK_ROOT'] + "/cavt/slack-message-template-required-tags.json") as json_file:
        data = json.load(json_file)

    url = "https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    msg = data
    encoded_msg = json.dumps(msg).encode('utf-8')
    resp = http.request('POST',url, body=encoded_msg)
    #resptxt = json.dumps(resp)

    #Make updates to event payload, if desired
    awsEvent.detail_type = "HelloWorldFunction updated event of " + awsEvent.detail_type + json.dumps(data);

    #Return event for further processing
    return Marshaller.marshall(awsEvent)
