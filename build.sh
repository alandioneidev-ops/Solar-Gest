#!/usr/bin/env bash
set -o errexit
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py seed_demo
