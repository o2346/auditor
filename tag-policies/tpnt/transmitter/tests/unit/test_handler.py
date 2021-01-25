import pytest

from schema.aws.s3.awsapicallviacloudtrail import AWSEvent
from schema.aws.s3.awsapicallviacloudtrail import AWSAPICallViaCloudTrail
from schema.aws.s3.awsapicallviacloudtrail import Marshaller
from transmitter import app

import os
import sys
import boto3
import json
import csv

@pytest.fixture()
def eventBridgeEvent():
    """ Generates EventBridge Event"""

    return {
            "version":"0",
            "id":"7bf73129-1428-4cd3-a780-95db273d1602",
            "detail-type":"AWS API Call via CloudTrail",
            "source":"aws.s3",
            "account":"123456789012",
            "time":"2015-11-11T21:29:54Z",
            "region":"us-east-1",
            "resources":[
              "arn:aws:ec2:us-east-1:123456789012:instance/i-abcd1111"
            ],
            "detail":{
              "ADD-YOUR-FIELDS-HERE":""
            }
    }


def test_lambda_handler(eventBridgeEvent, mocker):
    os.environ['SENDTO'] = 'Jone Due'
    ret = app.lambda_handler(eventBridgeEvent, "")

    awsEventRet:AWSEvent = Marshaller.unmarshall(ret, AWSEvent)
    detailRet:AWSAPICallViaCloudTrail = awsEventRet.detail

    #assert awsEventRet.detail_type.startswith("HelloWorldFunction updated event of ")
    assert True

def test_filter_noncompliants(eventBridgeEvent, mocker):
#    for p in sys.path:
#        print(p)
#/home/o2/Documents/tagging-discipline/tag-policies/tpnt/transmitter/src/transmitter/localmoc/report.csv
    csvpath = os.path.join(os.environ['src'],'transmitter','localmoc','report.csv')
    print(csvpath)
    with open(csvpath, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        print(len([dict(d) for d in reader]))
        ret = app.filter_noncompliants(reader)
#        for row in reader:
#            print(row['AccountId'])
    #https://alexharv074.github.io/2019/03/02/introduction-to-sam-part-i-using-the-sam-cli.html
    #https://docs.pytest.org/en/stable/assert.html
    assert len(ret) == 1
