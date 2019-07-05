import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="ThingStack",
    version="0.1",

    description="Python 3 project to create an AWS CloudFormation stack via the AWS CDK that provisions a Thing on AWS IoT, along with automated certificate creation and storage with AWS Secrets Manager.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Ed Swindelles",
    author_email="ed@swindelles.com",

    install_requires=[
        "cryptography",
        "boto3",
        "aws-cdk.core",
        "aws-cdk.aws-iot",
        "aws-cdk.aws-secretsmanager"
    ],

    python_requires=">=3.6"
)