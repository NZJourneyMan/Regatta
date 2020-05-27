#!/bin/bash

ROOTDIR=$(dirname $0)

echo "Using DB: $DATABASE_URL"
gunicorn \
    --reload \
    --reload-extra-file $ROOTDIR/static/dswc_leaderboard.js \
    --bind 0.0.0.0:5000 \
    --access-logfile - \
    --log-file - \
    dswc_leaderboard:app
