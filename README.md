# ThingStack

## About

This project deploys the necessary [AWS IoT](https://aws.amazon.com/iot/) components for the provisioning of a Thing (Arduino, in my case) through [AWS CloudFormation](https://aws.amazon.com/cloudformation/) and the [AWS CDK](https://aws.amazon.com/cdk/) (Python). The project automatically generates a device certificate and uses [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) for storing for the device's private key. It can be reused to deploy and manage the lifecycle of multiple devices.

The inspiration for this project was twofold:
* First, I wanted to install an Arduino microcontroller by my pool in order to track its water temperature. For this I selected an [ESP32-based microcontroller](https://www.amazon.com/dp/B0718T232Z/ref=cm_sw_em_r_mt_dp_U_HlShDb8YN7AT7) and [DS18B20-based temperature sensor](https://www.amazon.com/dp/B01MY8U394/ref=cm_sw_em_r_mt_dp_U_kmShDbWT4C6YH). The code I wrote for the Arduino to be able to connect to wifi and publish to the AWS IoT MQQT endpoint is here: [Arduino ESP32 Temperature Logger to AWS IoT](https://github.com/edsw/ESP32-TempLogger-AWS-IoT).
* Second, I wanted to experiment with AWS CDK's Python support.

## Prerequisites
Install AWS CLI, AWS CDK, and [jq](https://formulae.brew.sh/formula/jq). For example, on macOS with [brew](https://brew.sh/):
```
$ brew install awscli npm jq
$ npm install -g aws-cdk
```
I have tested this on:
* macOS Mojave (10.14.5) and Catalina (10.15.4)
* Python 3.7.2 and 3.8.2
* AWS CDK 0.36, 1.0, and 1.37.0

## Setup
First, configure your AWS CLI with with the necessary permissions to deploy an AWS IoT stack in CloudFormation. I have an IAM User configured with a policy allowing it only to assume a single role that has the AWS managed policy `IAMReadOnlyAccess` attached, along with the below customer managed policy:
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

I configure my CLI environment with the IAM user's Access Key and Secret Access Key.
```
aws configure
```

I then create a Named Profile to reference my Role's ARN.
```
 cat ~/.aws/config
...
[profile thingstack]
role_arn = arn:aws:iam::123456789012:role/ThingStack-Role
source_profile = default
region = us-east-2
...
```
_(Note: replace the role_arn with your specific Role ARN.)_

Then, clone this project and install the project prerequisites:
```
$ cd /Directory/Of/Choice
$ git clone https://github.com/edsw/ThingStack.git
$ python setup.py install
```

Lastly, create/edit the file `cdk.json` to include the default context variables used in provisioning the stack. I have intentionally left this file out of my repository since it contains my AWS IAM Role ARN. This JSON file includes the name of your AWS IoT Thing (`thing_name`), the JSON policy that applies to your Thing (`policy_file`), the IAM Role ARN that is assumed by the code (`role_arn`), and the AWS region where you are deploying IoT resources (`region`).

```
$ cat cdk.json 
{
    "app": "python3 app.py",
    "context": {
        "thing_name": "poolcontroller1",
        "policy_file": "policy.json",
        "role_arn": "arn:aws:iam::<account-id>:role/<role-name>",
        "region": "us-east-2"
    }
}
```

## Deploy a Thing
To use the values from `cdk.json` and the Named Policy `thingstack`:
```
$ cdk deploy --profile thingstack
```

To specify alternatives on the command line:
```
$ cdk deploy --context thing_name=device1234 --profile thingstack
```

## After Deploying a Thing
Once an AWS IoT Thing was provisioned, I needed to collect the necessary certificate details for my Arduino project. Note that in the below examples I specify the Named Profile I'm assuming via the `--profile thingstack` argument.

First, get the root certificate authority certificate under which all AWS IoT certificates are created.
```
$ curl -s https://www.amazontrust.com/repository/AmazonRootCA1.pem
```

Next, get the certificate provisioned by the AWS IoT service for your Thing.
```
$ IOT_CERT=$(aws cloudformation describe-stacks --profile thingstack --stack-name poolcontroller1 \
    --query "Stacks[0].Outputs[?OutputKey=='CertificateId'].OutputValue" --output text)

$ aws iot describe-certificate --profile thingstack --certificate-id $IOT_CERT \
    --query "certificateDescription.certificatePem" --output text
```
_(Note: Replace `poolcontroller1` with the name of your Thing)_

Then, retrieve the private key for your certificate from AWS Secrets Manager.
```
$ KEY_SECRET=$(aws cloudformation describe-stacks --profile thingstack --stack-name poolcontroller1 \
    --query "Stacks[0].Outputs[?OutputKey=='SecretId'].OutputValue" --output text)

$ aws secretsmanager get-secret-value --profile thingstack --secret-id $KEY_SECRET \
    --query "SecretString" --output text | jq -r ".privateKey"
```
_(Note: Again, replace `poolcontroller1` with the name of your Thing)_

P.S. You may also need to know your AWS IoT MQQT endpoint used to publish messages.
```
$ aws iot describe-endpoint --profile thingstack --output text
```

## Notes
1. To delete a stack, you must first set its certificate status to `INACTIVE` and re-run `cdk deploy` to update the stack. Then you can run `cdk destroy [--context thing_name=]` against it. In `thingstack.py`:
```
cert = aws_iot.CfnCertificate(..., status="INACTIVE")
```
2. If you're using the above certificates in an Arduino project as I did, you'll need to specify the certificate details in your source code in a specific format. Append the following `awk` command to the above certificate printing commands in order to help with this formatting: `| awk '{print "\"" $0 "\\n\" \\"}'`

## Resources
These sites were helpful in making this project successful:
* https://cryptography.io/en/latest/x509/tutorial/#creating-a-certificate-signing-request-csr
* https://docs.aws.amazon.com/cdk/api/latest/python/modules.html
* https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_IoT.html
* https://docs.aws.amazon.com/iot/latest/developerguide/managing-device-certs.html
* https://github.com/aws-samples/aws-cdk-examples/tree/master/python

## To Do
1. Define the minimally required permission set to deploy/destroy stacks with this project.
2. ~~Publish sister project with Arduino code~~ [DONE](https://github.com/edsw/ESP32-TempLogger-AWS-IoT)