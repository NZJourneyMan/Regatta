from copy import deepcopy


class Regatta(object):
    '''
    Data Structures:
    self.rounds = {
        'Round name': 
            [ array of dicts
                { 
                    'crew', (tuple of crew names),
                    'boatNum', 'boatname/number string',
                    'races': [array of race place records
                        {
                            'place': int,  # Should not be set in the DB if flag is used
                            'flag' : string,  # including DNS, DNF, DSQ & DNC
                            'discard': boolean,  # True if race was discarded. Not stored
                            'raceNum': int
                        }
                    ]
                }
            ]
    }
    Notes: 
        1. DNS, DNF & DSQ so are scored as the number of boats in the *round* + 1
        2. DNC is scored as the max number of boats in the *series* + 1
        3. Any person that doesn't appear in a round will get DNC for each race in that round
    '''

    VALID_DNX = ('DNS', 'DNF', 'DNC', 'DSQ')
    DISCARD_TYPES = ('fixed', 'keep', None)
    SUMMARY_TYPE = ('allraces', 'roundresults')

    def __init__(self,
                 roundDiscardsType, roundDiscardsNum,
                 seriesDiscardsType, seriesDiscardsNum,
                 overRideDNC=None):
        if roundDiscardsType not in self.DISCARD_TYPES \
            or seriesDiscardsType not in self.DISCARD_TYPES:
                raise ValueError('Discard Type must be one of {}'
                                 .format(', '.join(self.DISCARD_TYPES)))

        self.roundDiscardsType = roundDiscardsType
        self.roundDiscardsNum = roundDiscardsNum
        self.seriesDiscardsType = seriesDiscardsType
        self.seriesDiscardsNum = seriesDiscardsNum
        self.overRideDNC = overRideDNC
        self.rounds = {}
        self.roundIdx = {}

    '''
    The next section of methods deals with the data at the series level
    '''

    def getSeriesResults(self, summaryType='allRaces'):
        summary = Regatta(roundDiscardsType=self.seriesDiscardsType,
                          roundDiscardsNum=self.seriesDiscardsNum,
                          seriesDiscardsType=None,
                          seriesDiscardsNum=0,
                          overRideDNC=self.maxSeriesPlaces())
        if summaryType == 'allRaces':
            allPeeps = self.getAllPeeps()
            raceResultsBase = {person: 'DNC' for person in allPeeps}
            summary.addRound([{'crew': x, 'boatNum': None} for x in allPeeps], 'Summary')
            for roundName in self.rounds:
                for raceNum in range(self.numRaces(roundName)):
                    raceResult = raceResultsBase.copy()  # Default all races to DNC
                    for boat in self.getRoundResults(roundName):
                        for person in boat['crew']:
                            raceResult[(person,)] = boat['races'][raceNum]['place']  # Get races that occurred
                    summary.addRace('Summary', raceResult, checkRace=False)
            return summary.getRoundResults('Summary')
        else:
            raise NotImplementedError('The summaryType {} not implemented yet'.format(summaryType))

    def numBoats(self, roundName):
        return len(self.rounds[roundName])

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
        for _, res in self.rounds.items():
            if len(res) > maxBoats:
                maxBoats = len(res)
        return maxBoats + 1

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
        for crew, place in results.items():
            if not place:
                place = 'DNS'
            raceRec = {
                'place': place if type(place) == int else None,
                'flag': place.upper() if type(place) != int else None,
                'discard': False,
                'raceNum': raceNum,  # Note that this will be one higher than the array index
                }
            self.rounds[roundName][ self.roundIdx[crew] ]['races'].append(raceRec)

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
            if type(place) is int:
                # Check race number bounds
                if place > self.numBoats(roundName):
                    raise ValueError('Race place {} for crew {} may not be greater than the number '
                                     'of boats {}'.format(place, crew, self.numBoats(roundName)))
                if place <= 0:
                    raise ValueError('Race place {} for crew {} may not be less than one'
                                     .format(place, crew))
                if place in noDNXPlace and not allowDuplicates:
                    raise ValueError('Race place {} for crew {} must be unique'
                                     .format(place, crew))
                else:
                    noDNXPlace.append(place)
            elif type(place) is str or place is None:
                # Check the DNX strings are valid:
                # None, DNS, S represent Did Not Start
                # DNF, F represent Did Not Finish
                if not place:
                    place = 'DNS'
                if str(place).upper() not in self.VALID_DNX:
                    raise ValueError('Race place {} for crew {} in round {} must be a number or '
                                     'one of {}'
                                     .format(place, crew, roundName, self.VALID_DNX))
            else:  # No floats or other weird stuff please
                raise ValueError('Race place {} for crew {} in round {} must be a number or '
                                 'one of {}'
                                 .format(place, crew, roundName, self.VALID_DNX))

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

    def addRound(self, boats, roundName):
        self.rounds[roundName] = []
        self.roundIdx[roundName] = {}
        for i, boat in enumerate(boats):
            self.rounds[roundName].append({
                'crew': boat['crew'],
                'boatNum': boat['boatNum'],
                'races': [],
            })
            self.roundIdx[boat['crew']] = i

    def numRaces(self, roundName):
        roundResults = self.rounds[roundName]
        return len(roundResults[0]['races'])  # The number of races for the first crew

    def setDiscardRaces(self, roundName):
        '''
        This method sets the discard flag in the object for all the races
        in the round, so does not need to be passed or return any object.
        This should be calculated every time results are requested and not be saved into the DB
        in case of race edits. 
        '''
        if not self.roundDiscardsType:
            return
        elif self.roundDiscardsType in ('fixed', 'keep'):
            num = self.roundDiscardsNum
        else:
            raise NotImplementedError('The discard type {} is not implemented yet'
                                      .format(self.roundDiscardsType))
