import boto3
import json
client = boto3.client('config')

response = client.get_aggregate_compliance_details_by_config_rule(
    ConfigurationAggregatorName='ConfigurationAggregator',
    ConfigRuleName='required-tags',
    AccountId='111111111111',
    AwsRegion='ap-northeast-1',
    ComplianceType='NON_COMPLIANT'
)

#print(json.dumps(response))

response = client.select_aggregate_resource_config(
    Expression="SELECT configuration \
                WHERE \
                  configuration.configRuleList.complianceType = 'NON_COMPLIANT' \
                  AND configuration.configRuleList.configRuleName = 'required-tags'",
    ConfigurationAggregatorName='ConfigurationAggregator',
)
#https://docs.aws.amazon.com/config/latest/developerguide/querying-AWS-resources.html

for object in response['Results']:
    print(json.dumps(json.loads(object), indent=2))
