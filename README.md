
# Python

Prerequisites
```
$ brew install awscli npm jq
$ npm -i -g aws-cdk
```

Setup
```
$ pip install -r requirements.txt
```

Post
```
$ IOT_CERT=$(aws cloudformation describe-stacks --stack-name poolcontroller1 --query "Stacks[0].Outputs[?OutputKey=='CertificateId'].OutputValue" --output text)
$ aws iot describe-certificate --certificate-id $IOT_CERT --query "certificateDescription.certificatePem" --output text

$ KEY_SECRET=$(aws cloudformation describe-stacks --stack-name poolcontroller1 --query "Stacks[0].Outputs[?OutputKey=='SecretId'].OutputValue" --output text)
$ aws secretsmanager get-secret-value --secret-id $KEY_SECRET --query "SecretString" --output text | jq -r ".privateKey"

```

To delete, must first set Certificate Status -> INACTIVE

Resources
https://cryptography.io/en/latest/x509/tutorial/#creating-a-certificate-signing-request-csr