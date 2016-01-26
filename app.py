#!/usr/bin/env python

from flask import Flask, jsonify, render_template

import psycopg2
import psycopg2.extras
import sys
from sqlalchemy import create_engine

engine = create_engine('postgres://smqdidhwgocwmg:qRi2N64egyMRyHAN9tiQ42Bd0y@ec2-54-225-195-249.compute-1.amazonaws.com:5432/dbjjk6gfc81mbh')
connection = engine.connect()


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/slides')
def about():
    return render_template('slides.html')

@app.route('/data', methods=['GET'])
def data_func():
    """conn = psycopg2.connect(
        user="smqdidhwgocwmg",
        password="qRi2N64egyMRyHAN9tiQ42Bd0y",
        host="ec2-54-225-195-249.compute-1.amazonaws.com:5432",
        database="dbjjk6gfc81mbh")"""
    if not connection:
        print "connection object not good"
    #cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cmd = "SELECT * FROM priced WHERE date in (SELECT * FROM (SELECT date FROM priced WHERE model in ('accord', 'civic', 'camry', 'corolla') ORDER BY date) as t) ORDER BY delta DESC;"

    #cur.execute(cmd)
    """with engine.connect() as conn:
        data = conn.execute(cmd)"""
    #data = cur.fetchall()
    data = connection.execute(cmd)
    connection.close()
    return jsonify(items=list(data))


if __name__ == '__main__':
    app.run()

