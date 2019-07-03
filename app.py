#!/usr/bin/env python3

import sys,json,boto3
from thingstack.ThingStack import ThingStack
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from aws_cdk import core

app = core.App()

THING_NAME = app.node.try_get_context("thing_name")

with open(app.node.try_get_context("policy_file"), "r") as f:
    POLICY = json.load(f)

cfnClient = boto3.client("cloudformation")
secretsClient = boto3.client("secretsmanager")

try:
    stacks = cfnClient.describe_stacks(StackName=THING_NAME)

    outputs = [x["Outputs"] for x in stacks["Stacks"] if x["StackStatus"] in ["CREATE_COMPLETE","UPDATE_COMPLETE"]]

    if len(outputs) > 1:
        sys.exit("Too many matching Stacks ({l})".format(l=len(outputs)))

    secretId = [x["OutputValue"] for x in outputs[0] if x["OutputKey"] == "SecretId"][0]

    secret = secretsClient.get_secret_value(SecretId=secretId)
    secretJson = json.loads(secret["SecretString"])

    KEY_TEXT = secretJson["privateKey"]
    CSR_TEXT = secretJson["csr"]

except:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    csr = x509.CertificateSigningRequestBuilder().subject_name(
        x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "AWS IoT Certificate")])
    ).sign(key, hashes.SHA256(), default_backend())

    KEY_TEXT = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
    ).decode("UTF-8")
    CSR_TEXT = csr.public_bytes(serialization.Encoding.PEM).decode("UTF-8")

ThingStack(app, THING_NAME, KEY_TEXT, CSR_TEXT, POLICY)
app.synth()