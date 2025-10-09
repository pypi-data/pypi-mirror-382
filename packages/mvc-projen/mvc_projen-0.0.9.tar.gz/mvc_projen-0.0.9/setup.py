import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "mvc-projen",
    "version": "0.0.9",
    "description": "Base projen module for MV Consulting projects",
    "license": "Apache-2.0",
    "url": "https://github.com/MV-Consulting/mvc-projen",
    "long_description_content_type": "text/markdown",
    "author": "Manuel Vogel<8409778+mavogel@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/MV-Consulting/mvc-projen"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "mvc-projen",
        "mvc-projen._jsii"
    ],
    "package_data": {
        "mvc-projen._jsii": [
            "mvc-projen@0.0.9.jsii.tgz"
        ],
        "mvc-projen": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "constructs>=10.4.2, <11.0.0",
        "jsii>=1.115.0, <2.0.0",
        "projen==0.96.5",
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
