#!/bin/bash
set -e

CONF_DIR=/root/Dr-referral/Dr-referral-tracker/conf
WSGI_FILE=${CONF_DIR}/wsgi.py
if [ ! -e "$WSGI_FILE" ]; then
    echo "Expected to find $WSGI_FILE"
    exit 1
fi

pushd ${CONF_DIR} >> /dev/null

exec gunicorn -c gunicorn_app.conf wsgi:application

popd >> /dev/null
