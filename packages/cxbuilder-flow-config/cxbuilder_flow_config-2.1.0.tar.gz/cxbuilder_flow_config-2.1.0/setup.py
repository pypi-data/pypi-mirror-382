import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cxbuilder-flow-config",
    "version": "2.1.0",
    "description": "Amazon Connect third-party app for configuring variables and prompts in Connect contact flows",
    "license": "MIT",
    "url": "https://github.com/cxbuilder/flow-config#readme",
    "long_description_content_type": "text/markdown",
    "author": "CXBuilder<ivan@cxbuilder.ai>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cxbuilder/flow-config.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cxbuilder_flow_config",
        "cxbuilder_flow_config._jsii"
    ],
    "package_data": {
        "cxbuilder_flow_config._jsii": [
            "flow-config@2.1.0.jsii.tgz"
        ],
        "cxbuilder_flow_config": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib==2.194.0",
        "constructs>=10.0.0, <11.0.0",
        "jsii>=1.112.0, <2.0.0",
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
        "License :: OSI Approved",
        "Framework :: AWS CDK",
        "Framework :: AWS CDK :: 2"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
