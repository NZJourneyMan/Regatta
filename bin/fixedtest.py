#!/usr/bin/python3

import os, sys, json
from pprint import pprint

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../lib')))

from saillib import Regatta

allSeries = json.load(open(os.path.join(os.path.dirname(__file__), '../data/racedata.json')))

def doprint(results, includeRaces=True):
    strRaceFormat = '{:^4}'
    strFormat = ' {:15} {:>6} {:>5} {}'
    print(strFormat.format('Crew', 'Points', 'Place', 'Races' if includeRaces else ''))
    for boat in results:
        raceStrings = []
        for race in boat['races']:
            p = race['place']
            if race['discard'] and race['flag']:
                raceStr = strRaceFormat.format('*{}*'.format(p))
            elif race['discard']:
                raceStr = strRaceFormat.format('({})'.format(p))
            elif race['flag']:
                raceStr = strRaceFormat.format('[{}]'.format(p))
            else:
                raceStr = strRaceFormat.format('{}'.format(p))
            raceStrings.append(raceStr)

        racesString = ' '.join(raceStrings)
        print(strFormat.format(', '.join(boat['crew']),
                               boat['points'],
                               boat['place'],
                               racesString if includeRaces else ''))


def main():

    for series in allSeries:

        # Create each series
        sRound = Regatta()
        sRound.addSeries(name=series['name'], 
                         roundsDiscardType=series['roundsdiscardtype'], 
                         roundsDiscardNum=series['roundsdiscardnum'],
                         seriesDiscardType=series['seriesdiscardtype'], 
                         seriesDiscardNum=series['seriesdiscardnum'],
                         seriesStartDate=series['seriesStartDate'])
        # Add each round to the DB
        for round in series['rounds']:
            sRound.addRoundAll(round)

            print(f'\n{series["name"]} {round["name"]}')
            pprint(sRound.rounds)
            pprint(sRound.roundsIdx)

        pprint(sRound.getSeriesResults())

    '''
    Todo!
        o Duplicates are allowed after penalties, etc are factored in. Meh. Maybe add in an
          override flag. The idea being it could be used after an initial refusal.
    '''


if __name__ == '__main__':
    sys.exit(main())
