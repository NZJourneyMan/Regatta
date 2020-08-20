import sys
import os
import json
import re

from copy import deepcopy


class PickleDB():
    dbFile = 'db.pickle'
    import pickle

    def __init__(self):
        if os.path.isfile(self.dbFile):
            self.db = self._readDB()
        else:
            self.db = {}

    def _readDB(self):
        with open(self.dbFile, 'rb') as fd:
            return pickle.load(fd)  # pylint:disable=undefined-variable

    def listSeries(self):
        return list(self.db)

    def getSeries(self, series):
        return self.db[series]

class DBError(Exception):
    pass

class PG_DB():

    def __init__(self):
        import psycopg2
        dbConnStr = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(dbConnStr)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        self._setupDB()

    def _setupDB(self):
        sql = """
            CREATE TABLE IF NOT EXISTS series (
                name TEXT PRIMARY KEY,
                jdata JSONB
            );
            CREATE INDEX IF NOT EXISTS i_seriesStartDate ON series (
                (jdata->'seriesStartDate')
            )
        """
        self.cur.execute(sql)
        sql = """
            CREATE TABLE IF NOT EXISTS people (
                name TEXT PRIMARY KEY
        )"""
        self.cur.execute(sql)

    def listSeries(self):
        sql = "select name from series order by jdata->'seriesStartDate'"
        self.cur.execute(sql)
        return [x[0] for x in self.cur.fetchall()]

    def getSeries(self, seriesName):
        sql = 'select jdata from series where name = %s'
        self.cur.execute(sql, (seriesName,))
        if self.cur.rowcount > 0:
            return self.cur.fetchone()[0]
        else:
            raise DBError(f'Series "{seriesName}" not found')

    def saveSeries(self, seriesName, data):
        '''
        Method takes the series name and the data and writes it to the database
        using UPSERT, it will either insert a new series, or update the existing
        series
        '''
        sql = '''
            insert INTO series (name, jdata) 
            VALUES (%s, %s) 
            ON CONFLICT (name) DO UPDATE SET jdata = EXCLUDED.jdata
        '''
        self.cur.execute(sql, (seriesName, data))

    def listUsers(self):
        sql = 'select name from people order by name'
        self.cur.execute(sql)
        return [x[0] for x in self.cur.fetchall()]

    def saveUser(self, user):
        sql = '''
            insert INTO people (name)
            VALUES (%s) 
            ON CONFLICT (name) DO NOTHING  /* very passive aggressive */
        '''
        self.cur.execute(sql, (user,))

    def __del__self(self):
        self.cur.close()
        self.conn.close()


class SeriesDB(PG_DB):
    pass


