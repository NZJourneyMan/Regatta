#!/usr/bin/env python3
'''
DSWC sailing scoring app, focusing on the sailors, rather than the boats. This allows
for teams to have different members, and for the results to focus on the members.

'''
# pylint: disable=C0114,C0115,C0116


import sys
import os
import time
import json
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS

LIBDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
BINDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'bin'))
sys.path += [LIBDIR, BINDIR]
from saillib import Regatta, SeriesDB, RegattaException, PG_DB

if 'ADMIN_PW' in os.environ:
    ADMIN_PW = os.environ['ADMIN_PW']
else:
    print('Environment variable "ADMIN_PW" missing. Quitting', file=sys.stderr)
    sys.exit(1)

START_TIME = os.environ['START_TIME'] if 'START_TIME' in os.environ else time.time()

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='%%',
        variable_end_string='%%',
        comment_start_string='<#',
        comment_end_string='#>',
    ))

def getSeries(name):
    return Regatta(name)

app = CustomFlask(__name__)
CORS(app)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'clip_sailboat.png', mimetype='image/vnd.microsoft.icon')


# Index handling
@app.route('/')
def index():
    return render_template('index.html', startTime=START_TIME)

@app.route('/add_round')
def add_round():
    return render_template('add_round.html', startTime=START_TIME)

@app.route('/add_series')
def add_series():
    return render_template('add_series.html', startTime=START_TIME)

@app.route('/index', methods=['GET'])
def redirect_index():
    return redirect(url_for('index'))


# Boiler plate pages for 500, 404 and testing 500
@app.route('/boom', methods=['GET'])
def boom():

    class Boom(Exception):
        pass

    raise Boom("We're sinking!")


@app.errorhandler(404)
def do404(e):
    return render_template('message.html',
                           msg='Sorry, but that page was blown away in a storm<br>(404)',
                           but='Ok'), 404


@app.errorhandler(500)
def do500(e):
    return render_template('message.html',
                           msg='Mayday! Mayday! Mayday!<br>This site has sunk<br>(500)',
                           but='Ok'), 500


# API definitions
@app.route('/api/v1.0/getRoundResult', methods=['GET'])
def getRoundResult():
    seriesName = request.args.get('seriesName')
    roundName = request.args.get('roundName')
    return jsonify(getSeries(seriesName).getRoundResults(roundName))


@app.route('/api/v1.0/getSeriesResult', methods=['GET'])
def getSeriesResult():
    seriesName = request.args.get('seriesName')
    return jsonify(getSeries(seriesName).getSeriesResults())


@app.route('/api/v1.0/listRounds', methods=['GET'])
def listRounds():
    seriesName = request.args.get('seriesName')
    return jsonify(getSeries(seriesName).listRounds())

@app.route('/api/v1.0/listSeries', methods=['GET'])
def listSeries():
    return jsonify(SeriesDB().listSeries())

@app.route('/api/v1.0/listUsers', methods=['GET'])
def listUsers():
    return jsonify(SeriesDB().listUsers())

@app.route('/api/v1.0/addRound', methods=['POST'])
def addRound():
    seriesName = request.args.get('seriesName')
    data = request.get_json()
    if data['admin_pw'] != ADMIN_PW:
        return jsonify({'status': False, 'message': 'Incorrect password'}), 401
    msg = []
    try:
        db = PG_DB()
        series = getSeries(seriesName)
        toDel = []
        for i, round in enumerate(series.data['rounds']):
            if round['name'] == data['name']:
                toDel.append(i)
        for i in toDel:
            msg.append(f'Deleting existing {series.data["rounds"][i]["name"]}')
            del(series.data['rounds'][i])
            
        series.addRoundAll(data)
        db.saveSeries(seriesName, json.dumps(series.data))
        currentCrewList = SeriesDB().listUsers()
        # Save any new users
        for boat in data['boats']:
            for name in boat['crew']:
                if name not in currentCrewList and name not in (None, ''):
                    db.saveUser(name)
    # except RegattaException as e:
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 400
    else:
        return jsonify({'status': True, 'message': '\n'.join(msg)})

@app.route('/api/v1.0/addSeries', methods=['POST'])
def addSeries():
    data = request.get_json()
    if data['admin_pw'] != ADMIN_PW:
        return jsonify({'status': False, 'message': 'Incorrect password'}), 401
    series = Regatta()
    msg = []
    try:
        series.addSeries(
            data["seriesName"],
            data["seriesSummType"],
            data["roundDiscardType"],
            int(data["roundDiscardNum"]),
            data["seriesDiscardType"],
            int(data["seriesDiscardNum"]),
            data["seriesStartDate"],
            data["comment"],
        )
        db = PG_DB()
        db.saveSeries(data["seriesName"], json.dumps(series.data))
    # except RegattaException as e:
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 400
    else:
        return jsonify({'status': True, 'message': '\n'.join(msg)})

if __name__ == '__main__':
    # app.debug = True
    app.run()
