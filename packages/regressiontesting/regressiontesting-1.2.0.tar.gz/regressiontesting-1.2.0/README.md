# RegressionTesting
# Copyright (c) 2025 Lionel Guo
# Author: Lionel Guo
# Email: lionelliguo@gmail.com
# GitHub: https://github.com/lionelliguo/regressiontesting

## Overview
`RegressionTesting` is a Python package for automating regression testing with Google Sheets. This package allows you to:

- Fetch and compare HTTP headers using `curl` commands stored in Google Sheets.
- Process these commands and store results (pass/fail) in Google Sheets.
- Automatically manage the testing process using batch updates and configurable settings.

## Requirements
- Python 3.x
- `pip install gspread google-auth google-auth-oauthlib`
- `curl` command-line tool
- A valid Google Service Account JSON key

## Setup

1. Clone this repository.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
