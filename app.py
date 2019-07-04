#!/usr/bin/env python3

import json,thingstack,thingcert
from aws_cdk import core

app = core.App()

thing_name = app.node.try_get_context("thing_name")

with open(app.node.try_get_context("policy_file"), "r") as f:
    policy = json.load(f)

key, csr = thingcert.get_or_create(thing_name)

thingstack.ThingStack(app, thing_name, key, csr, policy)

app.synth()