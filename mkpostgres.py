#!/usr/bin/env python3

import sys
import os
import json
from pprint import pprint

LIBDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
BINDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'bin'))
sys.path += [LIBDIR, BINDIR]

from saillib import Regatta, PG_DB

db = PG_DB()

allSeries = json.load(open(os.path.join(os.path.dirname(__file__), 'data/racedata.json')))

def loadPG(allSeries):

    db = PG_DB()
    print(f'Using DB: {os.environ["DATABASE_URL"]}')

    for series in allSeries:
        # Create each series
        sRound = Regatta()
        sRound.addSeries(name=series['name'], 
                         roundsDiscardType=series['roundsdiscardtype'],
                         roundsDiscardNum=series['roundsdiscardnum'],
                         seriesDiscardType=series['seriesdiscardtype'],
                         seriesDiscardNum=series['seriesdiscardnum'],
                         seriesStartDate=series['seriesstartdate'])
        # Add each round to the DB
        for round in series['rounds']:
            sRound.addRoundAll(round)

        # pprint(sround.rounds)
        # pprint(sround.roundsidx)
        db.saveSeries(series['name'], json.dumps(sRound.data))

    # Extract the sailor names from the races and add them to the DB
    for series in allSeries:
        for round in series['rounds']:
            for boat in round['boats']:
                for name in boat['crew']:
                    db.saveUser(name)

loadPG(allSeries)

