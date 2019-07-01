#!/usr/bin/env python3

import json

from aws_cdk import (
    core,
    aws_iot as iot
)

THING_NAME = "poolcontroller1"
CSR_FILE = "csr.pem"
POLICY = '''
{
    "Version": "2012-10-17",
    "Statement": [
    {
        "Effect": "Allow",
        "Action": [
            "iot:*"
        ],
        "Resource": [
            "*"
        ]
    }
    ]
}
'''

with open(CSR_FILE, 'r') as file:
    csr = file.read()

class ThingStack(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        thing = iot.CfnThing(self, "Thing", thing_name=self.stack_name)
        cert = iot.CfnCertificate(self, "ThingCertificate", certificate_signing_request=csr, status="ACTIVE")
        policy = iot.CfnPolicy(self, "ThingPolicy", policy_document=json.loads(POLICY))

        iot.CfnThingPrincipalAttachment(self, "ThingCertificateAttachment", principal=cert.attr_arn, thing_name=thing.ref)
        iot.CfnPolicyPrincipalAttachment(self, "ThingPolicyAttachment", principal=cert.attr_arn, policy_name=policy.ref)

        core.CfnOutput(self, "ThingId", value=thing.ref)
        core.CfnOutput(self, "CertificateId", value=cert.ref)

app = core.App()
ThingStack(app, THING_NAME)
app.synth()
