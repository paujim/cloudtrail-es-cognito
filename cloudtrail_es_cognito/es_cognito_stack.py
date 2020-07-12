import os
from aws_cdk import (
    core,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3 as s3,
    aws_iam as iam,
    aws_logs as logs,
    aws_lambda as _lambda,
    aws_elasticsearch as elasticsearch,
    aws_cognito as cognito
)


class ESCognitoStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, domain_prefix: str, other_account: str,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        user_pool = cognito.CfnUserPool(
            scope=self,
            id="user-pool",
            admin_create_user_config=cognito.CfnUserPool.AdminCreateUserConfigProperty(
                allow_admin_create_user_only=True,
            ),
            policies=cognito.CfnUserPool.PoliciesProperty(
                password_policy=cognito.CfnUserPool.PasswordPolicyProperty(
                    minimum_length=10,
                )),
            username_attributes=["email"],
            auto_verified_attributes=["email"],
        )

        cognito.CfnUserPoolDomain(
            scope=self,
            id="cognito-user-pool-domain",
            domain=f"{domain_prefix}-{core.Aws.ACCOUNT_ID}",
            user_pool_id=user_pool.ref,
        )

        id_pool = cognito.CfnIdentityPool(
            scope=self,
            id="identity-pool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[],
        )

        auth_role = iam.Role(
            scope=self,
            id="auth-role",
            assumed_by=iam.FederatedPrincipal(
                federated="cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {"cognito-identity.amazonaws.com:aud": id_pool.ref},
                    "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": "authenticated"},
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity"),
        )

        es_role = iam.Role(
            scope=self,
            id="es-role",
            assumed_by=iam.ServicePrincipal('es.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name="AmazonESCognitoAccess"
                )
            ],
        )

        es_domain = elasticsearch.CfnDomain(
            scope=self,
            id="search-domain",
            elasticsearch_cluster_config=elasticsearch.CfnDomain.ElasticsearchClusterConfigProperty(
                instance_count=2,
                instance_type="t2.small.elasticsearch"),
            ebs_options=elasticsearch.CfnDomain.EBSOptionsProperty(
                ebs_enabled=True,
                volume_size=20),
            elasticsearch_version="7.4",
            domain_name=domain_prefix,
            access_policies={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": auth_role.role_arn
                        },
                        "Action": [
                            "es:ESHttpGet",
                            "es:ESHttpPut",
                            "es:ESHttpPost",
                            "es:ESHttpDelete"
                        ],
                        "Resource": "arn:aws:es:" + core.Aws.REGION + ":" + core.Aws.ACCOUNT_ID + ":domain/" + domain_prefix + "/*"
                    },
                ]
            },
        )

        es_domain.add_property_override(
            'CognitoOptions.Enabled', True)
        es_domain.add_property_override(
            'CognitoOptions.IdentityPoolId', id_pool.ref)
        es_domain.add_property_override(
            'CognitoOptions.RoleArn', es_role.role_arn)
        es_domain.add_property_override(
            'CognitoOptions.UserPoolId', user_pool.ref)

        cognito.CfnIdentityPoolRoleAttachment(
            scope=self,
            id='user-pool-role-attachment',
            identity_pool_id=id_pool.ref,
            roles={
                'authenticated': auth_role.role_arn
            }
        )

        es_external_role = iam.Role(
            scope=self,
            id="logger-role",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("lambda.amazonaws.com"),
                iam.AccountPrincipal(other_account),
            ),
            description="role to use elastic search assumed by lambda",
            inline_policies={
                "es_policy": iam.PolicyDocument(statements=[
                    iam.PolicyStatement(
                        actions=[
                            "es:ESHttpPost",
                        ],
                        resources=[
                            es_domain.attr_arn + "/*",
                        ],
                    )]),
            },
        )

        core.CfnOutput(
            scope=self,
            id="es-host",
            value=es_domain.attr_domain_endpoint,
        )

        core.CfnOutput(
            scope=self,
            id="es-region",
            value=core.Aws.REGION,
        )

        core.CfnOutput(
            scope=self,
            id="es-external-role",
            value=es_external_role.role_arn,
        )
