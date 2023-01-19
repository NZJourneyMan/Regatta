#!/bin/bash

ROOTDIR=$(dirname $0)

if [[ -f app.yaml ]]; then
    source venv/bin/activate
    eval "$(
        yq .env_variables < app.yaml | while read -r a b;do 
            echo "export ${a%:}=$b"
        done
    )"
    PORT=5000 eval "$(yq .entrypoint < app.yaml)"
else
    echo "Using DBs: $DATABASE_URL, $SERIES_COLLECTION_NAME, $USERS_COLLECTION_NAME"
    gunicorn \
        --reload \
        --reload-extra-file $ROOTDIR/static/dswc_leaderboard.js \
        --reload-extra-file $ROOTDIR/static/add_round.js \
        --reload-extra-file $ROOTDIR/templates/add_round.html \
        --bind 0.0.0.0:5000 \
        --access-logfile - \
        --log-file - \
        dswc_leaderboard:app
fi
