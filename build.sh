#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

export FLASK_APP=main.py

# Run migrations to ensure database tables are up to date
flask db upgrade || echo "Database migrations will run at container startup"
