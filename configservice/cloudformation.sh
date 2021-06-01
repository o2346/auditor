#!/bin/bash

#usage: $0 subcommands [options]
#supported subcommands
#create-stack-set
#update-stack-set
#create-stack-instances
#update-stack-instances
#delete-stack-set
#delete-stack-instances

#Original instruction
#add-deployment-targets-to-stack-set


cd `dirname $0`
subcommand="$1"

permission_model='SERVICE_MANAGED'
auto_deployment_option='--auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false'
readonly operation_pref="FailureToleranceCount=40,MaxConcurrentCount=4"
readonly regions_file=`mktemp`
aws ec2 describe-regions --all-regions --query 'Regions[?OptInStatus==`opted-in`].{Name:RegionName}' --output text > $regions_file
regions="`cat $regions_file | tr '\n' ' '`"

# args parsing
#https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --stack-set-name)
    readonly stack_set_name="$2"
    shift # past argument
    shift # past value
    ;;
    --deployment-targets)
    deployment_targets="$2" #"OrganizationalUnitIds=$ou"
    shift # past argument
    shift # past value
    ;;
    --regions)
    regions="`echo $2 | tr ',' ' '`" #"us-east-1,us-east-2"
    shift # past argument
    shift # past value
    ;;
    --description)
    readonly description="$2"
    shift # past argument
    shift # past value
    ;;
    --template-body)
    readonly template_body="$2"
    aws cloudformation validate-template --template-body "$template_body"
    readonly is_template_valid=$?
    [ "$is_template_valid" = 0 ] || exit $is_template_valid
    echo 'Template Validation Successful' >&2
    shift # past argument
    shift # past value
    ;;
    --parameters)
    readonly parameters="$2"
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
  esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

# Obtain current deployment targets
echo 'Obtainig recent values' >&2
readonly current_deployment_targets="$(
  aws cloudformation  describe-stack-set                                \
    --stack-set-name $stack_set_name                                    \
    --query 'StackSet.OrganizationalUnitIds' \
    --output text |
  tr '\t' ','
)"
readonly current_regions="$(aws cloudformation list-stack-instances --stack-set-name $stack_set_name --query 'Summaries[].{Region:Region}' --output text | sort -u | tr '\n' ' ')"
echo 'Just ignore error above if attempting to create new one' >&2

# enable stacksets on organizations beforhand according to below
# https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-cloudformation.html
# https://aws.amazon.com/blogs/aws/new-use-aws-cloudformation-stacksets-for-multiple-accounts-in-an-aws-organization/

function get_stackset_status() {
  aws cloudformation describe-stack-set \
    --stack-set-name $1                 \
    --query 'StackSet.Status'
}

function does_stack_exists() {
  :
}

function await_completion() {
  local statusis=`mktemp`
  trap "[ -f $statusis ] && rm $statusis" ERR EXIT
  seq 0 10 | xargs -I{} echo "2^{}-1" | bc | while read standby; do
    sleep "`shuf -i 0-$standby -n 1`" #https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

    aws cloudformation list-stack-set-operations --stack-set-name $1 \
      --query 'Summaries[?Status==`RUNNING`]' \
      --output text | grep 'RUNNING'
    [ "$?" != 0 ] && printf '0' > $statusis && break
    printf '1' > $statusis
    echo 'Stackset is still not yet ready' >&2
  done
  [ "`cat $statusis`" = '1' ] && echo "[ERROR] Gave up. Something is wrong with the stackset $1" >&2
  return "`cat $statusis`"
}

if echo "$deployment_targets" | grep "Accounts" > /dev/null; then
  permission_model='SELF_MANAGED'
  echo "permission_model will be $permission_model" >&2
  readonly auto_deployment_option=''
  readonly stack_set_name_adminperm='CloudFormationStackSetAdministratorPermmission'
  #https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-prereqs-self-managed.html
  if ! aws cloudformation describe-stacks --stack-name $stack_set_name_adminperm > /dev/null; then
    aws cloudformation create-stack \
      --stack-name $stack_set_name_adminperm \
      --template-url 'https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetAdministrationRole.yml' \
      --capabilities CAPABILITY_NAMED_IAM
    sleep 5
  fi
fi

if [ "$1" = "trust-stack-set-administrator" ]; then
  readonly master=`aws organizations describe-organization --query 'Organization.{a:MasterAccountId}' --output text`
  readonly stack_set_name_execperm='CloudFormationStackSetExectionPermmission'

  if ! aws cloudformation describe-stacks --stack-name $stack_set_name_execperm > /dev/null; then
    aws cloudformation create-stack \
      --stack-name $stack_set_name_execperm \
      --template-url 'https://s3.amazonaws.com/cloudformation-stackset-sample-templates-us-east-1/AWSCloudFormationStackSetExecutionRole.yml' \
      --capabilities CAPABILITY_NAMED_IAM \
      --parameters '[{"ParameterKey": "AdministratorAccountId","ParameterValue":"'$master'"}]'
  fi
  exit $?
