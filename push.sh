python3 -m build
aws codeartifact login --tool twine --repository eop --domain promethee-earth --domain-owner 724395993532 --region eu-west-3
twine upload --repository codeartifact dist/*