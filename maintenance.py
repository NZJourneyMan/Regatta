#!/usr/bin/env python3

import sys
import os
import re
import logging
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def doMaint(e):
    return render_template('maint.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
