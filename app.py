#!/usr/bin/env python3

from aws_cdk import core

from poolcontroller.poolcontroller_stack import PoolcontrollerStack


app = core.App()
PoolcontrollerStack(app, "poolcontroller-cdk-1")

app.run()
