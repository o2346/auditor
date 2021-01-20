

.PHONY: localinvoke bucketpolicy deploy undeploy test help
#SHELL := $(shell which zsh)

bucket_name = $(shell echo "tagpolicies-generated-reports-`aws sts get-caller-identity --query Account --output text`")
sendto = 'https://xxxx'

bucketif: ## Make bucket if absent
	@aws s3 ls | grep "$(bucket_name)" || aws s3 mb s3://$(bucket_name)

rbif: ## Forcibly remove bucket if present
	@aws s3 ls | grep "$(bucket_name)" && aws s3 rb --force s3://$(bucket_name)

put_bucket_policy: ##
	-@make -s bucketif
	@mkdir -p .user_cache
	@../s3bucket/generate-bucekt-policy.sh $(bucket_name) | tee .user_cache/.bucket_policy_$(bucket_name).json
	@aws s3api put-bucket-policy --bucket $(bucket_name) --policy file://.user_cache/.bucket_policy_$(bucket_name).json

#put_sample_csv: ## put sample.report.csv to $(bucket_name)
#	-@make -s bucketif
#	@aws s3 cp ./events/sample.report.csv s3://$(bucket_name)/sample.report.csv

local_invoke: ## sam local invoke
	@sam build
	@sam local invoke --event events/event.json

deploy: ## create stack in samcli
#	-@make -s rbif
	@sam build
	@sam deploy --resolve-s3
	@make -s put_bucket_policy

undeploy: ## delete stack
	@aws cloudformation delete-stack --stack-name tpnt-transmitter

test: ## print test message
	@echo $(bucket_name)
	@echo $(SHELL)

help: ## print about the targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
#.DEFAULT_GOAL := help
# https://postd.cc/auto-documented-makefile/
# https://www.gnu.org/software/make/manual/make.html#Standard-Targets

#https://kanasys.com/tech/522
##!/bin/bash
#make -j -f <(tail -n+$(expr $LINENO + 1) $0) $@ ;exit 0

