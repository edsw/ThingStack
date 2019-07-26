#!/usr/bin/env python3

import json,thingstack,thingcert
from aws_cdk import core

app = core.App()

# Get the Thing name from the AWS CDK context
thing_name = app.node.try_get_context("thing_name")

# Get the Role ARN to assume for access to AWS services and AWS region
role_arn = app.node.try_get_context("role_arn")
region = app.node.try_get_context("region")

# Get the policy file used by your Certificate/Thing from the AWS CDK context
with open(app.node.try_get_context("policy_file"), "r") as f:
    policy = json.load(f)

# Get an existing certificate for this Thing, if available, otherwise create one
key, csr = thingcert.get_or_create(thing_name, role_arn, region)

# Finally, create the Stack
thingstack.ThingStack(app, thing_name, key, csr, policy)
app.synth()