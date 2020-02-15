# Sailing Leader Board App for DSWC

## API Endpoints
* /api/v1.0/listSeries
* /api/v1.0/listRounds?seriesName=$seriesName
* /api/v1.0/getRoundResult?seriesName=$seriesName&roundName=$roundName
* /api/v1.0/getSeriesResult?seriesName=$seriesName

## Development

### Development, including the API backend

Ensure python3, venv and postgres are installed. At a guess greater than python 3.4 should do.

Clone this repository `git clone git@github.com:NZJourneyMan/Regatta.git`

cd into the new repo directory `cd Regatta`

Create a python3 virtual environment

`python3 -m venv venv/`

Create the database

`createdb regatta`

Activate the virtual environment

`./startenv`

Run `pip install -r requirements.txt`

Start up the local API with:

`./startapp.sh`

Browse to `http://localhost:5000`

Develop anything in the repo.

### Frontend development only

Clone this repository `git clone git@github.com:NZJourneyMan/Regatta.git`

cd into the new repo directory `cd Regatta`

You can now develop the front end files, principally:

* templates/index.html
* static/dswc_leaderboar.js

Use `file://<path to repo>/dev.html` to test in the browser. It is symlinked to templates/index.html but code in the javascript will detect the `dev` name and switch the API source to Heroku. 

Note: Heroku will take 8 seconds to supply data if it hasn't been accessed in the last 10 minutes.
