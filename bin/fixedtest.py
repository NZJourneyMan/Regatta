#!/usr/bin/python3

import os, sys, json
from pprint import pprint

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../lib')))

from saillib import Regatta

allSeries = {
    'Autumnal 2019': {
        'Round 1': [
            {'crew': ('Ken', 'Mark'),
            'races': [1, 2, 2, 1],
            'boatNum': '24',
            },
            {'crew': ('Emilio', 'Clare'),
            'races': [2, 5, 1, 3],
            'boatNum': '18',
            },
            {'crew': ('Evan', 'Lazlo'),
            'races': [4, 1, 4, 5],
            'boatNum':'22',
            },
            {'crew': ('Saj', 'Chris'),
            'races': [3, 3, 3, 4],
            'boatNum': '16'
            },
            {'crew': ('Anthony Dauppe',),
            'races': ['DNS', 4, 5, 2],
            'boatNum': '21',
            },
        ],
        'Round 2': [
            {'crew': ('Kentaro', 'Clare'),
            'races': [3, 2, 1, 1],
            'boatNum': '18',
            },
            {'crew': ('Ken', 'Mark'),
            'races': [1, 1, 4, 3],
            'boatNum': '20',
            },
            {'crew': ('Emilio', 'Furold'),
            'races': [6, 7, 7, 6],
            'boatNum': '4',
            },
            {'crew': ('Evan', 'Sean'),
            'races': [7, 4, 3, 2],
            'boatNum': '22',
            },
            {'crew': ('Matt', 'Amanda G'),
            'races': [5, 5, 2, 4],
            'boatNum': '17',
            },
            {'crew': ('Amanda C', 'Chris'),
            'races': [2, 3, 5, 7],
            'boatNum': '15',
            },
            {'crew': ('Saj', 'Maria'),
            'races': [8, 8, 6, 5],
            'boatNum': '16',
            },
            {'crew': ('Andrew',),
            'races': [4, 6, 'DNS', 'DNS'],
            'boatNum': '14',
            },
        ],
        'Round 3': [
            {'crew': ('Kentaro', 'Clare'),
            'races': [2, 1, 2, 1],
            'boatNum': '18',
            },
            {'crew': ('Albert',),
            'races': [4, 4, 4, 3],
            'boatNum': '17',
            },
            {'crew': ('Ken', 'Mark'),
            'races': [1, 2, 1, 2],
            'boatNum': '20',
            },
            {'crew': ('Saj', 'Amanda G'),
            'races': [3, 3, 3, 4],
            'boatNum': '22',
            },
        ],
        'Round 4': [
            {'crew': ('Kentaro', 'Clare'),
            'races': [4, 1, 1, 1],
            'boatNum': 'x',
            },
            {'crew': ('Ken', 'Mark'),
            'races': [2, 4, 4, 2],
            'boatNum': '22',
            },
            {'crew': ('Saj', 'Stephan'),
            'races': [1, 5, 2, 5],
            'boatNum': 'x',
            },
            {'crew': ('Amanda G', 'Evan'),
            'races': [3, 2, 3, 3],
            'boatNum': 'x',
            },
            {'crew': ('Raquel', 'Soraia'),
            'races': [6, 3, 5, 6],
            'boatNum': 'x',
            },
            {'crew': ('Maria', 'Richard'),
            'races': [5, 6, 6, 4],
            'boatNum': 'x',
            },
        ]
    },
    'Frostbite 2020': {
        'Round 1': [
            # 'Weather': 'Sunny NNW 3 - 12 kt'
            # 'Date': '2020/01/19'
            # 'Comment': ''
            {'crew': ('Clare', 'Maria'),
            'races': [2, 2, 2, 1],
            'boatNum': '18',
            },
            {'crew': ('Lazlo', 'Evan'),
            'races': [5, 3, 3, 4],
            'boatNum':'13',
            },
            {'crew': ('Teemu', 'Slava'),
            'races': [4, 4, 4, 3],
            'boatNum': '20',
            },
            {'crew': ('Mark', 'Ken'),
            'races': [1, 1, 1, 2],
            'boatNum': '10',
            },
            {'crew': ('Raquel', 'Soraia'),
            'races': [3, 5, 5, 5],
            'boatNum': '5',
            },
        ],
        'Round 2': [
            # 'Weather': 'Sunny W 8 - 25 kt'
            # 'Date': '2020/02/02'
            # 'Comment': ''
            {'crew': ('Raquel', 'Soraia'),
            'races': [4, 'DNF', 'DNS', 'DNS'],
            'boatNum': '6',
            },
            {'crew': ('Kentaro', 'Clare'),
            'races': [1, 2, 1, 2],
            'boatNum':'18',
            },
            {'crew': ('Chris', 'Teemu'),
            'races': [3, 3, 2, 3],
            'boatNum': '11',
            },
            {'crew': ('Mark', 'Ken'),
            'races': [2, 1, 3, 1],
            'boatNum': '22',
            },
        ],
        'Round 3': [
            # 'Weather': 'Rainy WNW 12 - 30 kt'
            # 'Date': '2020/02/17'
            # 'Comment': ''
            {'crew': ('Alex', 'Emilio'),
            'races': [1, 1, 3, 1],
            'boatNum': '22',
            },
            {'crew': ('Mark', 'Ken'),
            'races': [2, 2, 2, 2],
            'boatNum':'20',
            },
            {'crew': ('Evan', 'Lazlo'),
            'races': [4, 4, 4, 3],
            'boatNum': '13',
            },
            {'crew': ('Chris', 'Teemu'),
            'races': [3, 3, 1, 4],
            'boatNum': '24',
            },
        ],
        'Round 4': [
            # 'Weather': 'Rainy WSW 15 - 25 kt'
            # 'Date': '2020/03/01'
            # 'Comment': ''
            {'crew': ('Clare', 'Emilio', 'Maria'),
            'races': [2, 3, 2, 3],
            'boatNum': '21',
            },
            {'crew': ('Raquel', 'Soraia'),
            'races': [4, 4, 4, 4],
            'boatNum':'8',
            },
            {'crew': ('Chris', 'Teemu'),
            'races': [3, 1, 3, 1],
            'boatNum': '11',
            },
            {'crew': ('Ken', 'Mark'),
            'races': [1, 2, 1, 2],
            'boatNum': '23',
            },
        ],
    },
    '2.6 Practice': {
        'Single Round': [
            # 'Weather': 'Indoor - who cares!'
            # 'Date': '2020/04/26'
            # 'Comment': 'Virtual Regatta'
            {'crew': ('Tera-fying Sailor',),
            'races': [2, 7, 4, 2, 1, 1],
            'boatNum': None,
            },
            {'crew': ('Topper4life',),
            'races': [1, 1, 5, 3, 3, 3],
            'boatNum': None,
            },
            {'crew': ('NZJourneyMan',),
            'races': ['DNS', 2, 2, 1, 5, 2],
            'boatNum': None,
            },
            {'crew': ('Albert Peiro',),
            'races': [3, 4, 3, 6, 7, 6],
            'boatNum': None,
            },
            {'crew': ('Flying Carrot',),
            'races': [5, 6, 1, 4, 'DNS', 'DNS'],
            'boatNum': None,
            },
            {'crew': ('EatMyWake',),
            'races': [7, 3, 7, 11, 6, 5],
            'boatNum': None,
            },
            {'crew': ('Fluffy0069',),
            'races': [8, 'DNS', 8, 8, 2, 4],
            'boatNum': None,
            },
            {'crew': ('Boat46368',),
            'races': [4, 5, 6, 7, 8, 9],
            'boatNum': None,
            },
            {'crew': ('Lynx Ore',),
            'races': ['DNS', 'DNS', 10, 5, 4, 7],
            'boatNum': None,
            },
            {'crew': ('Lady B',),
            'races': [6, 'DNS', 9, 9, 'DNS', 8],
            'boatNum': None,
            },
            {'crew': ('Blackheath',),
            'races': ['DNS', 'DNS', 'DNS', 10, 9, 10],
            'boatNum': None,
            },
        ],
    },
}


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


