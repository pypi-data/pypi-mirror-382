#!/bin/bash

aws_profile=$(aws configure list-profiles | grep devops)
if [ -z "$aws_profile" ]
then
    echo "The profile ${aws_profile} has not been established.  Using default."
    aws_profile="default"
else
    echo "AWS_PROFILE=${aws_profile}"
fi

uv sync --dev

uv build

AWS_PROFILE=$aws_profile aws --region=us-east-1 codeartifact login --tool twine \
    --domain shared-package-domain \
    --domain-owner 922539530544 \
    --repository shared-package-repository

# lists all compiled distributions, parses the version, sorts, and only keeps the last result.
latest_distribution=$(ls dist/dkany-*.tar.gz | awk -F"-" '{print $NF, $0}' | sort -V | tail -n 1 | awk '{print $2}')

echo "latest_distribution=${latest_distribution}"

uv run python -m twine upload --repository codeartifact $latest_distribution --verbose