

.PHONY: localinvoke bucketpolicy deploy undeploy test help
#SHELL := $(shell which zsh)

accountid = $(shell aws sts get-caller-identity --query Account --output text)
bucket1_name = "tagpolicies-generated-reports-$(accountid)"
bucket2_name = "tagpolicies-noncompliantonly-reports-$(accountid)"
sendto = 'https://xxxx'

bucketif: ## Make bucket if absent
	@aws s3 ls | grep "$(bucket1_name)" || aws s3 mb s3://$(bucket1_name)

rbif: ## Forcibly remove bucket if present
	@aws s3 ls | grep "$(bucket1_name)" && aws s3 rb --force s3://$(bucket1_name)

put_bucket_policy: ## https://docs.aws.amazon.com/ARG/latest/userguide/tag-policies-prereqs.html#bucket-policy
	-@make -s bucketif
	@mkdir -p .user_cache
	@../s3bucket/generate-bucekt-policy.sh $(bucket1_name) | tee .user_cache/.bucket_policy_$(bucket1_name).json
	@aws s3api put-bucket-policy --bucket $(bucket1_name) --policy file://.user_cache/.bucket_policy_$(bucket1_name).json

#put_sample_csv: ## put sample.report.csv to $(bucket1_name)
#	-@make -s bucketif
#	@aws s3 cp ./events/sample.report.csv s3://$(bucket1_name)/sample.report.csv

local_invoke: ## sam local invoke
	@echo $(bucket1_name)
	@sam build
	@sam local invoke -l /tmp/invoke.log --event events/event.json  --parameter-overrides 'Bucket1Name=$(bucket1_name) Bucket2Name=$(bucket2_name) SendTo=$(sendto)'

deploy: ## create stack in samcli
#	-@make -s rbif
	@sam build
	@sam deploy --resolve-s3
	@make -s put_bucket_policy

undeploy: ## delete stack
	@aws cloudformation delete-stack --stack-name tpnt-transmitter

test: ## print test message
	@python3 -m pytest tests/ -v

#FYI
#https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/building-custom-runtimes.html
#https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-build.html

help: ## print about the targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
#.DEFAULT_GOAL := help
# https://postd.cc/auto-documented-makefile/
# https://www.gnu.org/software/make/manual/make.html#Standard-Targets
#

#https://kanasys.com/tech/522
##!/bin/bash
#make -j -f <(tail -n+$(expr $LINENO + 1) $0) $@ ;exit 0

