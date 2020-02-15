#!/bin/bash

echo "Using DB: $DATABASE_URL"
gunicorn --reload --bind 0.0.0.0:5000 --access-logfile - --log-file - dswc_leaderboard:app
