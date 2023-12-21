#!/bin/bash

export ISPYB_ENVIRONMENT="test"

python -m pytest
flake8