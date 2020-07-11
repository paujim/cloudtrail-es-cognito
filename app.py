#!/usr/bin/env python3
from aws_cdk import core

from cloudtrail_es_cognito.cloudtrail_stack import CloudtrailStack
from cloudtrail_es_cognito.es_cognito_stack import ESCognitoStack

app = core.App()
es_stack = ESCognitoStack(
    scope=app,
    id="es-cognito",
    application_prefix="myelastic")

CloudtrailStack(
    scope=app,
    id="cloudtrail",
    es_host=es_stack.es_host,
    es_arn=es_stack.es_arn,
)

app.synth()
