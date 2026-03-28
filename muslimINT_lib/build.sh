#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python muslimINT_lib/manage.py collectstatic --no-input