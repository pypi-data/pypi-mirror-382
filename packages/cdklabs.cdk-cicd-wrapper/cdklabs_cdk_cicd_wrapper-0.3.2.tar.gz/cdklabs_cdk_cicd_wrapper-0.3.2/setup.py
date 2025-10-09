import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdklabs.cdk-cicd-wrapper",
    "version": "0.3.2",
    "description": "This repository contains the infrastructure as code to wrap your AWS CDK project with CI/CD around it.",
    "license": "Apache-2.0",
    "url": "https://github.com/cdklabs/cdk-cicd-wrapper.git",
    "long_description_content_type": "text/markdown",
    "author": "CDK CI/CD Wrapper Team",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-cicd-wrapper.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdklabs.cdk_cicd_wrapper",
        "cdklabs.cdk_cicd_wrapper._jsii"
    ],
    "package_data": {
        "cdklabs.cdk_cicd_wrapper._jsii": [
            "cdk-cicd-wrapper@0.3.2.jsii.tgz"
        ],
        "cdklabs.cdk_cicd_wrapper": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.195.0, <3.0.0",
        "cdk-nag>=2.28.0, <3.0.0",
        "cdk-pipelines-github>=0.4.132, <0.5.0",
        "constructs>=10.3.0, <11.0.0",
        "jsii>=1.115.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
