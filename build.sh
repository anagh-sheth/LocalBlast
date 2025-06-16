#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Collect static files
python src/manage.py collectstatic --no-input

# Pull vendor files
python src/manage.py vendor_pull

# Run migrations
python src/manage.py migrate
