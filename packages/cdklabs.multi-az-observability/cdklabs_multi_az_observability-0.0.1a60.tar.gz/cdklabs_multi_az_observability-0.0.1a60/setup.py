import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdklabs.multi-az-observability",
    "version": "0.0.1.a60",
    "description": "A CDK construct for implementing multi-AZ observability to detect single AZ impairments",
    "license": "Apache-2.0",
    "url": "https://github.com/cdklabs/cdk-multi-az-observability",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services<aws-cdk-dev@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-multi-az-observability/"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdklabs.multi_az_observability",
        "cdklabs.multi_az_observability._jsii"
    ],
    "package_data": {
        "cdklabs.multi_az_observability._jsii": [
            "multi-az-observability@0.0.1-alpha.60.jsii.tgz"
        ],
        "cdklabs.multi_az_observability": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.189.1, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
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
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
