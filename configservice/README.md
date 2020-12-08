# helper elements for AWS Config

This is a part of explanation for [this parent article](https://qiita.com/o2346/fd4175335fd78418d9c9)
Besides, this is an excersize from my interest and designed to prove such tasks can be applied in the way below, instead of sticking around on Management Console.

## usage example to deploy a managed rule 'required-tags' across organizations along with aggregation feture, by CloudFormation StackSets in CLI

assuming conditions as follows:
- an account considered to be compliance account is one of member accounts of organization
- an aggregator of the compliance account is going to reside on us-east-1
- source accounts are supposed to reside in an ou $ouid
  - also /tmp/accounts.csv is already present
    - and the file contains the same accounts properly
- A Cloudformation template /tmp/required-tags-for-stackset.json is already present
  - you may generate one by [rdk](https://github.com/awslabs/aws-config-rdk)
- regions to deploy the Config rule as well as Aggregation Authorizations are $regions in comma separated
- most of the commands for CloudFormation will be executed with permission_model=SERVICE_MANAGED but there is an exeption
- other technical conditions indicated on parent article

in the begging, define ids and regions which may vary according to your env like below

```
compliance_accountid='12_DIGITS_ACCOUNT_ID_OF_YOURS'
ouid='OUID_WHICH_CONTAINS_TARGET_SOURCE_ACCOUNTS'
regions="us-east-1,ap-northeast-1"
```

Obtain credentials of the Organizations master account in order to create-stack-set.
Thereafter issue following commands sequentially

```
./cloudformation.sh create-stack-set --stack-set-name ConfigServiceAggregator \
  --description "an instance of Configservice Aggregator" \
  --template-body "file://aggregator.yml" \
  --parameters '[{"ParameterKey":"SourceAccounts","ParameterValue":"'`cat /tmp/accounts.csv`'"}]' \
  --deployment-targets "Accounts=$compliance_accountid" \
  --regions "us-east-1"
```

note: Beware deployment-targets of the command above is an account(instead of ou) considered to be a compliance account.
Meaning proper [Grant self-managed permissions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-prereqs-self-managed.html) between the one and Organizations master account is required to make this command successful.
In this case permission model will be switched to SELF_MANAGED(see the source of ./cloudformation.sh). This is the exception indicated before.

those two below are for source accounts in $ouid

```
./cloudformation.sh create-stack-set --stack-set-name ConfigServiceAggregationAuthorizations \
  --description "an auth for Configservice Aggregator" \
  --template-body "file://aggregation-authorizations.yml" \
  --parameters '[{"ParameterKey":"ComplianceAccount","ParameterValue":"'$compliance_accountid'"}]' \
  --deployment-targets "OrganizationalUnitIds=$ouid" \
  --regions "$regions"
```

```
./cloudformation.sh create-stack-set --stack-set-name required-tags \
  --description "AWS Config managed rule required-tags" \
  --template-body "file:///tmp/required-tags-for-stackset.json" \
  --parameters '[{"ParameterKey":"LambdaAccountId","ParameterValue":"'$compliance_accountid'"}]' \
  --deployment-targets "OrganizationalUnitIds=$ouid" \
  --regions "$regions"
```

after completion, visit Management Console of the compliance accunt, navigate to AWS Config in us-east-1.
Select 'Aggregated view' on the left pane and review what's up.
Or else same way through CLI or other api as you prefer.

## misc

As you know, Config rules to be deployed even in this procedure does not have to be limited to 'required-tags'. You may try some others in case of your interest. Good luck.
