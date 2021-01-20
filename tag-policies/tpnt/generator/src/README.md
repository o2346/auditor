# ScheduledEvent

*Automatically generated by the [Amazon Event Schemas](https://aws.amazon.com/)*

## Requirements

1. Python 36+
2. pprint 0.1
3. six 1.12.0
4. regex 2019.11.1

## Install Dependencies
### pip users

Create and update it in current project's **requirements.txt**:

```
pprint == 0.1
six == 1.12.0
regex == 2019.11.1
```

Run Command:

```sh
pip3 install -r requirements.txt
```

## local invoke, debug

```bash
sam build && sam local invoke --parameter-overrides Bucket=tagpolicies-generated-reports-725521117709 --debug -l "$(dirname $(mktemp -u))"/invoke.log
```

On other terminal,

```bash
tail -f "$(dirname $(mktemp -u))"/invoke.log
```