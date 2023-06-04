#!/bin/sh

set -e

# if running as root & command specified in CMD is python
if [ "$(id -u)" = "0" ] && [ "$1" = "python" ] && [ "$2" = "app.py" ]; then
    # make sure permissions are set correctly
    chown -R aryon:aryon /app
    cd /app
    # run command (verified to be `python app.py`) as aryon user
    exec su-exec aryon "$@"
fi

exec "$@"
