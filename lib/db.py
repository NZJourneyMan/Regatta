import os
from utils import mkCrewList
import json

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
        self.cur.execute(sql, (seriesName, json.dumps(data)))

    def listUsers(self):
        sql = 'select name from people order by upper(name)'
        self.cur.execute(sql)
        return mkCrewList([x[0] for x in self.cur.fetchall()])

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

class Firestore():
    google_app = None

    def __init__(self):
        if 'SERIES_COLLECTION_NAME' not in os.environ:
            raise DBError('Environment variable SERIES_COLLECTION_NAME is missing')
        if 'USERS_COLLECTION_NAME' not in os.environ:
            raise DBError('Environment variable USERS_COLLECTION_NAME is missing')
        import firebase_admin
        from firebase_admin import firestore
        if self.google_app is None:
            Firestore.google_app = firebase_admin.initialize_app()
        self.db = firestore.client()
        self.seriesCol = self.db.collection(os.environ['SERIES_COLLECTION_NAME'])
        self.usersCol = self.db.collection(os.environ['USERS_COLLECTION_NAME'])

    def listSeries(self):
        query = self.seriesCol.order_by('seriesStartDate')
        docs = query.stream()
        return [doc.id for doc in docs]

    def getSeries(self, seriesName):
        return self.seriesCol.document(seriesName).get().to_dict()

    def saveSeries(self, seriesName, data):
        self.seriesCol.document(seriesName).set(data)

    def listUsers(self):
        docs = self.usersCol.stream()
        return [doc.id for doc in docs]

    def saveUser(self, user):
        self.usersCol.document(user).set({'name': user})
