
# Python

Prerequisites
```
$ brew install awscli openssl npm
$ npm -i -g aws-cdk
```

Setup
```
$ openssl req -nodes -newkey rsa:2048 -keyout privkey.pem -out csr.pem -subj "/CN=AWS IoT Certificate"

$ pip install -r requirements.txt
```

Post
```
$ IOT_CERT=$(aws cloudformation describe-stacks --stack-name poolcontroller1 --query "Stacks[0].Outputs[?OutputKey=='CertificateId'].OutputValue" --output text)

$ aws iot describe-certificate --certificate-id $IOT_CERT --query "certificateDescription.certificatePem" --output text
```

To delete, must first set Certificate -> Inactive