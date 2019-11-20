#!/usr/bin/env python3

import sys
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS

from saillib import Regatta
from fixedtest import round1, round2, round3, round4, addRound

sRound = Regatta(roundDiscardsType='fixed', roundDiscardsNum=1,
                 seriesDiscardsType='fixed', seriesDiscardsNum=4)
addRound(sRound, 'Round1', round1)
addRound(sRound, 'Round2', round2)
addRound(sRound, 'Round3', round3)
addRound(sRound, 'Round4', round4)

app = Flask(__name__)
CORS(app)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'clip_sailboat.png', mimetype='image/vnd.microsoft.icon')


# Index handling
@app.route('/')
def index():
    return render_template('index.html')


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
    return jsonify(sRound.getRoundResults(roundName))


@app.route('/api/v1.0/getSeriesResult', methods=['GET'])
def getSeriesResult():
    seriesName = request.args.get('seriesName')
    return jsonify(sRound.getSeriesResults())


@app.route('/api/v1.0/listRounds', methods=['GET'])
def listRounds():
    seriesName = request.args.get('seriesName')
    return jsonify(sRound.listRounds())


if __name__ == '__main__':
    # app.debug = True
    app.run()
