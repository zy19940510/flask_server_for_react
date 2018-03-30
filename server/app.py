# coding: utf-8
# come from dw
import numpy
import pandas as pd
from pandas_datareader import data, wb
from flask import Flask, Response, request, make_response, jsonify, g
import datetime, time
import json
from flask_cors import *
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

def stringToDate(string):
    #example '2013-07-22 09:44:15+00:00'
    dt = datetime.datetime.strptime(string, "%Y-%m-%d")
    #print dt
    return dt


@app.route('/marks')
def marks():
    df_news = pd.read_csv('amazon_news.csv')
    try:
        df_news.drop('Unnamed: 0', inplace=True, axis=1)
    except ValueError:
        pass

    dates = df_news['date'].apply(lambda s: int(time.mktime(stringToDate(s).timetuple()))).tolist()
    ids = list(range(df_news.shape[0]))
    colors = ['red'] * df_news.shape[0]
    texts = df_news['title'].tolist()
    labels = ['N'] * df_news.shape[0]
    labelFontColor = ['white'] * df_news.shape[0]
    minSize = [7] * df_news.shape[0]

    response = make_response(jsonify(id=ids, time=dates, color=colors, text=texts,
                             label=labels, labelFontColor=labelFontColor, minSize=minSize))

    return response


@app.route('/history')
def get_history():
    symbol = 'AMZN'
    sym = request.args.get('symbol')
    if sym:
        symbol = sym
    f = '2015-1-1'
    t = '2018-1-1'
    uf = int(time.mktime(stringToDate(f).timetuple()))
    ut = int(time.mktime(stringToDate(t).timetuple()))
    af = request.args.get('from')
    at = request.args.get('to')
    if af and at:
        uf = af
        ut = at

    if os.path.exists('./data.csv'):
        df = pd.read_csv('data.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        if df.shape[0]:
            status = 'ok'
        print('from local:', df.shape)
    else:
        df = data.DataReader(symbol, 'quandl', f, t)

        df.to_csv('data.csv')
        if df.shape[0]:
            status = 'ok'
        print('from remote:', df.shape)
    print(df.index[0])
    print(df.head(1))

    date = list(map(lambda s: s.value // 10**9, df.index))
    date.reverse()

    open = df['Open'].tolist()
    open.reverse()

    high = df['High'].tolist()
    high.reverse()
    low = df['Low'].tolist()
    low.reverse()
    close = df['Close'].tolist()
    close.reverse()
    volume = df['Volume'].tolist()
    volume.reverse()

    response = make_response(jsonify(t=date, o=open,h=high, l=low, c=close, v=volume, s=status))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

@app.route('/config')
def config():
    with open('config.json', 'r') as f:
        jsdata = json.load(f)
        jsdata = json.dumps(jsdata)
        print(jsdata)

    return jsdata

@app.route('/symbols')
def symbols():
    with open('symbols.json', 'r') as f:
        jsdata = json.load(f)
        jsdata = json.dumps(jsdata)
        print(jsdata)

    return jsdata



if __name__ == '__main__':
    app.run(
        host='0.0.0.0'
    )

