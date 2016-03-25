#!/bin/bash
set -e

pushd /root/Dr-referral/Dr-referral-tracker/ >> /dev/null

# Set up Django app
sudo -u app_user python manage.py syncdb --noinput
sudo -u app_user python manage.py collectstatic --noinput

popd >> /dev/null

# Start supervisor
/usr/bin/supervisord

# Allow users to provide their own start script
USER_START_SCRIPT=/root/Dr-referral/Dr-referral-tracker/scripts/start.sh
if [ -e "$USER_START_SCRIPT" ]; then
    source ${USER_START_SCRIPT}
fi

# Run bash as container command
/bin/bash
