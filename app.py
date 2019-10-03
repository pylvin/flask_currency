from datetime import datetime, timedelta
from flask import Flask, Response, render_template, request, redirect, jsonify
import psycopg2
import requests
import json
import os
import xmltodict
from pymemcache.client import base
from pymemcache.client.base import Client
from pymemcache import serde
# connection = psycopg2.connect(
#     host="0.0.0.0",
#     database="flask_db",
#     user="flask_user",
#     password="944377a4"
# )
if os.getenv("docker"):
    client = Client(('memcached', 11211),
                serializer=serde.python_memcache_serializer,
                deserializer=serde.python_memcache_deserializer)
else:
    client = Client(('localhost', 11211),
                    serializer=serde.python_memcache_serializer,
                    deserializer=serde.python_memcache_deserializer)
def currencies_data():
    for i in date_checker():
        if i['@Type'] == 'Xarici valyutalar':
            return i['Valute']
def date_checker():
    now = datetime.now()
    a = now.strftime('%d.%m.%Y')
    r = requests.get(f'https://www.cbar.az/currencies/{a}.xml')
    try:
        data = json.loads(json.dumps(xmltodict.parse(r.text)))
        return data['ValCurs']['ValType']

    except:
        yesterday = now - timedelta(days=1)
        yesterday = yesterday.strftime('%d.%m.%Y')
        r = requests.get(f'https://www.cbar.az/currencies/{yesterday}.xml')
        data = json.loads(json.dumps(xmltodict.parse(r.text)))
        return data['ValCurs']['ValType']

def search_by_code(data,code):
    for i in data:
        if i['@Code'] == code:
            return i

app = Flask('app')

@app.route("/currency/<string:code>/")
def define_currency(code):
    if client.get(code):
        # print(f'{code} FROM MEMCACHE')
        return jsonify(client.get(code),{'MEMCACHE':True})
    else:
        client.set(code, search_by_code(currencies_data(),code.upper()), expire=20)
        # print(f'{code} FROM API')
        return jsonify(search_by_code(currencies_data(),code.upper()),{'API':True})

@app.route("/currency/")
def all_currency():
    if client.get('all'):
        # print('FROM MEMCACHE')
        return jsonify(client.get('all'),{'MEMCACHE'})
    else:
        client.set('all',currencies_data(),expire=20)
        # print('FROM API')
        return jsonify(currencies_data(),{'API':True})

@app.route("/")
def index():
    return redirect('http://127.0.0.1:5000/currency/')
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)