def addRound(roundObj, roundName, results):
    roundObj.addRound(results, roundName)

    for i in range(len(results[0]['races'])):
        raceResults = {}
        for boat in results:
            raceResults[boat['crew']] = boat['races'][i]
        try:
            roundObj.addRace(roundName, raceResults, checkRace=True)
        except ValueError as e:
            pprint(results)
            print('Error: {}'.format(e))
            sys.exit(1)


def main():

    for seriesName, series in allSeries.items():
        if seriesName != '2.6 Practice':
            continue

        # Create each series
        sRound = Regatta(name=seriesName, roundDiscardsType='fixed', roundDiscardsNum=1,
                        seriesDiscardsType='fixed', seriesDiscardsNum=4)
        # Add each round to the DB
        for roundName, round in series.items():
            addRound(sRound, roundName, round)

            print(f'\n {roundName}')
            pprint(sRound.rounds)
            pprint(sRound.roundsIdx)

        pprint(sRound.getSeriesResults())
        # db.saveSeries(seriesName, json.dumps({
        #     'rounds': sRound.rounds,
        #     'roundsIdx': sRound.roundsIdx
        # }))

#     # =======================================================

#     sRound = Regatta(name=name, roundDiscardsType='fixed', roundDiscardsNum=1,
#                    seriesDiscardsType='fixed', seriesDiscardsNum=4)

#     addRound(sRound, 'Round1', round1)
#     print(' Round 1')
# #     print(json.dumps(sRound.getRoundResults('Round1'), indent=2))
# #     sys.exit()
#     doprint(sRound.getRoundResults('Round1'))

#     addRound(sRound, 'Round2', round2)
#     print('\n Round 2')
#     doprint(sRound.getRoundResults('Round2'))

#     addRound(sRound, 'Round3', round3)
#     print('\n Round 3')
#     doprint(sRound.getRoundResults('Round3'))

#     addRound(sRound, 'Round4', round4)
#     print('\n Round 4')
#     doprint(sRound.getRoundResults('Round4'))

#     print('\n Series Results')  # (Interim after 3 rounds)')
#     doprint(sRound.getSeriesResults(), includeRaces=True)
#     print()
#     print('() = Discard, [] = DNx, ** = DNx & Discard')

    '''
    Todo!
    1. Update scoring:
        a. DNC (Did Not Compete) to the round is scored as the number of boats in the series + 1
        b. DNS/DNF is scored as the number of boats in the round + 1
        c. Duplicates are allowed after penalties, etc are factored in. Meh. Maybe add in an
           override flag. The idea being it could be used after an initial refusal.
    2. Update calcDNx to change the max score and add in calculation for DNC
    3. Allow numBoats override when calling getResults() to allow for calculating individual results.
    4. Write results to DB (Sqlite JSON) after adding crews and after each race.
    5. Read results from DB when instantiating the Regatta() class.
    6. calcCBPlaces should not consider discarded races (I think this is the wrong decision by the racing world!)
    '''


if __name__ == '__main__':
    sys.exit(main())
