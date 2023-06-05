#!/bin/bash
# This bash script is for uploading updates to the server

set -e -o pipefail

cd /opt/django_rep2/
git pull
cd infra/
sudo docker-compose -f docker-compose-prod.yml up -d --build

access_token="${ACCESS_TOKEN}"
revision=$(git rev-parse HEAD)
local_username="root server user"

curl -X POST \
     -H "X-Rollbar-Access-Token: $access_token" \
     -H "Content-Type: application/json" \
     -d '{"environment": "production", "revision": "'"$revision"'", "local_username": "'"$local_username"'", "comment": "'"$comment"'"}' \
     https://api.rollbar.com/api/1/deploy

echo -e "\nThe script has been successfully completed!"

comment="deploy was successfully"
