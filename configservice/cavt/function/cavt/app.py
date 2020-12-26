from schema.aws.events.scheduledjson import Marshaller
from schema.aws.events.scheduledjson import AWSEvent
from schema.aws.events.scheduledjson import ScheduledEvent

import json
import os

#https://aws.amazon.com/premiumsupport/knowledge-center/sns-lambda-webhooks-chime-slack-teams/
#https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents.html
import urllib3 
import json
http = urllib3.PoolManager() 

import boto3
client = boto3.client('config')

import glob

import functools
import re

#handle NextToken, or you would have incomplete results
def select_aggregate_resource_config(Expression, ConfigurationAggregatorName, NextToken=None, current={'Results': []}):

    kwargs = {'NextToken': NextToken} if NextToken else {}

    try:
        page = client.select_aggregate_resource_config(
            Expression=Expression,
            ConfigurationAggregatorName=ConfigurationAggregatorName,
            **kwargs
        )
        current.get('Results').extend(page.get('Results'))
    except:
        print(sys.exc_info())
        print('Error: something is wrong. Result may possibly be incomplete')
        return current

    if page.get('NextToken') is None:
        return current
    else:
        return select_aggregate_resource_config(Expression, ConfigurationAggregatorName, page.get('NextToken'), current)

def audit(context):
    nonconpliants = []
    with open(context, 'r') as json_file:
        json_text = json.dumps(json.load(json_file))
        #https://api.slack.com/messaging/webhooks
        #https://developers.mattermost.com/integrate/incoming-webhooks/
        #http://ykng0.hatenablog.com/entry/2016/12/25/225424
        #https://gist.github.com/rantav/c096294f6f35c45155b4
        #https://slack.dev/python-slackclient/basic_usage.html

    contextObject = json.loads(json_text)
    configRuleName = contextObject['attachments'][0]['props']['rvt']['configservice']['rule']['configRuleName']
    print(configRuleName)

    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/config.html#ConfigService.Client.select_aggregate_resource_config
    response = select_aggregate_resource_config(
        #https://github.com/awslabs/aws-config-resource-schema/blob/master/config/properties/AWS.properties.json
        Expression='''
            SELECT
              accountId,
              awsRegion,
              configuration.targetResourceId,
              configuration.targetResourceType,
              configuration.complianceType,
              configuration.configRuleList
            WHERE
              configuration.complianceType = 'NON_COMPLIANT'
              AND configuration.configRuleList.configRuleName = '{0}'
        '''.format(configRuleName),
        ConfigurationAggregatorName='ConfigurationAggregator',
    )

    for resultText in response['Results']:
        result = json.loads(resultText)
        #print(json.dumps(result,indent=2))
        # prepare template
        contextTemplateObject = [
            json_text,
            [ 'accountId', result['accountId'] ],
            [ 'awsRegion', result['awsRegion'] ],
            [ 'configuration.targetResourceId', result['configuration']['targetResourceId'] ],
            [ 'configuration.targetResourceType', result['configuration']['targetResourceType'] ],
            [ 'configuration.complianceType', result['configuration']['complianceType'] ]
            #[ 'configuration.configRuleList', result['configuration']['configRuleList'] ]
        ]
        item = json.loads(functools.reduce(lambda a,b :re.sub(b[0], b[1], a) ,contextTemplateObject))
        nonconpliants.append(item)
    #https://stackoverflow.com/a/39550486
    #result.append(json_text)
    return nonconpliants


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
    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/config.html#ConfigService.Client.select_aggregate_resource_config
    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/config.html#ConfigService.Client.get_aggregate_compliance_details_by_config_rule
    #response = client.get_aggregate_compliance_details_by_config_rule(
    #    ConfigurationAggregatorName='ConfigurationAggregator',
    #    ConfigRuleName='required-tags',
    #    AccountId='NNNNNNNNNNNN',
    #    AwsRegion='us-east-1',
    #    ComplianceType='NON_COMPLIANT'
    #)
    url = os.environ['SENDTO']
    nonconpliants = {}
    for (filename) in glob.glob(str(os.environ['LAMBDA_TASK_ROOT'] + "/cavt/rules/*.json")):
        audited = audit(filename)
        if len(audited) == 0:
            continue

        nonconpliants[filename]=audited
        for idx, val in enumerate(nonconpliants[filename]):
            encoded_msg = json.dumps(val).encode('utf-8')
            val['http_send_response'] = http.request('POST',url, body=encoded_msg)
        #nonconpliants[filename]['http_send_response'] = 'mocresponce'

    #usage example:
    #sam build && sam local invoke --parameter-overrides SendTo=YOUR_WEBHOOK_URL
    #msg = audit('hoge')
    #encoded_msg = json.dumps(msg).encode('utf-8')
    #resp = http.request('POST',url, body=encoded_msg)
    #resptxt = json.dumps(resp)

    #Make updates to event payload, if desired
    #awsEvent.detail_type = "HelloWorldFunction updated event of " + awsEvent.detail_type + str(os.environ['SENDTO']);
    #awsEvent.detail_type = msg
    #awsEvent.detail_type = nonconpliants
    #awsEvent.detail_type = str(nonconpliants)
    awsEvent.detail_type = ''
    #awsEvent.detail_type = json.dumps(response, indent=2)

    #Return event for further processing
    return Marshaller.marshall(awsEvent)
