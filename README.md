# ThingStack

## Prerequisites
```
$ brew install awscli npm jq
$ npm -i -g aws-cdk
```

## Setup
```
$ cd /Directory/Of/Choice
$ git clone <url>
$ pip install -r requirements.txt
```

## Execution
```
$ cdk deploy
$ cdk deploy --context thing_name=pool1
```

## Post
```
$ curl -s https://www.amazontrust.com/repository/AmazonRootCA1.pem

$ IOT_CERT=$(aws cloudformation describe-stacks --stack-name poolcontroller1 --query "Stacks[0].Outputs[?OutputKey=='CertificateId'].OutputValue" --output text)
$ aws iot describe-certificate --certificate-id $IOT_CERT --query "certificateDescription.certificatePem" --output text

$ KEY_SECRET=$(aws cloudformation describe-stacks --stack-name poolcontroller1 --query "Stacks[0].Outputs[?OutputKey=='SecretId'].OutputValue" --output text)
$ aws secretsmanager get-secret-value --secret-id $KEY_SECRET --query "SecretString" --output text | jq -r ".privateKey"

$ aws iot describe-endpoint --output text
```

## Resources
* https://cryptography.io/en/latest/x509/tutorial/#creating-a-certificate-signing-request-csr
* https://docs.aws.amazon.com/cdk/api/latest/python/modules.html
* https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_IoT.html
* https://docs.aws.amazon.com/iot/latest/developerguide/managing-device-certs.html
* https://github.com/aws-samples/aws-cdk-examples/tree/master/python

## Notes
1. To delete stack, you must first set the certificate status to INACTIVE and `cdk deploy` to update the stack.
2. Append to certificate printing commands for format required by Arduino: `| awk '{print "\"" $0 "\\n\" \\"}'`