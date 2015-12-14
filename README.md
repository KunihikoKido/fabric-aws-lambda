# Fabric Tasks for AWS Lambda function development

## Install

```shell
pip install git+https://github.com/kunihikokido/fabric-aws-lambda.git
```

## Example fabfile.py

Example ``fabfile.py``
```python
# -*- coding: utf-8 -*-
from fabric_aws_lambda import SetupTask
from fabric_aws_lambda import InvokeTask
from fabric_aws_lambda import MakeZipTask
from fabric_aws_lambda import AWSLambdaInvokeTask
from fabric_aws_lambda import AWSLambdaGetConfigTask
from fabric_aws_lambda import AWSLambdaUpdateCodeTask

LAMBDA_FUNCTION_NAME = 'hello-lambda'

task1 = SetupTask()
task2 = InvokeTask()
task3 = MakeZipTask()
task4 = AWSLambdaInvokeTask(LAMBDA_FUNCTION_NAME)
task5 = AWSLambdaGetConfigTask(LAMBDA_FUNCTION_NAME)
task6 = AWSLambdaUpdateCodeTask(LAMBDA_FUNCTION_NAME)
```

```
fab --list
Available commands:

    aws-getconfig           Get function configuration on AWS Lambda.
    aws-invoke              Invoke function on AWS Lambda.
    aws-updatecode          Update code on AWS Lambda.
    invoke                  Invoke function on Local Machine.
    makezip                 Make zip file for AWS Lambda Function.
    setup                   Setup on Local Machine.
```