#         races = self.rounds
#         for rec in sorted(races, key=lambda x: x['place'])[:num - 1]:
#             rec['discard'] = True
#         return [x for x in races if not x['discard']]

        for boat in self.rounds[roundName]:
            # Reverse sort by place and set the first "num" places to discard
            for rec in sorted(boat['races'], key=lambda x: x['place'], reverse=True)[:num]:
                rec['discard'] = True

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

        for boat in self.rounds[roundName]:
            for race in boat['races']:
                if not race['flag']:
                    continue  # Assume that race['place'] has a valid value
                elif race['flag'] in validDNX:
                    if race['flag'] == 'DNC':
                        if self.overRideDNC:
                            race['place'] = self.overRideDNC
                        else:
                            race['place'] = self.maxSeriesPlaces()
                    else:
                        race['place'] = self.maxRoundPlaces(roundName)
                else:
                    raise ValueError('DNx value {} in round {} race {} for crew {} is invalid'
                                     .format(race['flag'],
                                             roundName,
                                             race['raceNum'],
                                             boat['crew']))

#         for crew, races in results.items():
#             retResults[crew] = []
#             for place in races:
#                 if type(place) is int:
#                     retResults[crew].append(place)
#                 else:
#                     if not place:
#                         place = 'DNS'
#                     place = place.upper()
#                     if place in validDNX:
#                         if place in ('DNC', 'C'):
#                             if self.overRideDNC:
#                                 retResults[crew].append(self.overRideDNC)
#                             else:
#                                 retResults[crew].append(self.maxSeriesPlaces())
#                         else:
#                             retResults[crew].append(self.maxRoundPlaces(roundName))
#
#         return retResults

    def maxCountBack(self, roundName):
        return self.maxSeriesPlaces() ** self.numRaces(roundName)

    def setScore(self, roundName):
        maxCB = self.maxCountBack(roundName)
        self.setDNX(roundName)
        self.setDiscardRaces(roundName)
        for boat in self.rounds[roundName]:
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
        for i, boat in enumerate(self.rounds[roundName], start=1):
            if boat['score'] == prevScore:
                boat['place'] = prevPlace
            else:
                boat['place'] = i
            prevPlace = boat['place']
            prevScore = boat['score']

    def sortPlaces(self, roundName):
        self.rounds[roundName].sort(key=lambda x: x['score'], reverse=True)

    def getRoundResults(self, roundName):
        '''
        Calculate the overall score and place for each crew across each race in the round
        Return an array reverse sorted by score
        '''
        overall_results = []

        self.setScore(roundName)
        return self.rounds[roundName]
#         for crew, races in self.setDNX(self.rounds[roundName], roundName).items():
#
#             overall_results.append({
#                 'crew': crew,
#                 'score': score,
#                 'points': points[0],
#                 'races': races,
#                 'races_orig': self.rounds[roundName][crew]
#             })
#         # Add in the position
#         overall_results.sort(key=lambda v: v['score'], reverse=True)
#         prevScore = 0
#         prevPlace = 0
#         for i, rec in enumerate(overall_results, start=1):
#             if rec['score'] == prevScore:
#                 rec['place'] = prevPlace
#             else:
#                 rec['place'] = i
#             prevPlace = rec['place']
#             prevScore = rec['score']
#
#         return overall_results

    def getAllCrews(self, roundName='_all_'):
        crews = set()
        for name, boats in self.rounds.items():
            if name != roundName and roundName != '_all_':
                continue
            for boat in boats:
                crews.add(boat['crew'])
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
#         tot = self.racePlacesToInt(self.flipResults(roundName, sorted(discardRaces, key=lambda x: x['place'])),
#                              self.maxSeriesPlaces())
        return tot

    def calcCBLastBest(self, roundName, races):
        '''
        Flip the results to first is highest, then reverse the list so the most recent race
        is in the most significant position, then convert to an int with a base of the number
        of boats
        '''
        flippedRaces = self.flipResults(races)[::-1]  # Flip then reverse order
        tot = self.racePlacesToInt(flippedRaces, self.maxSeriesPlaces())
#         tot = self.racePlacesToInt(self.flipResults(roundName, races)[::-1], self.maxSeriesPlaces())
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
#         adjTot = sum(self.flipResults(roundName, discardRaces))
#         tot = sum(discardRaces)
        return loPoints, hiPoints

