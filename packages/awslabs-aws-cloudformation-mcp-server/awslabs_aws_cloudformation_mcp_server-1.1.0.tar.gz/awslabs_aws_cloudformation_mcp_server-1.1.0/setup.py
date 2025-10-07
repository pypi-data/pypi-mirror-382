from setuptools import setup, find_packages
import os

setup(
    name="awslabs-aws-cloudformation-mcp-server",  # PyPI name
    version="1.1.0",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "aws-mcp-post-install = awslabs_aws_cloudformation_mcp_server.post_install:main",
        ],
    },
    description="AWS CloudFormation MCP server helper",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)

