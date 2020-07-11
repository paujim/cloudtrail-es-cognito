#!/usr/bin/env python3

from aws_cdk import core

from cloudtrail_es_cognito.cloudtrail_es_cognito_stack import CloudtrailEsCognitoStack


app = core.App()
CloudtrailEsCognitoStack(app, "cloudtrail-es-cognito")

app.synth()
