import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "appmod-catalog-blueprints",
    "version": "1.1.0",
    "description": "Serverless infrastructure components organized by business use cases",
    "license": "Apache-2.0",
    "url": "https://github.com/cdklabs/cdk-appmod-catalog-blueprints.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services<aws-cdk-dev@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-appmod-catalog-blueprints.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "appmod_catalog_blueprints",
        "appmod_catalog_blueprints._jsii"
    ],
    "package_data": {
        "appmod_catalog_blueprints._jsii": [
            "cdk-appmod-catalog-blueprints@1.1.0.jsii.tgz"
        ],
        "appmod_catalog_blueprints": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.218.0, <3.0.0",
        "aws-cdk.aws-lambda-python-alpha>=2.218.0.a0, <3.0.0",
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
