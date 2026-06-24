from aws_cdk import (
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_certificatemanager as acm, 
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_lambda as _lambda,
    aws_route53_targets as targets,
    Stack,
    RemovalPolicy,
    Duration,
    Size
)
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from aws_cdk.aws_iam import PolicyStatement, Effect
from aws_cdk import aws_iam as iam
from constructs import Construct

class FrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Bucket for HTML files - private bucket accessed only via CloudFront
        s3_bucket = Bucket(
            self, "beg-sdv-dashboard",
            block_public_access=BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True
            ),
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Deploy frontend assets - with explicit IAM permission grant
        s3_deployment = BucketDeployment(
            self, "RootDeployment",
            sources=[Source.asset("frontend/my-vue-app/dist")],
            destination_bucket=s3_bucket,
            memory_limit=512,
            ephemeral_storage_size=Size.mebibytes(1024),
            retain_on_delete=False
        )

        # Define hosted zone
        domain_name = "beg-sdv-dashboard.com"  
        subdomains = [
            "app.beg-sdv-dashboard.com",
        ]

        hosted_zone = route53.HostedZone.from_lookup(
            self, "existing-zone",
            domain_name=domain_name
        )

        # Define ACM certificate for all domains
        certificate = acm.Certificate(
            self, "dashboard-certificate",
            domain_name=domain_name,
            subject_alternative_names=subdomains,
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

        # Create Origin Access Identity for secure S3 access
        oai = cloudfront.OriginAccessIdentity(
            self, "OAI",
            comment="OAI for beg-sdv-dashboard bucket"
        )

        # Grant CloudFront OAI permission to read from the bucket
        s3_bucket.grant_read(oai)

        # Modern CloudFront distribution using Distribution (not deprecated CloudFrontWebDistribution)
        distribution_root = cloudfront.Distribution(
            self, "RootDomainDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    s3_bucket,
                    origin_access_identity=oai
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                compress=True,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            default_root_object="index.html",
            certificate=certificate,
            domain_names=[domain_name] + subdomains,
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5)
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5)
                )
            ]
        )

        # Create DNS alias record for CloudFront distribution (main domain)
        cloudfront_alias_record = route53.ARecord(
            self, "CloudFrontAliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(distribution_root)
            ),
        )

        # Create subdomain alias records
        for i, subdomain in enumerate(subdomains):
            route53.ARecord(
                self, f"SubdomainAliasRecord{i}",
                record_name=subdomain.replace(f".{domain_name}", ""),
                zone=hosted_zone,
                target=route53.RecordTarget.from_alias(
                    targets.CloudFrontTarget(distribution_root)
                ),
            )