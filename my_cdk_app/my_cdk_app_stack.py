from aws_cdk import (
    aws_cognito as cognito, 
    core,
    aws_apigateway as apigateway,
    aws_s3 as s3,
)
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_iam import PolicyStatement, Effect
from aws_cdk.aws_apigateway import LambdaRestApi, Cors
from aws_cdk.aws_cognito import UserPool, UserPoolClient
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from aws_cdk import aws_iam as iam

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

        # API Gateway with CORS support
        api = LambdaRestApi(
            self, "HelloApi",
            handler=hello_function,
            default_cors_preflight_options={
                "allow_origins": Cors.ALL_ORIGINS,
                "allow_methods": Cors.ALL_METHODS,
                "allow_headers": ["*"]
            }
        )

        # Cognito User Pool
        user_pool = UserPool(self, "MyUserPool", removal_policy=core.RemovalPolicy.DESTROY)

        # Cognito User Pool Client
        user_pool_client = UserPoolClient(
            self, "MyUserPoolClient",
            user_pool=user_pool
        )

        # Create an Authorizer for API Gateway
        cognito_authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool],
            identity_source="method.request.header.Authorization",
        )

        # Associate the authorizer with the desired resource or method
        api.root.add_method("GET", authorizer=cognito_authorizer)

        # Custom domain for the User Pool
        user_pool_domain = cognito.CfnUserPoolDomain(
            self, "MyUserPoolDomain",
            user_pool_id=user_pool.user_pool_id,
            domain="my-awesome-app"
        )

        # Grant permissions for Cognito to use the custom domain
        user_pool_domain.node.add_dependency(user_pool)
        user_pool_domain.node.add_dependency(user_pool_client)

        # Create a user in the Cognito User Pool
        user = cognito.CfnUserPoolUser(
            self, "MyUser",
            user_pool_id=user_pool.user_pool_id,
            username="user123",
            desired_delivery_mediums=["EMAIL"],
            user_attributes=[{
                "name": "email",
                "value": "user@gmail.com"
            }],
            force_alias_creation=False
        )

      # S3 Bucket for HTML files with web hosting and public ACL permissions
        s3_bucket = Bucket(
            self, "MyS3Bucket",
            block_public_access=BlockPublicAccess(restrict_public_buckets=False),
            encryption=s3.BucketEncryption.S3_MANAGED,
            website_index_document="index.html",
            website_error_document="error.html"
        )

        # Upload HTML files to S3 bucket using S3Deployment
        s3_deployment = BucketDeployment(
            self, "MyS3Deployment",
            sources=[Source.asset("frontend")],
            destination_bucket=s3_bucket
        )
      # Add public read access policy to the S3 Bucket
        s3_bucket.add_to_resource_policy(iam.PolicyStatement(
        actions=["s3:GetObject"],
        effect=Effect.ALLOW,
        principals=[iam.ArnPrincipal("*")],    
       resources=[f"{s3_bucket.bucket_arn}/*"]
       ))

        admin_function = Function(
            self, "AdminFunction",
            runtime=Runtime.PYTHON_3_9,
            handler="admin_handler.admin",
            code=Code.from_asset("lambda"),
            environment={
                "COGNITO_USER_POOL_ID": user_pool.user_pool_id,
            },
            role=iam.Role(
                self, "LambdaRole",
                assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            )
        )

        # Attach an inline policy to the role granting necessary Cognito permissions
        admin_function.role.add_to_policy(PolicyStatement(
            actions=["cognito-idp:AdminCreateUser", "cognito-idp:AdminDeleteUser"],
            resources=[user_pool.user_pool_arn]
        ))
        
        # Modify the existing API Gateway for admin functions
        admin_api = LambdaRestApi(
        self, "AdminApi",
        handler=admin_function,
        default_cors_preflight_options={
         "allow_origins": Cors.ALL_ORIGINS,
         "allow_methods": Cors.ALL_METHODS,
         "allow_headers": ["*"]
      }
    )
    
         # Cognito Authorizer for the admin API
        admin_cognito_authorizer = apigateway.CognitoUserPoolsAuthorizer(
         self, "AdminCognitoAuthorizer",
         cognito_user_pools=[user_pool],
         identity_source="method.request.header.Authorization",
     )
     
        admin_api.root.add_method("GET", authorizer=admin_cognito_authorizer)

    