# configservice aggregated violation transmitter

Sends noncompliant items which violates against config rule to Slack channel

This is developed with [sam]() and based on a following selection from the tool:

>
> AWS quick start application templates:
>         3 - EventBridge App from scratch (100+ Event Schemas)
>
>       66 - aws.events@ScheduledJson

You may find this Schema while interacting on `sam init`.

## Prerequsites

To begin with, obtain Credentials of your Compliance account on terminal.
Make sure an aggregator is ready on the Compliance account. A sample way to set up an aggregator is introduced at above directory.

## Build

`sam build`

## Deploy

```
sam deploy --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX --resolve-s3
```

## local

```
sam build && sam local invoke --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### with debug output

```
sam build && sam local invoke --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX --debug -l /tmp/invoke.log
```

on another terminal, review output by following:

`tail -f /tmp/invoke.log`


## Confirmation

Check the Slack channel that defined by yourself

<!-- configservice-aggregated-violation-transmitter -->
