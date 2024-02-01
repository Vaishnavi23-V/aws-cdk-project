from aws_cdk import core
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_iam import PolicyStatement, Effect
from aws_cdk.aws_apigateway import LambdaRestApi

class MyCdkAppStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # DynamoDB Table
        dynamo_table = Table(
            self, "HelloWorldTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST
        )

        # Lambda Function
        hello_function = Function(
            self, "HelloFunction",
            runtime=Runtime.PYTHON_3_9,
            handler="handler.hello",
            code=Code.from_asset("lambda"),  
            environment={"DYNAMODB_TABLE": dynamo_table.table_name}
        )

        # Permissions for Lambda to access DynamoDB
        dynamo_table.grant_read_write_data(hello_function)

        # Additional IAM permissions for PutItem
        hello_function.add_to_role_policy(
            statement=PolicyStatement(
                actions=["dynamodb:PutItem"],
                effect=Effect.ALLOW,
                resources=[dynamo_table.table_arn]
            )
        )

        # API Gateway
        api = LambdaRestApi(
            self, "HelloApi",
            handler=hello_function
        )
