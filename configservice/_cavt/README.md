# Configservice Aggregated Noncompliant Transmitter

Sends noncompliant items which violates against config rule, to Slack channel

This is developed with [sam](https://aws.amazon.com/serverless/sam/) and based on a following selection from the tool:

>
> AWS quick start application templates:
>         3 - EventBridge App from scratch (100+ Event Schemas)
>
>       66 - aws.events@ScheduledJson

You may find this Schema while interacting on `sam init`.

## Prerequisites

- obtain Credentials of your Compliance account on terminal
- Make sure an aggregator is ready on the Compliance account
  - fyi, a sample way to set up an aggregator is introduced at directory above.
- set up 'required-tags' on some Source accounts, at least one
  - You could not confirm any message if the rule was not present or everything was compliant, of course
- obtain webhook url of Your slack channel
  - `\invite AWS` if the desired channel was private

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
sam build && sam local invoke --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX --debug -l /tmp/invoke.log
```

on another terminal, review output by following:

`tail -f /tmp/invoke.log`

## Features

As default, Only 'required-tags' are the rule to inspect.

### Message types

There are 2 kinds of messages to be transmitted

- Individual
  - One message per Noncompliant
- Summary
  - Reports number of Noncompliants for each Source accounts

### Misc

- self-imposed posting restraint
  - Omit reporting Individuals if too many (to be accurate, number of actual Noncompliants has exceeded predefined threshold)
    - Even at such a case, Summary will be transmitted at least. So anyway you would be noticed there were many.
  - Without this restraint, You would receive the same number of messages if there were 1000 or more of Noncompliants
    - Assuming such a behavior is undesirable.
- Summary will finally be omitted if there was zero Noncompliants. Congratulations.

## todo for future

Defferent rules other than 'required-tags' could be applied.
It supposed to be availabe by adding proper context jsons.
Unfortunately that is not tested and well documented yet.

<!-- configservice-aggregated-violation-transmitter -->
