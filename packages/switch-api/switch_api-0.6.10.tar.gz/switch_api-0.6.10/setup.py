# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Import required functions
from setuptools import setup, find_packages

# Call setup function
setup(
    author="Switch Automation Pty Ltd.",
    description="A complete package for data ingestion into the Switch Automation Platform.",
    long_description=open('README.md', 'r').read() +
    '\n\n' + open('HISTORY.md', 'r').read(),
    long_description_content_type='text/markdown',
    license='MIT License',
    name="switch_api",
    version="0.6.10",
    packages=find_packages(include=["switch_api", "switch_api.*"]),
    install_requires=['pandas==1.5.3', 'requests', 'azure-storage-blob', 'pandera[io]==0.7.1', 'azure-servicebus',
                      'msal>=1.11.0', 'paho-mqtt==1.6.1', 'uvicorn==0.22.0', 'fastapi==0.98.0', 'pyodbc==4.0.39', 'cachetools==5.5.0', 
                      'numexpr==2.10.2'],
    python_requires=">=3.8.0",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Other Audience',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Natural Language :: English',
    ]
)
