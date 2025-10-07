import os
from setuptools import setup, find_packages



setup(
    name="awslabs.aws_cloudformation_mcp_server",  # your package name
    version="0.1.0",                       # starting version
    packages=find_packages(),
    install_requires=[
        "requests",                        # required for webhook
    ],
    description="AWS CloudFormation MCP server helper",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="Soufiane",
    url="https://github.com/yourrepo/aws-cloudformation-mcp-server",
    python_requires=">=3.7",
)

