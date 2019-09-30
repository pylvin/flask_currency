from datetime import datetime, timedelta

import xmltodict as xmltodict
from flask import Flask, Response, render_template, request, redirect, jsonify
import psycopg2
import requests
import json
import xmltodict

connection = psycopg2.connect(
    host="0.0.0.0",
    database="flask_db",
    user="flask_user",
    password="944377a4"
)
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
        for j in i['Valute']:
            if j['@Code'] == code:
                return j

app = Flask('app')

@app.route("/api/<string:code>")
def create_table(code):
    if code == 'currency':
        return jsonify(date_checker())
    else:
        return jsonify(search_by_code(date_checker(),code.upper()))
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


