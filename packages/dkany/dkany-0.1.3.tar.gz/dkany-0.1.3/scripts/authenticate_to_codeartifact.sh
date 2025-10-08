#!/bin/bash -e
auth=$(aws --region=us-east-1 codeartifact get-authorization-token --domain shared-package-domain --domain-owner 922539530544 --query authorizationToken --output text)
touch .env
sed -i '/^CODEARTIFACT_TOKEN/d' .env
echo -e "\nCODEARTIFACT_TOKEN=$auth" >> .env
echo "Success!"
