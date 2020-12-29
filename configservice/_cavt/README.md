# Configservice Aggregated Non-compliance Transmitter

Sends warning message for noncompliant resouce(s) which violates against config rule to Slack channel. Currently only a managed rule 'required-tags' was confirmed work.

This is developed with [sam](https://aws.amazon.com/serverless/sam/) and based on a following selection from the tool:

>
> AWS quick start application templates:
>         3 - EventBridge App from scratch (100+ Event Schemas)
>
>       66 - aws.events@ScheduledJson

You may find this Schema while interacting `sam init`.

## Prerequisites

- Obtain Credentials of your Compliance account on terminal
- Make sure an aggregator named `ConfigurationAggregator` is ready on the Compliance account as well as Souce account(s)
  - fyi, a sample way to set up an aggregator is introduced at directory above.
- Set up 'required-tags' on some Source account(s), at least one
  - You would not recive any message if the rule was not present or every resources in the scope was compliant
- Obtain webhook URL of your Slack chat room
  - [/invite @AWS](https://docs.aws.amazon.com/chatbot/latest/adminguide/getting-started.html#chat-client-setup) if the desired channel was private

## Start

Just `git clone` this repo and `cd` to this directory, issue following commands

### Build

`sam build`

### Deploy

```
sam deploy --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX --resolve-s3
```

### local

```
sam build && sam local invoke --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### with debug output

```
sam build && sam local invoke --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX --debug -l "$(dirname $(mktemp -u))"/invoke.log
```

On the other hand, review output by something like:

`tail -f "$(dirname $(mktemp -u))"/invoke.log`

## Features

As default, Only 'required-tags' is rule to inspect.

### Message types

There are 2 kinds of messages to be transmitted

- Individual
  - One message per noncompliant resouce
- Summary
  - Reports number of noncompliant resouces for each Source accounts

### Misc

- Self-Imposed Posting Restraint
  - Omit reporting Individuals if too many
    - to be accurate, if number of actual noncompliant resouces has exceeded predefined threshold
    - Even at such a case, Summary will anyway be transmitted
      - So you would at least be noticed there were many of them. Go to Aggregated View on Management Console for individual details at such case
  - Without this restraint, You would receive the huge number of messages as well as number of noncompliant resouces. For instance, if there were 1000 of noncompliant resouces, number of messages would be the same
    - Assuming such a behavior is undesirable
- Summary will finally be omitted if there was zero noncompliant resouce. Congratulations.

## todo for future

Defferent rules other than 'required-tags' could be applied.
It supposed to be availabe by adding proper context jsons.
Unfortunately that is not tested neither well documented yet.

<!-- configservice-aggregated-violation-transmitter -->
