import os

from flask import Flask, request, redirect, render_template, url_for
from pymongo import MongoClient
from sih import dataframe, flag_maker
from bson.objectid import ObjectId


app = Flask(__name__)
client = MongoClient('localhost', 27017)    #Configure the connection to the database
db = client.sihdata    #Select the database
products = db.newdata #Select the collection

list_of_descriptions = []
list_of_pl = []
list_of_index = []
old_items = []
new_items = []
deleted_items = []
similar_descriptions_ids = []
description_object_list = []
pl_number_object = {}
chosen_description_id = ''

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

for item in old_items:
     list_of_descriptions.append(item['Description'])
     list_of_pl.append(item['PL Number'])
     list_of_index.append(item['_id'])



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    global old_items
    global new_items
    global deleted_items
    global list_of_descriptions
    global list_of_pl
    global list_of_index
    global similar_descriptions_ids
    global description_object_list
    global pl_number_object
    old_items = list(products.find({'type':'old'}))
    new_items = list(products.find({'type':'new'}))
    deleted_items = list(products.find({'type':'deleted'}))
      
    for item in old_items:
        list_of_descriptions.append(item['Description'])
        list_of_pl.append(item['PL Number'])
        list_of_index.append(item['_id'])

    sim = dataframe(list_of_descriptions, list_of_index)
    print(sim)
    flag= flag_maker(sim)
    similar_descriptions_ids = list(flag[0][0][0])
    pl_number = flag[0][0][1]
    pl_number_object = products.find_one({'_id':pl_number})
    for description_id in similar_descriptions_ids:
        description_object_list.append(products.find_one({'_id':description_id}))

    return render_template('main.html', pl_number_object=pl_number_object, description_object_list=description_object_list)

@app.route('/start', methods=['POST'])
def start_post():
    global list_of_descriptions
    global list_of_pl
    global list_of_index
    global description_object_list
    global pl_number_object
    global similar_descriptions_ids
    global chosen_description_id
    this_plnumber_id = pl_number_object['PL Number']
    chosen_description_id = request.form['selected_description']
    list_of_descriptions = []
    list_of_pl=[]
    list_of_index=[]
    description_object_list=[]

    for one in similar_descriptions_ids:
        products.update({'_id':ObjectId(one)}, {'$set':{'type':'deleted'}})

    products.update({'_id':ObjectId(chosen_description_id)}, {'$set':{'type':'new' }})
    

    return redirect(url_for('start'))

@app.route('/history')
def history():
    deleted_descriptions_object_list = list(products.find({'type':'deleted'}))
    return render_template('history.html', deleted_descriptions_object_list=deleted_descriptions_object_list)
