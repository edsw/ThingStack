import json
from aws_cdk import core
from aws_cdk import aws_iot
from aws_cdk import aws_secretsmanager

class ThingStack(core.Stack):
    def __init__(self, app: core.App, id: str, key: str, csr: str, policy: str) -> None:
        super().__init__(app, id)

        thing = aws_iot.CfnThing(self, "Thing", thing_name=self.stack_name)
        cert = aws_iot.CfnCertificate(self, "ThingCertificate", certificate_signing_request=csr, status="ACTIVE")
        policy = aws_iot.CfnPolicy(self, "ThingPolicy", policy_document=policy)

        aws_iot.CfnThingPrincipalAttachment(self, "ThingCertificateAttachment", principal=cert.attr_arn, thing_name=thing.ref)
        aws_iot.CfnPolicyPrincipalAttachment(self, "ThingPolicyAttachment", principal=cert.attr_arn, policy_name=policy.ref)

        secret = aws_secretsmanager.CfnSecret(self, "PrivateKeySecret", secret_string=json.dumps({"certificateId": cert.ref, "csr": csr, "privateKey": key}))

        core.CfnOutput(self, "ThingId", value=thing.ref)
        core.CfnOutput(self, "CertificateId", value=cert.ref)
        core.CfnOutput(self, "SecretId", value=secret.ref)