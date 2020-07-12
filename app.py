#!/usr/bin/env python3
import constants
from aws_cdk import (
    core,
    aws_iam as iam,
)

from cloudtrail_es_cognito.cloudtrail_stack import CloudtrailStack
from cloudtrail_es_cognito.es_cognito_stack import ESCognitoStack

app = core.App()

es_stack = ESCognitoStack(
    scope=app,
    id="es-cognito",
    domain_prefix=constants.ES_DOMAIN_PREFIX,
    other_account=constants.OTHER_ACCOUNT,
)

CloudtrailStack(
    scope=app,
    id="cloudtrail",
    es_host=constants.ES_HOST,
    es_region=constants.ES_REGION,
    es_external_role=constants.ES_EXT_ROLE_ARN,
)

app.synth()
