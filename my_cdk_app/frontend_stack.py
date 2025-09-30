from aws_cdk import (
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_iam as iam,
    Stack
)
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from constructs import Construct


class FrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        domain_name = "sdvengbegsolutions.com"

        # Private S3 bucket
        s3_bucket = Bucket(
            self,
            "FrontendBucket",
            block_public_access=BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        # Deploy frontend files
        s3deploy.BucketDeployment(
            self,
            "FrontendDeployment",
            sources=[Source.asset("dist/xspace-tenant/browser")],
            destination_bucket=s3_bucket,
            # Automatically invalidate CloudFront cache on deploy
        )

        # Hosted zone
        hosted_zone = route53.HostedZone.from_lookup(
            self,
            "HostedZone",
            domain_name=domain_name
        )

        # ACM certificate in us-east-1
        certificate = acm.Certificate(
            self,
            "FrontendCertificate",
            domain_name=domain_name,
            subject_alternative_names=[f"www.{domain_name}"],
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

        # CloudFront Origin Access Control (OAC)
        oac = cloudfront.CfnOriginAccessControl(
            self,
            "OAC",
            origin_access_control_config=cloudfront.CfnOriginAccessControl.OriginAccessControlConfigProperty(
                name="OACForS3",
                origin_access_control_origin_type="s3",
                signing_behavior="always",
                signing_protocol="sigv4"
            )
        )

        # CloudFront distribution
        distribution_root = cloudfront.CloudFrontWebDistribution(
            self,
            "RootDomainDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=s3_bucket
                    ),
                    behaviors=[cloudfront.Behavior(is_default_behavior=True)]
                )
            ],
            viewer_certificate=cloudfront.ViewerCertificate.from_acm_certificate(
                certificate,
                aliases=[domain_name, f"www.{domain_name}"]
            ),
            default_root_object="index.html",
            # Serve index.html for all SPA routes
            error_configurations=[
                cloudfront.CfnDistribution.CustomErrorResponseProperty(
                    error_code=404,
                    response_code=200,
                    response_page_path="/index.html"
                )
            ]
        )

        # Attach OAC to distribution
        cfn_dist = distribution_root.node.default_child
        cfn_dist.add_property_override(
            "DistributionConfig.Origins.0.OriginAccessControlId", oac.attr_id
        )

        # Bucket policy to allow only CloudFront access
        s3_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject"],
                resources=[f"{s3_bucket.bucket_arn}/*"],
                principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
                conditions={
                    "StringEquals": {
                        "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution_root.distribution_id}"
                    }
                }
            )
        )

        # Route53 alias record
        route53.ARecord(
            self,
            "CloudFrontAliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution_root))
        )
