#!/bin/bash

ROOTDIR=$(dirname $0)

echo "Using DB: $DATABASE_URL"
gunicorn \
    --reload \
    --reload-extra-file $ROOTDIR/static/dswc_leaderboard.js \
    --reload-extra-file $ROOTDIR/static/add_round.js \
    --reload-extra-file $ROOTDIR/templates/add_round.html \
    --bind 0.0.0.0:5000 \
    --access-logfile - \
    --log-file - \
    dswc_leaderboard:app
