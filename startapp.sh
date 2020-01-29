#!/bin/bash

source /home/mark/repos/dswc-results/venv/bin/activate
export DATABASE_URL=bob
gunicorn --reload --bind 0.0.0.0:5000 --access-logfile - --log-file - dswc_leaderboard:app
