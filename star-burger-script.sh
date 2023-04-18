#!/bin/bash
# This bash script is for uploading updates to the server

set -e -o pipefail

cd /opt/django_rep2/
source venv/bin/activate
git pull
pip install -r requirements.txt
npm ci --dev
python3 manage.py migrate
python3 manage.py collectstatic --no-input
systemctl reload star-burger

access_token="71fcf0f288e641d9ba832a19d635b2b5"
revision="git SHA"
local_username="root server user"
comment="deploy was successfully"

curl -X POST \
     -H "X-Rollbar-Access-Token: $access_token" \
     -H "Content-Type: application/json" \
     -d '{"environment": "production", "revision": "'"$revision"'", "local_username": "'"$local_username"'", "comment": "'"$comment"'"}' \
     https://api.rollbar.com/api/1/deploy

echo -e "\nThe script has been successfully completed!"
