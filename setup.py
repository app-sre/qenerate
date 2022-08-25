# -*- coding: utf-8 -*-
from setuptools import setup

packages = [
    "qenerate",
    "qenerate.core",
    "qenerate.plugins",
    "qenerate.plugins.pydantic_v1",
]

package_data = {"": ["*"]}

install_requires = ["graphql-core>=3.2,<4.0", "requests>=2.22,<3.0"]

entry_points = {"console_scripts": ["qenerate = qenerate.cli:run"]}

setup_kwargs = {
    "name": "qenerate",
    "version": "0.2.0",
    "description": "Code Generator for GraphQL Query Data Classes",
    "long_description": None,
    "author": "Service Delivery - AppSRE",
    "author_email": "sd-app-sre@redhat.com",
    "maintainer": "Service Delivery - AppSRE",
    "maintainer_email": "sd-app-sre@redhat.com",
    "url": "https://github.com/app-sre/qenerate",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "entry_points": entry_points,
    "python_requires": ">=3.9,<4.0",
}


setup(**setup_kwargs)
