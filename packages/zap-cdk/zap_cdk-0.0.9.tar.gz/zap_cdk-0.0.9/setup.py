import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "zap-cdk",
    "version": "0.0.9",
    "description": "zap-cdk",
    "license": "Apache-2.0",
    "url": "https://github.com/kesi03/zap-cdk",
    "long_description_content_type": "text/markdown",
    "author": "Kester Simm<68278724+kesi03@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/kesi03/zap-cdk"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "zap_cdk",
        "zap_cdk._jsii"
    ],
    "package_data": {
        "zap_cdk._jsii": [
            "zap-cdk@0.0.9.jsii.tgz"
        ],
        "zap_cdk": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
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
