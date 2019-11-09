#!/usr/bin/python3

import os, sys, json
from pprint import pprint

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../flask/lib')))
print(sys.path[-1] + " " + __file__)

from saillib import Regatta


def main():
    round1 = [
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
    ]
    round2 = [
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
         'boatNum': '18',
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
         'boatNum': 'Pico',
        },
    ]
    round3 = [
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
    ]
    round4 = [
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
        {'crew': ('Raquel', 'Soraya'),
         'races': [6, 3, 5, 6],
         'boatNum': 'x',
        },
        {'crew': ('Maria', 'Richard'),
         'races': [5, 6, 6, 4],
         'boatNum': 'x',
        },
    ]

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

    sRound = Regatta(roundDiscardsType='fixed', roundDiscardsNum=1,
                     seriesDiscardsType='fixed', seriesDiscardsNum=4)

    addRound(sRound, 'Round1', round1)
    print(' Round 1')
#     print(json.dumps(sRound.getRoundResults('Round1'), indent=2))
#     sys.exit()
    doprint(sRound.getRoundResults('Round1'))

    addRound(sRound, 'Round2', round2)
    print('\n Round 2')
    doprint(sRound.getRoundResults('Round2'))

    addRound(sRound, 'Round3', round3)
    print('\n Round 3')
    doprint(sRound.getRoundResults('Round3'))

    addRound(sRound, 'Round4', round4)
    print('\n Round 4')
    doprint(sRound.getRoundResults('Round4'))

    print('\n Series Results')  # (Interim after 3 rounds)')
    doprint(sRound.getSeriesResults(), includeRaces=True)
    print()
    print('() = Discard, [] = DNx, ** = DNx & Discard')

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
