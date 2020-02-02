#!/usr/bin/env python3

import sys
import os

LIBDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
BINDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'bin'))
sys.path += [LIBDIR, BINDIR]
from saillib import Regatta, SeriesDB


from fixedtest import allSeries, addRound

# series = allSeries['Frostbite_2020']
# for roundName, round in series.items():
#     addRound(sRound, roundName, round)

def pickleData(allSeries):
    import pickle, pprint

    db = {}
    for seriesName, series in allSeries.items():
        sRound = Regatta(name=seriesName, roundDiscardsType='fixed', roundDiscardsNum=1,
                        seriesDiscardsType='fixed', seriesDiscardsNum=4)
        for roundName, round in series.items():
            addRound(sRound, roundName, round)

        db[seriesName] = {
            'rounds': sRound.rounds,
            'roundsIdx': sRound.roundsIdx
        }
        

    pprint.pprint(db)

    with open('db.pickle', 'wb') as fh:
        pickle.dump(db, fh)

pickleData(allSeries)

