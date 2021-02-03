# Tag Policies Non-compliance Transmitter

<!--StackName:TagPoliciesNoncomplianceTransmitter-->
Send message to slack channel when Non-compliant resources against tag policies was introduced

## Prerequisites

- Credentials of your Organizations Master account on terminal
  - for Generator(see below)
- Credentials of your Compliance account on terminal
  - for Transmitter(see below)
- Webhook URL of your Slack chat room
  - [/invite @AWS](https://docs.aws.amazon.com/chatbot/latest/adminguide/getting-started.html#chat-client-setup) if the desired channel was private

## Features

There are 2 separate components below with respective sam templates.

### Generator

- Being deployed Organizations Master Account.
- [Generate report](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/resourcegroupstaggingapi.html#ResourceGroupsTaggingAPI.Client.start_report_creation) to given S3 bucket periodically.
  - The S3 bucket for the report will not reside Organizations Master Account but Compliance Account

### Transmitter

- Being deployed on Compliance Account.
- Fired when Compliance Report were generated on the S3 Bucket, filter out and provide only non-compliant items. It then transmit the warning message contaings location of Non-compliant report to given slack channel.
- User who recieves the warning message then can download the Non-compliant report, only if he does deserve with proper permissions.

## Preparation

`git clone` this repo and `cd` to this directory

## Deploy the application

assuming default region is us-east-1

### Transmitter

Follow instruction described in 'transmitter/README.md'

### Generator

Follow instruction described in 'generator/README.md'

