#!/usr/bin/env python3
from aws_cdk import core

from cloudtrail_es_cognito.cloudtrail_stack import CloudtrailStack
from cloudtrail_es_cognito.es_cognito_stack import ESCognitoStack

app = core.App()
es_stack = ESCognitoStack(
    scope=app,
    id="es-cognito",
    application_prefix="elastic")

CloudtrailStack(
    scope=app,
    id="cloudtrail",
    es_host=es_stack.es_host)

app.synth()
