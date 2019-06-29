#!/usr/bin/env python3

# openssl req -nodes -newkey rsa:2048 -keyout privkey.pem -out csr.pem -subj "/CN=AWS IoT Certificate"

from aws_cdk import (
    core,
    aws_iot as iot
)

STACK_ID = "PoolController"
THING_NAME = "poolcontroller1"
CSR_FILE = "csr.pem"

with open(CSR_FILE, 'r') as file:
    csr = file.read()

class PoolcontrollerStack(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        thing = iot.CfnThing(self, "Controller", thing_name=THING_NAME)
        cert = iot.CfnCertificate(self, "ControllerCertificate", certificate_signing_request=csr, status="ACTIVE")
        iot.CfnThingPrincipalAttachment(self, "ControllerCertificateAttachment", principal=cert.attr_arn, thing_name=thing.ref)

app = core.App()
PoolcontrollerStack(app, STACK_ID)
app.synth()
