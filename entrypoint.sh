#!/bin/sh

set -e

# if running as root & command specified in CMD is python
if [ "$(id -u)" = "0" ] && [ "$1" = "python" ]; then
    # make sure permissions are set correctly
    chown -R aryon:aryon /app
    cd /app
    # run command specified in CMD (verified to be python) as aryon user
    exec su-exec aryon "$@"
fi

exec "$@"
