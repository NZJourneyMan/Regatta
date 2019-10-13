#!/usr/bin/python3

import os, sys, json
from pprint import pprint


class Regatta(object):

    VALDNS = (None, 'NONE', 'DNS', 'S')
    VALDNF = ('DNF', 'F')

    def __init__(self, discardsPercentage=None, numDiscards=None):
        if discardsPercentage:
            if numDiscards:
                raise ValueError('Cannot set both discardsPercentage and numDiscards')
            if discardsPercentage < 0 or discardsPercentage >= 100:
                raise ValueError('discardsPercentage must be between zero and one hundred')
        elif not numDiscards:
            raise ValueError('Must set one of discardsPercentage or numDiscards')

        self.discardsPercentage = float(discardsPercentage) / 100 if discardsPercentage else None
        self.numDiscards = numDiscards
        self.results = {}

    def addBoatCrews(self, boatCrews):
        for crew in boatCrews:
            self.results[crew] = []
        self.numBoats = len(self.results)
        self.maxPlaces = self.numBoats + 2

    def addRace(self, results):
        if len(results) != self.numBoats:
            raise ValueError('There are not enough boats in this race. Expected {} but got {}: {}'
                             .format(self.numBoats, len(results), list(results)))
        self.checkValidRace(results)
        for crew, place in self.calcDNX(results).items():
            self.results[crew].append(place)
        self.updateStats()

    def updateStats(self):
        self.numRaces = len(self.results[list(self.results)[0]])
        self.maxCountBack = self.maxPlaces ** self.numRaces
        if self.discardsPercentage:
            self.numDiscards = int(self.discardsPercentage * self.numRaces)

    def getResults(self):
        '''
        Calculate the overall score for each crew across the races.
        Return an array reverse sorted by score
        '''
        maxCB = self.maxCountBack
        overall_results = []

        for crew, races in self.results.items():
            points = self.calcPoints(races)
            # Create an overall score using a base of maxCB to ensure the different
            # values cannot interfere with each other.
            score = points[1] * maxCB ** 2 + \
                    self.calcCBPlaces(races) * maxCB + \
                    self.calcCBLastBest(races)

            overall_results.append({
                'crew': crew,
                'score': score,
                'points': points[0],
                'races': races,
            })
        return sorted(overall_results, key=lambda v: v['score'], reverse=True)

    def wordToInt(self, word, base):
        tot = 0
        for i, num in enumerate(word, start=1):
            if num >= base:
                raise ValueError('Number {} at index {} must be less than the base {}'.format(num, i, base))
            tot += num * base ** (len(word) - i)
        return tot

    def flipResults(self, races):
        '''
        Reverses the race numbers so that DNS is 0 and first is the number of boats + 1
        '''
        rev = [self.maxPlaces - x for x in races]
        return rev

    def calcCBPlaces(self, races):
        '''
        Flip the results to first is the highest number, then sort the best places to 
        most significant digit then convert to an int with a base of the number of boats
        '''
        tot = self.wordToInt(self.flipResults(sorted(races)), self.maxPlaces)
        return tot

    def calcCBLastBest(self, races):
        '''
        Flip the results to first is highest, then reverse the list so the most recent race
        is in the most significant position, then convert to an int with a base of the number
        of boats
        '''
        tot = self.wordToInt(self.flipResults(races)[::-1], self.maxPlaces)
        return tot

    def calcPoints(self, races):
        '''
        Discard the worst races. Return:
            points: sum the discard adjusted results
            adjPoints: Flip the discard adjusted results to first is highest then sum 
        '''
        discardRaces = sorted(races)[:self.numRaces - self.numDiscards]
        adjTot = sum(self.flipResults(discardRaces))
        tot = sum(discardRaces)
        return tot, adjTot

    def checkValidRace(self, results):
        '''
        Checks that the race places are unique and within bounds.
        Also checks that DNS or DNF places use a valid string
        Raises ValueError on the first error.
        Returns nothing
        '''

        # Check unique, except for DNF and DNS
        noDNXPlace = []
        for crew, place in results.items():
            if type(place) is int:
                # Check race number bounds
                if place > self.numBoats:
                    raise ValueError('Race place {} for crew {} may not be greater than the number '
                                     'of boats {}'.format(place, crew, self.numBoats))
                if place <= 0:
                    raise ValueError('Race place {} for crew {} may not be less than one'
                                     .format(place, crew))
                if place in noDNXPlace:
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
                if str(place).upper() not in self.VALDNS + self.VALDNF:
                    raise ValueError('Race place {} for crew {} must be a number or one of '
                                     'blank, DNS, S, DNF or F'.format(place, crew))
            else:  # No floats or other weird stuff please
                raise ValueError('Race place {} for crew {} must be a number or one of '
                                 'blank, DNS, S, DNF or F'.format(place, crew))

        # Check numeric race result values do not have gaps and start from 1.
        # Above we check for duplicates, so only need to check the sum is the same a 1+2+3+...n
        intPlaces = [results[x] for x in results if type(results[x]) is int]
        if sum(intPlaces) != sum(range(1, len(intPlaces) + 1)):
            raise ValueError('Numeric race values must not have gaps and must start from 1: {}'
                             .format([results[x] for x in results]))

    def calcDNX(self, results):
        '''
        Converts DNS or DNS race place to an integer.
        Assumes the DNS or DNF strings are valid
        Returns an array of integer race places
        '''
        dnf = self.maxPlaces - 1
        dns = self.maxPlaces

        retResults = {}
        for crew, place in results.items():
            if type(results[crew]) is int:
                retResults[crew] = place
            else:
                if not place:
                    place = 'DNS'
                place = place.upper()
                if place in self.VALDNS:
                    retResults[crew] = dns
                else:
                    retResults[crew] = dnf

        return retResults


