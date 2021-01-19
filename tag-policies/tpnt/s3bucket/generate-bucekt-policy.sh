#!/bin/bash
#https://docs.aws.amazon.com/ARG/latest/userguide/tag-policies-prereqs.html#bucket-policy
#Usage:
#./generate-bucekt-policy.sh [custom-bucket-name-if-desired]

#to be more practical,
#aws s3api put-bucket-policy --bucket 'tagpolicies-generated-reports-NNNNNNNNNNNN' --policy "`../s3bucket/generate-bucekt-policy.sh`"

#Assuming such a bucket already exists

cd $(dirname $0)

readonly your_org_id="$(aws organizations describe-organization --query 'Organization.Id' --output text)"

if [ -n "$1" ]; then
  readonly your_bucket_name=$1
else
  readonly your_bucket_name="$(aws s3 ls | grep 'tagpolicies-generated-reports-' | head -n1 | awk '{print $NF}')"
fi

cat ./bucket-policy-template.json |
  sed -e 's/your-org-id/'"${your_org_id}"'/g' |
  sed -e 's/your-bucket-name/'"${your_bucket_name}"'/g'
