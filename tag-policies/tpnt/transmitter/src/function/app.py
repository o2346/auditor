from schema.aws.s3.awsapicallviacloudtrail import Marshaller
from schema.aws.s3.awsapicallviacloudtrail import AWSEvent
from schema.aws.s3.awsapicallviacloudtrail import AWSAPICallViaCloudTrail

import os
import io
import sys
import boto3
import json
import csv
import urllib
import re
import functools

import urllib3
http = urllib3.PoolManager()

s3 = boto3.client('s3')

# return only items marked as noncompliant
def filter_noncompliants(csv):
    #https://www.geeksforgeeks.org/filter-in-python/
    result = filter(lambda x: x['ComplianceStatus'] == 'false', csv)
    #print(len(list(result)))
    return list(result)

#Obtain CSV accordingly, and parse it(csv named column in 1st row) into dict data
def get_dictdata(event):
    parent = event['Records'][0]['s3']['bucket']['name']
    #https://stackoverflow.com/questions/9748678/which-is-the-best-way-to-check-for-the-existence-of-an-attribute
    #if hasattr(os.environ, 'LAMBDA_TASK_ROOT'):
    #    #at local invoking
    #    current_dir = os.path.dirname(os.path.abspath(__file__))
    #    local_csvpath = os.path.join(current_dir,'localmoc','report.csv')
    #else:
    #    #at unit testing
    #    local_csvpath = os.path.join(os.environ['src'],'transmitter','localmoc','report.csv')

    if parent == 'localmoc':
        #most in case of development
        #https://stackoverflow.com/questions/30218802/get-parent-of-current-directory-from-python-script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_csvpath = os.path.join(current_dir,'localmoc','report.csv')
        print(local_csvpath)
        with open(local_csvpath, newline='') as csvfile:
            #https://docs.python.org/3/library/csv.html#reader-objects
            reader = csv.DictReader(csvfile, delimiter=',')
            ret = [dict(d) for d in reader]
            #print(len([dict(d) for d in reader]))

            #https://stackoverflow.com/questions/47115041/read-from-csv-into-a-list-with-dictreader
    else:
        #in case of production
        #str(os.environ['LAMBDA_TASK_ROOT'] + "/function/summarytemplates/" + configRuleName + '.json')
        #https://stackoverflow.com/questions/42312196/how-do-i-read-a-csv-stored-in-s3-with-csv-dictreader
        #https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-deployment-pkg.html#with-s3-example-deployment-pkg-python
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        #key = event['Records'][0]['s3']['object']['key'].encode('utf8')
        try:
            response = s3.get_object(Bucket=parent, Key=key)
            # for python 3 you need to decode the incoming bytes:
            lines = response['Body'].read().decode('utf-8').split()
            reader = csv.DictReader(lines)
            ret = [dict(d) for d in reader]
            # now iterate over those lines
            #for row in csv.DictReader(lines):
                # here you get a sequence of dicts
                # do whatever you want with each line here
                #print(row)
            #print("CONTENT TYPE: " + response['ContentType'])
            #return response['ContentType']
        except Exception as e:
            print(e)
            print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
            raise e
    return ret

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
    detail:AWSAPICallViaCloudTrail = awsEvent.detail

    #Execute business logic

    #print(json.dumps(event))
    #print(os.environ['SENDTO'])
    noncompliantsCount = len(filter_noncompliants(get_dictdata(event)))
    print(noncompliantsCount)

    if noncompliantsCount == 0:
        #Make updates to event payload, if desired
        awsEvent.detail_type = "Successful. 0 Non-compliant resources found, Congratulations. Abort"
        #Return event for further processing
        return Marshaller.marshall(awsEvent)

    noncompliants = filter_noncompliants(get_dictdata(event))
    #https://stackoverflow.com/questions/61466934/convert-list-of-dict-to-csv-string-using-dict-keys
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=noncompliants[0].keys())
    writer.writeheader()
    writer.writerows(noncompliants)

    print(os.environ['BUCKET1'])
    print(os.environ['BUCKET2'])
    #print(os.environ['testing'])

    if os.environ.get('testing') == 'True':
        awsEvent.detail_type = "Successful. Ommiting further tasks since it's merely for unit testing"
        return Marshaller.marshall(awsEvent)
    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_object
    response = s3.put_object(
        Body=output.getvalue(), #https://dev.classmethod.jp/articles/upload-json-directry-to-s3-with-python-boto3/
        Bucket=os.environ['BUCKET2'],
        Key='noncompliants.csv'
    )

    print(response)

    #
    #Generate and Send message
    #
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_location = os.path.join(current_dir,'message','template.json')
    print(template_location)
    with open(template_location, 'r') as messate_template_file:
        message_template = json.dumps(json.load(messate_template_file))

    noncompliantsReportMapping = [
        message_template,
        [ 'value.S3Bucket', os.environ['BUCKET2'] ],
        [ 'value.Totalling', noncompliantsCount ],
        [ 'value.S3Object', 'noncompliants.csv' ]
    ]

    message_json = json.loads(functools.reduce(lambda a,b :re.sub(b[0], str(b[1]), a) ,noncompliantsReportMapping))
    encoded_msg = json.dumps(message_json).encode('utf-8')
    response = http.request('POST',os.environ['SENDTO'], body=encoded_msg)
    #print(output.getvalue())
    #print(os.environ['BUCKET1'])
    #print(os.environ['BUCKET2'])
    print(str(response))
    print(os.environ['SENDTO'])

    #Make updates to event payload, if desired
    awsEvent.detail_type = "Successful. Non-compliant resources found and Message sent"
    #Return event for further processing
    return Marshaller.marshall(awsEvent)