class Regatta(object):
    '''
    Data Structures:
    self.rounds = {     FIXME!
        [ lsit of dicts 
            'name': round name string,
            "seriessummarytype":  one of "allRaces" or "roundResults",
            roundsdiscardtype: discard type for each round string
            roundsdiscardnum: number of discards for each round
            seriesdiscardtype: discard type for each series summarising
            seriesdiscardnum: discard number for each series summarising
            'boats': [ list of dicts
                'crew', (tuple of crew names),
                'boatNum', 'boatname/number string',
                'races': [ list of race place records
                    'place': int,  # Should not be set in the DB if flag is used
                    'flag' : string,  # including DNS, DNF, DSQ & DNC
                    'discard': boolean,  # True if race was discarded. Not stored
                    'raceNum': int
                ]
            ]
        ]
    }
    self.roundsIdx = {
        Round_Name: {
            'idx': list index for self.rounds 
            'crews': Comma seperated sting of crew names: list index in self.rounds['boats'] 
        }

    }
    Notes: 
        1. DNS, DNF & DSQ so are scored as the number of boats in the *round* + 1
        2. DNC is scored as the max number of boats in the *series* + 1
        3. Any person that doesn't appear in a round will get DNC for each race in that round
    '''

    VALID_DNX = ('DNS', 'DNF', 'DNC', 'DSQ')
    DISCARD_TYPES = ('discardWorst', 'keepBest', None)
    SUMMARY_TYPE = ('allraces', 'roundresults')

    def __init__(self, name=None):
        if name:
            self.db = SeriesDB()
            self.data = self.db.getSeries(name)

    def addSeries(self, name,
                  seriesSummaryType,
                  roundsDiscardType,
                  roundsDiscardNum,
                  seriesDiscardType,
                  seriesDiscardNum,
                  seriesStartDate,
                  comment=None, 
                  overRideDNC=None):
        if roundsDiscardType not in self.DISCARD_TYPES \
            or seriesDiscardType not in self.DISCARD_TYPES:
                raise ValueError('Discard Type must be one of {}'
                                 .format(', '.join(self.DISCARD_TYPES)))

        self.data = {
            'seriesName': name,
            'seriesSummaryType': seriesSummaryType,
            'roundsDiscardType': roundsDiscardType,
            'roundsDiscardNum': roundsDiscardNum,
            'seriesDiscardType': seriesDiscardType,
            'seriesDiscardNum': seriesDiscardNum,
            'seriesStartDate': seriesStartDate,
            'overRideDNC': overRideDNC,
            'comment': comment,
            'rounds': [],
            'roundsIdx': {},
        }

    @property
    def seriesName(self):
        return self.data['seriesName']

    @property
    def seriesSummaryType(self):
        return self.data['seriesSummaryType']

    @property
    def roundsDiscardType(self):
        return self.data['roundsDiscardType']

    @property
    def roundsDiscardNum(self):
        return self.data['roundsDiscardNum']
        
    @property
    def seriesDiscardType(self):
        return self.data['seriesDiscardType']
        
    @property
    def seriesDiscardNum(self):
        return self.data['seriesDiscardNum']
        
    @property
    def overRideDNC(self):
        return self.data['overRideDNC']

    @property
    def comment(self):
        return self.data['comment']
        
    @property
    def rounds(self):
        return self.data['rounds']
        
    @property
    def roundsIdx(self):
        return self.data['roundsIdx']
        
    @property
    def seriesStartDate(self):
        return self.data['seriesStartDate']

    '''
    The next section of methods deals with the data at the series level
    '''

    def getSeriesResults(self):
        discards = self.seriesDiscardNum
        if len(self.rounds) == 1:
            discards = self.roundsDiscardNum
        summary = Regatta()
        summaryType = self.seriesSummaryType
        summary.addSeries(name='Summary',
                          seriesSummaryType=summaryType,
                          roundsDiscardType=self.seriesDiscardType,
                          roundsDiscardNum=discards,
                          seriesDiscardType=None,
                          seriesDiscardNum=0,
                          seriesStartDate=None,
                          overRideDNC=self.maxSeriesPlaces())
        allPeeps = self.getAllPeeps()
        raceResultsBase = {person: 'DNC' for person in allPeeps}  # Initially set everyone to DNC
        summary.addRound('Summary', '', '', 'Leaderboard',
                            [{'crew': x, 'boatNum': None} for x in allPeeps])
        if summaryType == 'allRaces':
            for round in self.rounds:
                roundName = round['name']
                for raceNum in range(self.numRaces(roundName)):
                    raceResult = raceResultsBase.copy()  # Default all races to DNC
                    for boat in self.getRoundResults(roundName)['boats']:
                        for person in boat['crew']:
                            raceRec = boat['races'][raceNum].copy()  # Get races that occurred
                            raceRec['discard'] = False
                            raceResult[(person,)] = raceRec
                    summary.addRace('Summary', raceResult, checkRace=False)
            return summary.getRoundResults('Summary')
        elif summaryType == 'roundResults':
            for i, round in enumerate(self.rounds):
                roundName = round['name']
                raceResult = raceResultsBase.copy()  # Default all races to DNC
                for boat in self.getRoundResults(roundName)['boats']:
                    raceRec = {
                        'place': boat['place'],
                        'discard': False,
                        'flag': False,
                        'raceNum': i,
                    }
                    for person in boat['crew']:
                        raceResult[(person,)] = raceRec
                summary.addRace('Summary', raceResult, checkRace=False)
            return summary.getRoundResults('Summary')
                
        else:
            raise NotImplementedError('The summaryType {} not implemented yet'.format(summaryType))

    def numBoats(self, roundName):
        return len(self._getRound(roundName)['boats'])

    def maxRoundPlaces(self, roundName):
        '''
        Returns the highest possible place for the round
        '''
        return self.numBoats(roundName) + 1

    def maxSeriesPlaces(self):
        '''
        Returns the highest possible place for the series.
        This is the maximum number of boats in any round.
        '''
        maxBoats = 0
        for round in self.rounds:
            if len(round['boats']) > maxBoats:
                maxBoats = len(round['boats'])
        return maxBoats + 1

    def listRounds(self):
        return [round['name'] for round in self.rounds]

    '''
    The next section of methods use submitted race results that are passed as
        (tuple of crew names): place string (int or DNx string)
    '''

    def addRace(self, roundName, results, checkRace=True):
        '''
        roundName is a string
        results are: 
        {
            (tuple of crew names): place string (int or DNx string),
            ...
        }
        checkRace can be disabled for splitting crew to disable numBoats check
        
        Returns nothing
        '''
        if len(results) != self.numBoats(roundName) and checkRace:
            raise ValueError('There are not enough boats in this race. Expected {} but got {}: {}'
                             .format(self.numBoats(roundName), len(results), list(results)))
        self.checkValidRace(roundName, results, allowDuplicates=not checkRace)
        raceNum = self.numRaces(roundName) + 1
        for crew, placeObj in results.items():
            if type(placeObj) == dict:
                raceRec = placeObj
            else:
                if not placeObj:
                    placeObj = 'DNS'
                raceRec = {
                    'place': placeObj if type(placeObj) == int else None,
                    'flag': placeObj.upper() if type(placeObj) != int else None,
                    'discard': False,
                    'raceNum': raceNum,  # Note that this will be one higher than the array index
                }
            boat = self._getBoat(roundName, crew)
            boat['races'].append(raceRec)

    def checkValidRace(self, roundName, results, allowDuplicates=False):
        '''
        Checks that the race places are unique and within bounds.
        Also checks that DNS or DNF places use a valid string
        Raises ValueError on the first error.
        Returns nothing
        '''
        # Check unique, except for DNX
        noDNXPlace = []
        for crew, place in results.items():
            if type(place) is dict:
                # Check race number bounds
                placeNum = place['place']
                if placeNum > self.numBoats(roundName) and not place['flag']:
                    raise ValueError(f'Race place {placeNum} for crew {crew} may not be greater '
                                     f'than the number of boats {self.numBoats(roundName)}')
                if placeNum <= 0:
                    raise ValueError(f'Race place {placeNum} for crew {crew} may not be less '
                                     f'than one')
                if placeNum in noDNXPlace and not allowDuplicates:
                    raise ValueError(f'Race place {placeNum} for crew {crew} must be unique')
                else:
                    noDNXPlace.append(placeNum)

            elif type(place) is int:
                # Check race number bounds
                if place > self.numBoats(roundName):
                    raise ValueError(f'Race place {place} for crew {crew} may not be greater than '
                                     f'the number of boats {self.numBoats(roundName)}')
                if place <= 0:
                    raise ValueError(f'Race place {place} for crew {crew} may not be less than one')
                if place in noDNXPlace and not allowDuplicates:
                    raise ValueError(f'Race place {place} for crew {crew} must be unique')
                else:
                    noDNXPlace.append(place)
            elif type(place) is str or place is None:
                # Check the DNX strings are valid:
                # None, DNS, S represent Did Not Start
                # DNF, F represent Did Not Finish
                if not place:
                    place = 'DNS'
                if str(place).upper() not in self.VALID_DNX:
                    raise ValueError(f'Race place {place} for crew {crew} in round {roundName} '
                                     f'must be a number or one of {roundName}')
            else:  # No floats or other weird stuff please
                raise ValueError(f'Race place {place} for crew {crew} in round {roundName} must be '
                                 f'a number, a valid dict or one of {self.VALID_DNX}')

        # Check numeric race result values do not have gaps and start from 1.
        # Above we check for duplicates, so only need to check the sum is the same a 1+2+3+...n
        intPlaces = [results[x] for x in results if type(results[x]) is int]
        if sum(intPlaces) != sum(range(1, len(intPlaces) + 1)) and not allowDuplicates:
            raise ValueError('Numeric race values must not have gaps and must start from 1: {}'
                             .format([results[x] for x in results]))

    def racePlacesToInt(self, races, base):
        '''
        Takes all the place fields in the record and treats them as a digit in a word of
        the passed base then converts that word to an int. 
        '''
        tot = 0
        for i, rec in enumerate(races, start=1):
            num = rec['place']
            if num > base:
                raise ValueError('Result {} for race {} must be less than or equal to the number '
                                 'of boats + 1 {}'.format(num, i + 1, base))
            if type(num) is not int:
                raise ValueError('Result {} for race {} must be an integer'.format(num, i + 1))
            tot += num * base ** (len(races) - i)
        return tot

    '''
    The methods in the next section only use the roundName
    '''

    def addRoundAll(self, round):
        boats = round['boats']
        roundName = round['name']
        self.addRound(roundName,
                      round['weather'], 
                      round['rounddate'], 
                      round['comment'], 
                      boats)

        for i in range(len(boats[0]['races'])):
            raceResults = {}
            for boat in boats:
                raceResults[tuple(boat['crew'])] = boat['races'][i]
            self.addRace(roundName, raceResults, checkRace=True)

    def addRound(self, roundName, weather, roundDate, comment, boats):
        round = {
            'name': roundName,
            'weather': weather,
            'rounddate': roundDate,
            'comment': comment,
            'boats': []
        }
        self.roundsIdx[roundName] = {
            'idx': len(self.rounds)  # We can use len() because we have not appended the round blob yet
        }
        for i, boat in [(i, o.copy()) for i, o in enumerate(boats)]:
            boat['races'] = []
            round['boats'].append(boat)
            crewStr = ','.join(boat['crew'])
            self.roundsIdx[roundName][crewStr] = {'idx': i}
        self.rounds.append(round)

    def numRaces(self, roundName):
        round = self._getRound(roundName)
        return len(round['boats'][0]['races'])  # The number of races for the first boat
        ### TODO ### Need to add some validation somewhere that all boats have the same amount of races

    def setDiscardRaces(self, roundName):
        '''
        This method sets the discard flag in the object for all the races
        in the round, so does not need to be passed or return any object.
        This should be calculated every time results are requested and not be saved into the DB
        in case of race edits. 
        '''
        num = self.roundsDiscardNum
        if not self.roundsDiscardType:
            return
        elif self.roundsDiscardType == 'discardWorst':
            for boat in self._getRound(roundName)['boats']:
                # Reverse sort by place and set the first "num" places to discard
                for rec in sorted(boat['races'], key=lambda x: x['place'], reverse=True)[:num]:
                    rec['discard'] = True
        elif self.roundsDiscardType == 'keepBest':
            for boat in self._getRound(roundName)['boats']:
                # Sort by place and set the last "num" places to discard
                for rec in sorted(boat['races'], key=lambda x: x['place'])[num:]:
                    rec['discard'] = True
        else:
            raise NotImplementedError('The discard type {} is not implemented yet'
                                      .format(self.roundsDiscardType))

    def setDNX(self, roundName):
        '''
        This method converts the DNx flag in the object for all the races
        in the round, so does not need to be passed or return any object.
        DNC is the max boats in the series + 1. All other DNX values are the number of boats in
        the round + 1
        This should be calculated every time results are requested and not be saved into the DB
        in case of race edits. 
        '''
        validDNX = self.VALID_DNX

        for boat in self._getRound(roundName)['boats']:
            for race in boat['races']:
                flag = race['flag']
                if type(race['place']) is int:
                    continue  # Assumes that any flag has already been converted to a value
                elif flag in validDNX:
                    if flag == 'DNC':
                        if self.overRideDNC:
                            race['place'] = self.overRideDNC
                        else:
                            race['place'] = self.maxSeriesPlaces()
                    else:
                        race['place'] = self.maxRoundPlaces(roundName)
                else:
                    raise ValueError(f'Invalid combination of place {race["place"]} and '
                                     f'flag {flag} in ' f'round "{roundName}" '
                                     f'race {race["raceNum"]} for '
                                     f'crew "{", ".join(boat["crew"])}".\n'
                                     f'Place must be None or integer. Flag must be one of '
                                     f'{", ".join(self.VALID_DNX)} or None')

    def maxCountBack(self, roundName):
        return self.maxSeriesPlaces() ** self.numRaces(roundName)

    def setScore(self, roundName):
        maxCB = self.maxCountBack(roundName)
        self.setDNX(roundName)
        self.setDiscardRaces(roundName)
        for boat in self._getRound(roundName)['boats']:
            loPoints, highPoints = self.calcPoints(roundName, boat['races'])
            # Create an overall score using a base of maxCB to ensure the different
            # values cannot interfere with each other.
            boat['score'] = highPoints * maxCB ** 2 + \
                            self.calcCBPlaces(roundName, boat['races']) * maxCB + \
                            self.calcCBLastBest(roundName, boat['races'])
            boat['points'] = loPoints
        self.sortPlaces(roundName)
        prevScore = 0
        prevPlace = 0
        for i, boat in enumerate(self._getRound(roundName)['boats'], start=1):
            if boat['score'] == prevScore:
                boat['place'] = prevPlace
            else:
                boat['place'] = i
            prevPlace = boat['place']
            prevScore = boat['score']

    def sortPlaces(self, roundName):
        # self.rounds[roundName].sort(key=lambda x: x['score'], reverse=True)
        boats = self._getRound(roundName)['boats']
        boats.sort(key=lambda x: x['score'], reverse=True)

    def getRoundResults(self, roundName):
        '''
        Calculate the overall score and place for each crew across each race in the round
        Return an array reverse sorted by score
        '''
        round = self._getRound(roundName)
        self.setScore(roundName)
        return round

    def _getRound(self, roundName):
            return self.rounds[self.roundsIdx[roundName]['idx']]

    def _getBoat(self, roundName, crew):
            boats = self._getRound(roundName)['boats']
            crewStr = ','.join(crew)
            return boats[self.roundsIdx[roundName][crewStr]['idx']]

    def getAllCrews(self, roundName='_all_'):
        crews = set()
        for round in self.rounds:
            if round['name'] != roundName and roundName != '_all_':
                continue
            for boat in round['boats']:
                crews.add(tuple(boat['crew']))
        return crews

    def getAllPeeps(self, roundName='_all_'):
        peeps = set()
        for crew in self.getAllCrews(roundName):
            for person in crew:
                peeps.add((person,))
        return peeps

    '''
    The below methods are based on a passed array of races. 
    The format is:
    [
        {
            'place': int,
            'flag': string,
            'discard': boolean,
            'raceNum': int
        },
        ...
    ]
    '''

    def getDiscardRaces(self, races):
        return [x for x in races if not x['discard']]

    def flipResults(self, races):
        '''
        Reverses the race numbers so that DNS is 0 and first is the number of boats + 1.
        '''
        flippedRaces = deepcopy(races)  # Don't mess up the original record!
        for rec in flippedRaces:
            # Note you *must* use maxSeriesPlace, NOT the max place for the round
            # to maintain the value of first place across rounds
            rec['place'] = self.maxSeriesPlaces() - rec['place']
        return flippedRaces

    def calcCBPlaces(self, roundName, races):
        '''
        Flip the results to first is the highest number, then sort the best places to 
        most significant digit then convert to an int with a base of the number of boats
        '''
        discardRaces = self.getDiscardRaces(races)
        discardRaces.sort(key=lambda x: x['place'])  # sort by place, ascending
        flippedRaces = self.flipResults(discardRaces)  # Now flipped, descending order
        tot = self.racePlacesToInt(flippedRaces, self.maxSeriesPlaces())
        return tot

    def calcCBLastBest(self, roundName, races):
        '''
        Flip the results to first is highest, then reverse the list so the most recent race
        is in the most significant position, then convert to an int with a base of the number
        of boats
        '''
        flippedRaces = self.flipResults(races)[::-1]  # Flip then reverse order
        tot = self.racePlacesToInt(flippedRaces, self.maxSeriesPlaces())
        return tot

    def calcPoints(self, roundName, races):
        '''
        Discard the worst races. Return:
            points: sum the discard adjusted results
            adjPoints: Flip the discard adjusted results to first is highest then sum 
        '''
        discardRaces = self.getDiscardRaces(races)
        flippedDiscardRaces = self.flipResults(discardRaces)
        loPoints = sum([x['place'] for x in discardRaces])
        hiPoints = sum([x['place'] for x in flippedDiscardRaces])
        return loPoints, hiPoints

