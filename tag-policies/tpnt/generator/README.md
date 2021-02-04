# tpnt-generator

Periodically generate Tag policies report and save to Given S3 Bucket.
This is one of 2 major components of Tag Policies Non-compliance Transmitter.

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- src - Code for the application's Lambda function.
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and an EventBridge Rule. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

## Deploy the application

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To execute following commands, obtain credentials of your Organizations Mater account.

To build and deploy your application , run the following in your shell:

```bash
sam build && sam deploy --resolve-s3 --parameter-overrides Bucket=[NAME_OF_BUCKET1]
```

replace NAME_OF_BUCKET1 to Yours.
It supposed to be something like `tagpolicies-generated-reports-111111111111`.
`111111111111` would be an account id of your Compliance account, that tpnt-transmitter would be deployed to.
You will see actual value as of Bucket1 that is one of outputs from cloudformation for tpnt-transmitter.

## Use the SAM CLI to build and test locally

Build your application with the `sam build` command.

```bash
sam build && sam local invoke
```

## Unit tests

N/A

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name `cat samconfig.toml | grep -E '^stack_name' | awk '{print $NF}' | tr -d '"'`


## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
