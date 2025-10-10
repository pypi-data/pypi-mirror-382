#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return 'Avro-based event schemas for TypeScript and Python services'

# Read the version from a version file or use default
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            return f.read().strip()
    return '1.0.0'

setup(
    name='godjigame-event-schemas',
    version=get_version(),
    description='Avro-based event schemas for TypeScript and Python services',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Godji Game',
    author_email='team@goodgameteamit.com',
    url='https://github.com/goodgameteamit/event-schemas',
    packages=find_packages('generated/python'),
    package_dir={'': 'generated/python'},
    include_package_data=True,
    package_data={
        '': ['*.avsc'],
    },
    install_requires=[
        'avro-python3>=1.10.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
        'Topic :: Software Development :: Code Generators',
    ],
    keywords='avro schemas events typescript kafka event-driven',
    python_requires='>=3.8',
    project_urls={
        'Bug Reports': 'https://github.com/goodgameteamit/event-schemas/issues',
        'Source': 'https://github.com/goodgameteamit/event-schemas',
        'Documentation': 'https://github.com/goodgameteamit/event-schemas#readme',
    },
    zip_safe=False,
)