def main():
#         race_results = {
#         'Boat 0': [10,10,10,10,10,10,10,10],
#         'Boat 1': [4,5,5,5,5,5,5,5],
#         'Boat 2': [5,5,5,5,5,5,5,4],
#         'Boat 3': [1,2,1,1,1,1,1,1],
#         'Boat 4': [5,1,1,1,1,1,1,1],
#         'Boat 5': [1,2,2,1,1,1,1,1],
#         'Boat 6': [3,1,1,1,1,1,1,1],
#         'Boat 7': [1,1,1,1,4,5,5,5],
#         'Boat 8': [5,5,5,5,1,1,1,1],
#     }
#     race_results = {
#         'Boat 1': [1,2,3,4],
#         'Boat 2': [4,3,2,1],
#         'Boat 3': [3,1,4,2],
#         'Boat 4': [2,4,1,3],
#     }
    race_results = {
        'Boat 1': [1, 2],
        'Boat 2': ['dns', '']
    }
#     race_results = {
#         ('Kentaro', 'Clare'): [3, 2, 1, 1],
#         ('Ken', 'Mark'): [1, 1, 4, 3],
#
#         ('Emilio', 'Furold'): [6, 7, 7, 6],
#         ('Evan', 'Sean'): [7, 4, 3, 2],
#         ('Matt', 'Amanda G'): [5, 5, 2, 4],
#         ('Amanda C', 'Chris'): [2, 3, 5, 7],
#         ('Saj', 'Maria'): [8, 8, 6, 5],
#         ('Andrew',): [4, 6, 'DNS', ''],
#     }

    # sRound = Regatta(discardsPercentage=50)
    sRound = Regatta(numDiscards=1)

    crews = list(race_results)
    sRound.addBoatCrews(crews)

    for i in range(len(race_results[crews[0]])):
        results = {c: race_results[c][i] for c in crews if len(race_results[c]) > i}
        try:
            sRound.addRace(results)
        except ValueError as e:
            pprint(results)
            print('Error: {}'.format(e))
            sys.exit(1)
    # sRound.addRace({1:1, 2:2})  # Check for too few boats

    overall_results = sRound.getResults()

    prev = None
    for result in overall_results:
        print(str(result['crew']) + ':', \
              result['points'], \
              race_results[result['crew']], \
              'ERROR: Score cannot be the same' if result['score'] == prev else '')
        prev = result['score']


if __name__ == '__main__':
    sys.exit(main())
