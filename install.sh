#!/usr/bin bash

MAJOR_PYTHON_VERSION=$(python -c 'import sys; print(sys.version_info[:][0])')
MINOR_PYTHON_VERSION=$(python -c 'import sys; print(sys.version_info[:][1])')

if [[ $MAJOR_PYTHON_VERSION -lt 3 || $MINOR_PYTHON_VERSION -lt 6 ]]; then
echo "Update your python interpreter to version 3.6 or higher."
exit 1
fi

pip install virtualenv
virtualenv env
source ./env/bin/activate
if [[ ! $? -eq 0 ]]; then
    exit 1
fi

pip install -r requirements.txt