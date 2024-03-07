from aws_cdk import (
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_certificatemanager as acm, 
    aws_cloudfront as cloudfront,
    aws_route53 as route53,
    aws_lambda as _lambda,
    aws_route53_targets as targets,
    Stack
)
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from aws_cdk.aws_iam import PolicyStatement, Effect
from aws_cdk import aws_iam as iam
from constructs import Construct

class FrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

         # S3 Bucket for HTML files with web hosting and public ACL permissions
        s3_bucket = Bucket(
            self, "new-awesome-app.com",
            block_public_access=BlockPublicAccess(restrict_public_buckets=False),
            encryption=s3.BucketEncryption.S3_MANAGED,
            website_index_document="index.html",
            website_error_document="error.html"
        )

        s3_deployment = BucketDeployment(
            self, "RootDeployment",
            sources=[Source.asset("frontend/my-vue-app/dist")],
            destination_bucket=s3_bucket,
        )

         # Grant public read access to all objects in the bucket
        s3_bucket.grant_public_access()

        www_subdomain_bucket = s3.Bucket(
                    self, "www.new-awesome-app.com",
                    website_index_document="index.html",
                    website_error_document="error.html"
        )
        
      # Define or refer hosted zone
        domain_name = "new-awesome-app.com"  

        hosted_zone = route53.HostedZone.from_lookup(self, "existing-zone",
        domain_name=domain_name
        )

      # Define ACM certificate for the custom domain
        certificate = acm.Certificate(self, "MyCertificate",
        domain_name="new-awesome-app.com",
        validation=acm.CertificateValidation.from_dns(hosted_zone),
       )

      # CloudFront distribution configuration 
        distribution_root = cloudfront.CloudFrontWebDistribution(self, "RootDomainDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=s3_bucket
                    ),
                    behaviors=[
                        cloudfront.Behavior(is_default_behavior=True)
                    ]
                )
            ],
            viewer_certificate=cloudfront.ViewerCertificate.from_acm_certificate(certificate),  
            default_root_object="index.html"
        )   

        # Update the S3 bucket policy to allow access only from CloudFront
        s3_bucket.add_to_resource_policy(iam.PolicyStatement(
            sid="AllowCloudFrontServicePrincipal",
            effect=iam.Effect.ALLOW,
            principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
            actions=["s3:GetObject"],
            resources=[f"{s3_bucket.bucket_arn}/*"],
            conditions={
                "StringEquals": {
                    "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution_root.distribution_id}",
                }
            }
        ))
       
         # Create a record set for the CloudFront distribution
        cloudfront_alias_record = route53.ARecord(
            self, "CloudFrontAliasRecord",
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution_root)),
            zone=hosted_zone,
        )  
 
       