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


class CloudtrailStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, es_host: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        fn = _lambda.Function(
            scope=self,
            id='lambda-fn',
            runtime=_lambda.Runtime.GO_1_X,
            handler='main',
            code=_lambda.Code.from_asset(path=os.path.join(
                'elasticSearch', "main.zip")),
            environment={
                "ES_HOST": es_host,
                "ES_REGION": core.Aws.REGION,
            },
            # log_retention=logs.RetentionDays.ONE_WEEK,
            retry_attempts=0,
        )

        rule = events.Rule(
            scope=self,
            id="audit-event-rule",
            description="rule to match all iam user accitions",
            enabled=True,
        )

        rule.add_event_pattern(
            detail_type=["AWS API Call via CloudTrail"],
            account=[core.Aws.ACCOUNT_ID],
            detail={
                "userIdentity": {
                    "type": ['IAMUser'],
                }
            }
        )
        rule.add_target(
            target=targets.LambdaFunction(
                handler=fn),
        )
