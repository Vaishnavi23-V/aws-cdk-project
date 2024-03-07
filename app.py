#!/usr/bin/env python3
import os
import aws_cdk as cdk

from my_cdk_app.my_cdk_app_stack import MyCdkAppStack
from my_cdk_app.frontend_stack import FrontendStack

app = cdk.App()

MyCdkAppStack(app, "MyCdkAppStack", env={'region': 'us-east-1'})
FrontendStack(app, 'FrontendStack', env={'account': '723094108107', 'region': 'us-east-1'}, )

app.synth()
