#!/usr/bin/env python3

import sys
import os
import re
import logging
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
# from printlights import Stranger, QueueFull


class Boom(Exception):
    pass


app = Flask(__name__)
# stranger = Stranger()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/index', methods=['GET'])
def redirect_index():
    return redirect(url_for('index'))


@app.route('/sending', methods=['POST'])
def sending():
    msg = request.form['message']
    sys.stderr.write('Recieved from the interwebs: "%s"\n' % msg)
    for w in 'fuck,cunt,wank,jiz'.split(','):
        if re.search(r'\b%s' % w, msg.lower()):
            return redirect(url_for('oops'))
    qlen = 0
    if msg:
        try:
            qlen = stranger.send(msg)
        except QueueFull:
            return redirect(url_for('queueFull'))
    return render_template('sending.html', msg=msg, qlen=qlen)


@app.route('/boom')
def boom():
    raise Boom()


@app.route('/you/have/been/very/bad')
def oops():
    return render_template('message.html',
                           msg='Oops! I\'ll tell your mother!',
                           but='Oops')


@app.route('/queue/full')
def queueFull():
    return render_template('message.html',
                           msg='Queue is full. Please wait a bit',
                           but='Ok')


@app.errorhandler(404)
def do404(e):
    return render_template('message.html',
                           msg='Sorry but the Demogorgon ate that page<br>(404)',
                           but='Ok')


@app.errorhandler(500)
def do500(e):
    return render_template('message.html',
                           msg='Oh no! The Demogorgon got me<br>(500)',
                           but='Ok')


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0')
