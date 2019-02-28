import os

from flask import Flask, request, render_template, url_for
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('localhost', 27017)    #Configure the connection to the database
db = client.sihdata    #Select the database
products = db.items #Select the collection

list_of_descriptions = []
list_of_pl = []

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    items = list(products.find())
    for item in items:
        list_of_descriptions.append(item['Description'])
        list_of_pl.append(item['PL Number'])

    print(list_of_descriptions)
    print(list_of_pl)
    return render_template('main.html', items=items)