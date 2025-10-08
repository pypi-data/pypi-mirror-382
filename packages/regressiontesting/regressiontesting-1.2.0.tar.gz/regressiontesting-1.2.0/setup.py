# RegressionTesting
# Copyright (c) 2025 Lionel Guo
# Author: Lionel Guo
# Email: lionelliguo@gmail.com
# GitHub: https://github.com/lionelliguo/regressiontesting

from setuptools import setup, find_packages

setup(
    name="regressiontesting",
    version="1.2.0",  # Update the version number
    description="A Python package for regression testing with Google Sheets integration.",
    long_description=open('README.md').read(),  # Read the contents of README.md
    long_description_content_type="text/markdown",
    author="Lionel Guo",
    author_email="lionelliguo@gmail.com",
    url="https://github.com/lionelliguo/regressiontesting",  # Your package URL
    packages=find_packages(),  # Automatically finds all the packages in your project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",  # Change to Apache License
        "Operating System :: OS Independent",
    ],
    install_requires=[  # Add dependencies your package needs
        'gspread',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'twine',
    ],
    python_requires='>=3.6',  # You can specify the minimum version of Python required
    include_package_data=True,  # Include additional files (e.g., README, license, etc.)
    license="Apache 2.0",  # Set the license type
)
