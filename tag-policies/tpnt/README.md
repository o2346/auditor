# Tag Policies Non-compliance Transmitter

<!--StackName:TagPoliciesNoncomplianceTransmitter-->
Send message to slack channel when Non-compliant resources against tag policies was introduced

![message_img]()

## Features

There are 2 separate components below with respective sam templates.

### Generator

- Being deployed Organizations Master Account.
- [Generate report](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/resourcegroupstaggingapi.html#ResourceGroupsTaggingAPI.Client.start_report_creation) to given S3 bucket periodically.
  - The S3 bucket for the report will not reside Organizations Master Account but Compliance Account

### Transmitter

- Being deployed on Compliance Account.
- Fired when Compliance Report were generated on the S3 Bucket, filter out and provide only non-compliant items. It then transmit the warning message contains location of Non-compliant report to given slack channel.
- User who recieves the warning message then can download the Non-compliant report, only if he does deserve to access the S3 Bucket on the Compliance account.

## Preparation

`git clone` this repo and `cd` to this directory

## Prerequisites

- Credentials of your Organizations Master account on terminal
  - for Generator(see below)
- Credentials of your Compliance account on terminal
  - for Transmitter(see below)
- Webhook URL of your Slack chat room
  - [/invite @AWS](https://docs.aws.amazon.com/chatbot/latest/adminguide/getting-started.html#chat-client-setup) if the desired channel was private

## Quick instruction for deployment

assuming default region is us-east-1

### Transmitter

obtain credentials of your Compliance account.
obtain Slack webhook url of yours.

```bash
cd transmitter
make deploy sendto=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

For more detailes, refer 'transmitter/README.md'

### Generator

Obtain credentials of your Organizations Mater account.
Obtain NAME_OF_BUCKET1 that would be provided as output from cloudformation of Transmitter's deployment.

```bash
cd generator
sam build && sam deploy --resolve-s3 --parameter-overrides Bucket=[NAME_OF_BUCKET1]
```

For more detailes, refer 'generator/README.md'

On the completions of both 2 components above, You then should be recieving warning messages like image above, every 24 hours.

If non of Non-compliants were present to be reported, meaning your entire organization was considered to be completely compliance against Tag Policies, No warning messages would be transmitted.
