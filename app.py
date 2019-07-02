#!/usr/bin/env python3

import json
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID

from aws_cdk import (
    core,
    aws_iot as iot,
    aws_secretsmanager as secretsmanager
)

THING_NAME = "poolcontroller1"

CSR_FILE = Path('csr.pem')
KEY_FILE = Path('key.pem')

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

if not KEY_FILE.is_file() or not CSR_FILE.is_file():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    csr = x509.CertificateSigningRequestBuilder().subject_name(
        x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "AWS IoT Certificate")])
    ).sign(key, hashes.SHA256(), default_backend())

    with open(KEY_FILE, "w") as kf, open(CSR_FILE, "w") as cf:
        kf.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode("UTF-8"))

        cf.write(csr.public_bytes(serialization.Encoding.PEM).decode("UTF-8"))

with open(KEY_FILE, "r") as kf, open(CSR_FILE, "r") as cf:
    keyStr = kf.read()
    csrStr = cf.read()

class ThingStack(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        thing = iot.CfnThing(self, "Thing", thing_name=self.stack_name)
        cert = iot.CfnCertificate(self, "ThingCertificate", certificate_signing_request=csrStr, status="ACTIVE")
        policy = iot.CfnPolicy(self, "ThingPolicy", policy_document=json.loads(POLICY))

        iot.CfnThingPrincipalAttachment(self, "ThingCertificateAttachment", principal=cert.attr_arn, thing_name=thing.ref)
        iot.CfnPolicyPrincipalAttachment(self, "ThingPolicyAttachment", principal=cert.attr_arn, policy_name=policy.ref)

        secret = secretsmanager.CfnSecret(self, "PrivateKeySecret", secret_string=json.dumps({"certificateId": cert.ref, "privateKey": keyStr}))

        core.CfnOutput(self, "ThingId", value=thing.ref)
        core.CfnOutput(self, "CertificateId", value=cert.ref)
        core.CfnOutput(self, "SecretId", value=secret.ref)

app = core.App()
ThingStack(app, THING_NAME)
app.synth()
