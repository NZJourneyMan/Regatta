#!/usr/bin/env python3

import os
import firebase_admin
from firebase_admin import firestore
import json
import argparse
from collections import OrderedDict

parser = argparse.ArgumentParser()
parser.add_argument('--prod', action='store_true', help='Load data into prod collections instead of dev')

args = parser.parse_args()
if args.prod:
    if 'SERIES_COLLECTION_NAME_PROD' not in os.environ:
        raise RuntimeError('Environment variable SERIES_COLLECTION_NAME_PROD is missing')
    os.environ['SERIES_COLLECTION_NAME'] = seriesCol = os.environ['SERIES_COLLECTION_NAME_PROD']
    if 'USERS_COLLECTION_NAME_PROD' not in os.environ:
        raise RuntimeError('Environment variable USERS_COLLECTION_NAME_PROD is missing')
    os.environ['USERS_COLLECTION_NAME'] = os.environ['USERS_COLLECTION_NAME_PROD']

# os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8888'
# os.environ['GOOGLE_CLOUD_PROJECT'] = 'onyx-virtue-370122'
if 'SERIES_COLLECTION_NAME' not in os.environ:
    raise RuntimeError('Environment variable SERIES_COLLECTION_NAME is missing')
seriesCol = os.environ['SERIES_COLLECTION_NAME']
if 'USERS_COLLECTION_NAME' not in os.environ:
    raise RuntimeError('Environment variable USERS_COLLECTION_NAME is missing')
usersCol = os.environ['USERS_COLLECTION_NAME']

# Application Default credentials are automatically created.
print('Creating App connection')
app = firebase_admin.initialize_app()
print('Creating client')
db = firestore.client()

with open('backup/all_data.json') as fd:
    allData = json.load(fd, object_pairs_hook=OrderedDict)

for seriesName in list(allData['allRaces']):
    doc_ref = db.collection(seriesCol).document(seriesName)
    print(f'Loading {seriesName}')
    doc_ref.set(allData['allRaces'][seriesName])

for user in list(allData['users']):
    doc_ref = db.collection(usersCol).document(user)
    print(f'Loading {user}')
    doc_ref.set({'name': user})

print()

dswc_ref = db.collection(seriesCol)
docs = dswc_ref.stream()
for doc in docs:
    print(f'Series {doc.id}')

print()

dswc_ref = db.collection(usersCol)
docs = dswc_ref.stream()
for doc in docs:
    print(f'Users {doc.id}')
