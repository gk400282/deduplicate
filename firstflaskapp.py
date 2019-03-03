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

def initialize():
    global list_of_descriptions
    global list_of_pl
    global list_of_index
    global description_object_list
    global pl_number_object
    global similar_descriptions_ids
    global chosen_description_id
    list_of_descriptions = []
    list_of_pl=[]
    list_of_index=[]
    description_object_list=[]

def pl_duplication(id):
    global new_items
    pl_number = products.find_one({'_id':ObjectId(id)})['PL Number']
    counter = 0
    for item in new_items:
        if pl_number == item['PL Number']:
            counter = counter + 1
    if counter == 0:
        return 0
    else:
        return 1

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


    #checking if no old items left to work with
    if len(old_items) == 0:
        return("No data left to workon")

    for item in old_items:
        list_of_descriptions.append(item['Description'])
        list_of_pl.append(item['PL Number'])
        list_of_index.append(item['_id'])

    sim = dataframe(list_of_descriptions, list_of_index)
    flag= flag_maker(sim)
    similar_descriptions_ids = list(flag[0][0][0])
    pl_number = flag[0][0][1]
    pl_number_object = products.find_one({'_id':pl_number})


    #checking if there is just one unique description
    if len(similar_descriptions_ids) == 1:
        initialize()
        if pl_duplication(pl_number) == 0:
            products.update({'_id':ObjectId(pl_number)}, {'$set':{'type':'new' }})
        else:
            products.update({'_id':ObjectId(pl_number)}, {'$set':{'type':'pending' }})
        return redirect(url_for('start'))

    #creating a description object list to be used in the rendered html pages
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
    global old_items
    global new_items
    global deleted_items
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
    complete_descriptions_object_list = list(products.find())
    
    return render_template('history.html', complete_descriptions_object_list=complete_descriptions_object_list)

@app.route('/pending')
def pending():
    pending_pl_object_list = list(products.find({'type':'pending'}))
    return render_template('pending.html', pending_pl_object_list=pending_pl_object_list)

@app.route('/pending/<id>', methods=['POST'])
def pending_post(id):
    entered_pl = request.form['entered_pl']
    products.update({'_id':ObjectId(id)}, {'$set':{'PL Number':entered_pl, 'type':'new' }})
    return redirect(url_for('pending'))
