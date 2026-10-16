#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Run migrations to ensure database tables are up to date
flask db upgrade