fi


if echo $1 | grep 'delete\-stack\-instances'; then
  aws cloudformation delete-stack-instances    \
    --stack-set-name $stack_set_name           \
    --deployment-targets "OrganizationalUnitIds=$current_deployment_targets" \
    --no-retain-stacks                         \
    --regions $current_regions
  await_completion $stack_set_name
  exit 0
fi

if echo $1 | grep 'delete\-stack\-set'; then
  aws cloudformation delete-stack-instances    \
    --stack-set-name $stack_set_name           \
    --deployment-targets "OrganizationalUnitIds=$current_deployment_targets" \
    --no-retain-stacks                         \
    --regions $current_regions
  await_completion $stack_set_name

  aws cloudformation delete-stack-set \
    --stack-set-name $stack_set_name
  await_completion $stack_set_name
  exit 0
fi

if [ "$1" = 'add-deployment-targets-to-stack-set' ]; then

  deployment_targets="$deployment_targets,$current_deployment_targets"
  description="$(aws cloudformation describe-stack-set --stack-set-name $stack_set_name --query 'StackSet.Description' --output text)"
  template_body="$(aws cloudformation describe-stack-set --stack-set-name $stack_set_name --query 'StackSet.TemplateBody' --output text)"
  aws cloudformation validate-template --template-body "$template_body" || exit 1
  permission_model="$(aws cloudformation describe-stack-set --stack-set-name $stack_set_name --query 'StackSet.PermissionModel' --output text)"
  parameters="$(aws cloudformation describe-stack-set --stack-set-name $stack_set_name --query 'StackSet.Parameters')"
  readonly subcommand='create-stack-set'
  regions="$current_regions"

  echo "$deployment_targets"
  echo "$description"
  echo "$template_body"
  echo "$permission_model"
  echo "$parameters"
  echo $subcommand
  echo "$regions"

  aws cloudformation delete-stack-instances    \
    --stack-set-name $stack_set_name           \
    --deployment-targets "OrganizationalUnitIds=$current_deployment_targets" \
    --no-retain-stacks                         \
    --regions $current_regions
  await_completion $stack_set_name

  aws cloudformation delete-stack-set \
    --stack-set-name $stack_set_name
  await_completion $stack_set_name
fi

if [ "$subcommand" = "create-stack-set" ] ; then
  echo 'creating new one' >&2
  aws cloudformation create-stack-set                           \
    --stack-set-name $stack_set_name                            \
    --description "$description"                                \
    --template-body "$template_body"                            \
    --capabilities CAPABILITY_NAMED_IAM                         \
    --permission-model $permission_model                        \
    $auto_deployment_option                                     \
    --parameters "$parameters"
#    [--administration-role-arn <value>]
#    [--execution-role-name <value>]
#    [--client-request-token <value>]
  await_completion $stack_set_name
fi

if [ "$1" = "update-stack-set" ] ; then
  echo "updating" >&2
  aws cloudformation update-stack-set             \
    --stack-set-name $stack_set_name              \
    --description "$description"                  \
    --template-body "$template_body"              \
    --capabilities CAPABILITY_NAMED_IAM           \
    --permission-model  $permission_model         \
    $auto_deployment_option                       \
    --operation-preferences $operation_pref       \
    --parameters "$parameters"

  await_completion $stack_set_name
fi

if echo "$1" | grep -E 'update' > /dev/null; then
  echo 'updating stack-instances' >&2
  aws cloudformation update-stack-instances    \
    --stack-set-name $stack_set_name           \
    --deployment-targets "$deployment_targets" \
    --operation-preferences $operation_pref    \
    --regions $regions

elif echo "$subcommand" | grep -E 'create' > /dev/null; then
  echo 'creating new stack-instances' >&2
  aws cloudformation create-stack-instances    \
    --stack-set-name $stack_set_name           \
    --deployment-targets "$deployment_targets" \
    --operation-preferences $operation_pref    \
    --regions $regions

fi

await_completion $stack_set_name

if echo "$1" | grep -E '(update|detect-stack-set-drift)' > /dev/null; then
  aws cloudformation detect-stack-set-drift \
    --stack-set-name $stack_set_name
  await_completion $stack_set_name
fi

#describe & list
aws cloudformation describe-stack-set      \
  --stack-set-name $stack_set_name         \
  --query 'StackSet.{Status:Status,StackSetARN:StackSetARN,OrganizationalUnitIds:OrganizationalUnitIds}'
aws cloudformation list-stack-instances --stack-set-name $stack_set_name

if [ "$1" = 'delete-stack-set' ]; then
  echo "If error says $stack_set_name not found, affirmative since that is exactly what you expect. Dismissed."
fi

exit 0
