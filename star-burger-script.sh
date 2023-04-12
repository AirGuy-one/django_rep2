#!/bin/bash
# This bash script is for uploading updates to the server

set -e -o pipefail

cd /opt/django_rep2/
source venv/bin/activate
git pull
pip install -r requirements.txt
npm ci --dev
python3 manage.py makemigrations
python3 manage.py migrate
echo "yes" | python3 manage.py collectstatic
systemctl reload star-burger
echo "The script has been successfully completed!"
