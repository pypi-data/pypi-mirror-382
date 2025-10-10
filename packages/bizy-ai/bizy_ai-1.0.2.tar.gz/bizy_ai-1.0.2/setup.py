#!/usr/bin/env python3
"""Setup script for business-agent CLI"""

from setuptools import setup, find_packages

setup(
    name='bizy-ai',
    version='1.0.2',
    description='AI-powered business planning and execution agent',
    author='Reid Chatham',
    packages=find_packages(),
    install_requires=[
        'anthropic>=0.18.0',
        'schedule>=1.2.0',
        'python-dotenv>=1.0.0',
        'pyyaml>=6.0',
        'sqlalchemy>=2.0.0',
        'requests>=2.31.0',
        'beautifulsoup4>=4.12.0',
        'pandas>=2.0.0',
        'rich>=13.0.0',
        'python-dateutil>=2.8.2',
        'click>=8.1.0',
        'jinja2>=3.1.2',
    ],
    entry_points={
        'console_scripts': [
            'bizy=agent.cli:cli',
        ],
    },
    python_requires='>=3.8',
)
