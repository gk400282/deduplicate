import os

from flask import Flask, request, render_template, url_for
from pymongo import MongoClient

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import nltk
import string 
import sklearn
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import sent_tokenize, word_tokenize 
from nltk.stem import WordNetLemmatizer
from porter2stemmer import Porter2Stemmer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from autocorrect import spell

app = Flask(__name__)
client = MongoClient('localhost', 27017)    #Configure the connection to the database
db = client.sihdata    #Select the database
products = db.items #Select the collection
stemmer = Porter2Stemmer()
lemmatizer = WordNetLemmatizer()
word_tokenizer = word_tokenize
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

list_of_descriptions = []
list_of_pl = []
list_of_index = []
flag = []
items = list(products.find())
    
for item in items:
    list_of_descriptions.append(item['Description'])
    list_of_pl.append(item['PL Number'])
    list_of_index.append(item['_id'])

def get_wordnet_pos(word):
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)
def lemmatize(text):
    return ' '.join([lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in nltk.word_tokenize(text)])

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]    
    
def normalize(text):
    text = lemmatize(text)
    stop = set(stopwords.words('english'))
    tokens = word_tokenizer(text.lower().translate(remove_punctuation_map))
    tokens = stem_tokens([spell(token) for token in tokens])
    return ' '.join([token for token in tokens if token not in stop])

def cosine_similarity_matrix(list_of_descriptions):
    
    vectorizer = TfidfVectorizer(tokenizer=normalize)
    tfidf = vectorizer.fit_transform(list_of_descriptions)
    return sklearn.metrics.pairwise.cosine_similarity(tfidf, Y=None, dense_output=True)

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

cosine_similarity_dataframe = pd.DataFrame(cosine_similarity_matrix(list_of_descriptions))
cosine_similarity_dataframe.columns = list_of_index
cosine_similarity_dataframe.index = list_of_index
sim = cosine_similarity_dataframe

for i in range(len(sim)):
    flag1 = []
    temp = sim.sort_values(by = sim.index[i], axis = 1, ascending = False)
    gtt = []
    drop_list = []
    for j in range(len(sim)):      
        if sim.iloc[i][j] > 0.9 :
            gtt.append(sim.columns[j])
            # drop_list.append(j)        
#     sim = sim.drop(drop_list, axis = 0)
#     sim = sim.drop(drop_list, axis = 1)
    #greater_than_threshold(gtt,sim,i)
    
    flag1.append((gtt,sim.index[i]))                        
    flag.append(flag1)

similar_descriptions = list(flag[0][0][0])
pl_number = flag[0][0][1]
description_object_list = []
pl_number_object = products.find_one({'_id':pl_number})
for description in similar_descriptions:
    description_object_list.append(products.find_one({'_id':description}))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    return render_template('main.html', description_object_list=description_object_list, pl_number_object=pl_number_object)

@app.route('/start', methods=['POST'])
def start_post():
    selected_id = request.form['selected_description']
    return selected_id


