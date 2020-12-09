import boto3
client = boto3.client('config')

response = client.get_aggregate_compliance_details_by_config_rule(
    ConfigurationAggregatorName='ConfigurationAggregator',
    ConfigRuleName='required-tags',
    AccountId='111111111111',
    AwsRegion='ap-northeast-1',
    ComplianceType='NON_COMPLIANT'
)

print(response)



