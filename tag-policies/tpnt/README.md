# Tag Policies Non-compliance Transmitter

<!--StackName:TagPoliciesNoncomplianceTransmitter-->
Send message to slack channel when Non-complianct against tag policies was introduced

## Prerequisites

- Obtain Credentials of your Organizations Master account on terminal
- Obtain Credentials of your Compliance account on terminal
- Obtain webhook URL of your Slack chat room
  - [/invite @AWS](https://docs.aws.amazon.com/chatbot/latest/adminguide/getting-started.html#chat-client-setup) if the desired channel was private

---

## Preparation

Just `git clone` this repo and `cd` to this directory

## Deploy the application

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX --resolve-s3
```

The first command will build the source of your application. The second command will package and deploy your application to AWS.

## Build and run locally

Build your application with the `sam build` command & Run functions locally invoking them with the `sam local invoke` command.

```bash
sam build && sam local invoke --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Invoke with tailing debug output

```
sendto=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
sam build && sam local invoke --parameter-overrides SendTo=$sendto --debug -l "$(dirname $(mktemp -u))"/invoke.log
```
On the other hand, review output by something like:

`tail -f "$(dirname $(mktemp -u))"/invoke.log`

---

## Features

There are 2 separate components below with sam templates.

### Generator

Being deployed Organizations Master Account.
[Generate report](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/resourcegroupstaggingapi.html#ResourceGroupsTaggingAPI.Client.start_report_creation) to given S3 bucket periodically.
The S3 bucket would reside Compliance Account other than Organizations Master Account.

### Transmitter

Being deployed Compliance Account.
Fired when Compliance Report were introduced on the S3 Bucket described above, filter out and provide only non-compliant items. It then transmit Non-compliant items to given slack channel.


