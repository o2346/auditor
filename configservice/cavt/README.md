# Configservice Aggregated Non-compliance Transmitter

Sends warning message for noncompliant resouce(s) which violates against config rule to Slack channel. Currently only a managed rule 'required-tags' was confirmed work.

This is developed with [sam](https://aws.amazon.com/serverless/sam/) and based on a following selection from the tool:

>
> AWS quick start application templates:
>         3 - EventBridge App from scratch (100+ Event Schemas)
>
>       66 - aws.events@ScheduledJson

You may find this Schema while interacting `sam init`.

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- function - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and a ScheduledEvent. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

## Prerequisites

- Obtain Credentials of your Compliance account on terminal
- Make sure an aggregator named `ConfigurationAggregator` is ready on the Compliance account
  - fyi, a sample way to set up an aggregator is introduced at directory above.
- Souce account(s) with Aggregation auth
- Set up 'required-tags' on some Source account(s), at least one
  - You would not recive any message if the rule was not present or every resources in the scope was compliant
- Obtain webhook URL of your Slack chat room
  - [/invite @AWS](https://docs.aws.amazon.com/chatbot/latest/adminguide/getting-started.html#chat-client-setup) if the desired channel was private

## Preparation

Just `git clone` this repo and `cd` to this directory

## Deploy the application

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX --resolve-s3
```

The first command will build the source of your application. The second command will package and deploy your application to AWS.

> The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.
> 
> To use the SAM CLI, you need the following tools.
> 
> * SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
> * [Python 3 installed](https://www.python.org/downloads/)
> * Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

## Build and run locally

Build your application with the `sam build` command & Run functions locally invoking them with the `sam local invoke` command.

```bash
sam build && sam local invoke --parameter-overrides SendTo=https://hooks.slack.com/services/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

> The SAM CLI installs dependencies defined in `function/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.
> Don't forget to update the event.json detail with the fields you want to set from your schema.aws.events.scheduledjson.ScheduledEvent object

### Invoke with tailing debug output

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


### Self-Imposed Posting Restraint

- Omit reporting Individuals if too many
  - To be more precise, if number of actual noncompliant resouces has exceeded predefined threshold
  - Even at such a case, Summary will anyway be transmitted
    - So you would at least be noticed there were many of them. Go to Aggregated View on Management Console for individual details at such case
- Without this restraint, You might receive the huge number of messages as well as number of noncompliant resouces. For instance, if there were 1000 of noncompliant resouces, number of messages would be the same
  - Assuming such a behavior is undesirable

### Misc

- Summary will finally be omitted if there was zero noncompliant resource. Congratulations.

## todo for future

Defferent rules other than 'required-tags' could be applied.
It supposed to be availabe by adding proper context jsons.
Unfortunately that is not tested neither well documented yet.

> ## Add a resource to your application
> 
> The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.
> 
> ## Fetch, tail, and filter Lambda function logs
> 
> To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.
> 
> `NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.
> 
> ```bash
> $ sam logs -n HelloWorldFunction --stack-name STACK_NAME --tail
> ```
> 
> You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).
> 
> ## Unit tests
> 
> N/A

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name STACK_NAME
```

> ## Resources
> 
> See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.
