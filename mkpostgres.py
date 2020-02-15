#!/usr/bin/env python3

import sys
import os
import json
from pprint import pprint

LIBDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
BINDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'bin'))
sys.path += [LIBDIR, BINDIR]
# from saillib import Regatta, SeriesDB
from saillib import Regatta, PG_DB

db = PG_DB()


from fixedtest import allSeries, addRound

# series = allSeries['Frostbite_2020']
# for roundName, round in series.items():
#     addRound(sRound, roundName, round)

def loadPG(allSeries):

    db = PG_DB()
    print(f'Using DB: {os.environ["DATABASE_URL"]}')
    for seriesName, series in allSeries.items():
        sRound = Regatta(name=seriesName, roundDiscardsType='fixed', roundDiscardsNum=1,
                        seriesDiscardsType='fixed', seriesDiscardsNum=4)
        for roundName, round in series.items():
            addRound(sRound, roundName, round)

        # # pprint(sround.rounds)
        # # pprint(sround.roundsidx)
        db.saveSeries(seriesName, json.dumps({
            'rounds': sRound.rounds,
            'roundsIdx': sRound.roundsIdx
        }))



loadPG(allSeries)

