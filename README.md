# ThingStack

## About

This project deploys the necessary [AWS IoT](https://aws.amazon.com/iot/) components for the provisioning of a Thing (Arduino, in my case) through [AWS CloudFormation](https://aws.amazon.com/cloudformation/) and the [AWS CDK](https://github.com/awslabs/aws-cdk) (Python). The project automatically generates a device certificate and uses [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) for storing for the device's private key. It can be reused to deploy and manage the lifecycle of multiple devices.

The inspiration for this project was twofold. First, I wanted to install an Arduino microcontroller by my pool in order to track its water temperature. For this I selected an [ESP32-based microcontroller](https://www.amazon.com/dp/B0718T232Z/ref=cm_sw_em_r_mt_dp_U_HlShDb8YN7AT7) and [DS18B20-based temperature sensor](https://www.amazon.com/dp/B01MY8U394/ref=cm_sw_em_r_mt_dp_U_kmShDbWT4C6YH) (_will link here to Arduino code soon_). Second, I wanted to experiment with AWS CDK's Python support.

## Prerequisites
Install the required packages...
```
$ brew install awscli npm jq
$ npm install -g aws-cdk
```
_Note: Only tested on macOS 10.14.5, Python 3.7.2, and AWS CDK 0.37._

## Setup
First, configure your AWS CLI with an Access Key that has the necessary permissions to deploy an AWS IoT stack in CloudFormation. My Access Key had the AWS managed policy `IAMReadOnlyAccess` attached, along with the below customer managed policy:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole",
                "secretsmanager:*",
                "iot:*",
                "cloudformation:*"
            ],
            "Resource": "*"
        }
    ]
}
```
_(Note: This policy provides more access than the minimally required permission set to deploy/destroy a stack.)_

```
aws configure
```

Then, clone this project and install the project prerequisites:
```
$ cd /Directory/Of/Choice
$ git clone <url>
$ pip3 install -r requirements.txt
```

## Deploy a Thing
The file `cdk.json` includes the default context variables used in provisioning the stack.
```
$ cat cdk.json 
{
    "app": "python3 app.py",
    "context": {
        "thing_name": "poolcontroller1",
        "policy_file": "policy.json"
    }
}
```
To alter the name of your AWS IoT Thing, either edit the `thing_name` parameter above, or specify an alternative when deploying the stack on the command line. This also applies to the `policy_file` parameter, which is a JSON file that defines the policy that applies to your Thing.

To use the values from `cdk.json`:
```
$ cdk deploy
```

To specify alternatives on the command line:
```
$ cdk deploy --context thing_name=device1234
```

## After Deploying a Thing
Once an AWS IoT Thing was provisioned, I needed to collect the necessary certificate details for my Arduino project. First, get the root certificate authority certificate under which all AWS IoT certificates are created.
```
$ curl -s https://www.amazontrust.com/repository/AmazonRootCA1.pem
```

Next, get the certificate provisioned by the AWS IoT service for your Thing.
```
$ IOT_CERT=$(aws cloudformation describe-stacks --stack-name poolcontroller1 \
    --query "Stacks[0].Outputs[?OutputKey=='CertificateId'].OutputValue" --output text)

$ aws iot describe-certificate --certificate-id $IOT_CERT
    --query "certificateDescription.certificatePem" --output text
```
_(Note: Replace `poolcontroller1` with the name of your Thing)_

Then, retrieve the private key for your certificate from AWS Secrets Manager.
```
$ KEY_SECRET=$(aws cloudformation describe-stacks --stack-name poolcontroller1 \
    --query "Stacks[0].Outputs[?OutputKey=='SecretId'].OutputValue" --output text)

$ aws secretsmanager get-secret-value --secret-id $KEY_SECRET \
    --query "SecretString" --output text | jq -r ".privateKey"
```
_(Note: Again, replace `poolcontroller1` with the name of your Thing)_

P.S. You may also need to know your AWS IoT MQQT endpoint used to publish messages.
```
$ aws iot describe-endpoint --output text
```

## Notes
1. To delete a stack, you must first set its certificate status to `INACTIVE` and re-run `cdk deploy` to update the stack. Then you can run `cdk destroy` against it. In `thingstack.py`:
```
cert = aws_iot.CfnCertificate(..., status="INACTIVE")
```
2. If you're using the above certificates in an Arduino project you'll need to specify the certificate details in your `.ino` file in a specific format. Append the following `awk` command to the above certificate printing commands in order to help with this formatting: `| awk '{print "\"" $0 "\\n\" \\"}'`

## Resources
These sites were helpful in making this project successful:
* https://cryptography.io/en/latest/x509/tutorial/#creating-a-certificate-signing-request-csr
* https://docs.aws.amazon.com/cdk/api/latest/python/modules.html
* https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_IoT.html
* https://docs.aws.amazon.com/iot/latest/developerguide/managing-device-certs.html
* https://github.com/aws-samples/aws-cdk-examples/tree/master/python

## To Do
1. Define the minimally required permission set to deploy/destroy stacks with this project.