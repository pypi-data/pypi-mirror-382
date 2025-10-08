#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    find_packages,
    setup,
)

extras_require = {
    'linter': [
        'ruff==0.13.2',
        'isort>=4.2.15,<5.4.3',
        'importlib-metadata<5.0',
    ],
    'dev': [
        'click==8.3.0',
        'freezegun==1.5.5',
        'mock==5.2.0',
        'pytest==8.4.2',
        'pytest-cov==7.0.0',
        'Random-Word==1.0.4',
        'twine==6.2.0',
    ],
    'hw-wallet': ['ledgerblue==0.1.47'],
}

extras_require['dev'] = (
    extras_require['linter'] + extras_require['dev'] + extras_require['hw-wallet']
)


setup(
    name='skale.py',
    version='7.5dev1',
    description='SKALE client tools',
    long_description_markdown_filename='README.md',
    author='SKALE Labs',
    author_email='support@skalelabs.com',
    url='https://github.com/skalenetwork/skale.py',
    include_package_data=True,
    install_requires=[
        'redis==6.4.0',
        'sgx.py==0.11dev0',
        'skale-contracts==2.0.0a6',
        'typing-extensions==4.15.0',
        'web3==7.13.0',
    ],
    python_requires='>=3.11,<4',
    extras_require=extras_require,
    keywords='skale',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.11',
    ],
)
