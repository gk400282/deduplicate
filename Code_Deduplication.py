import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import nltk
import string 
import operator
from collections import Counter
import sklearn
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import sent_tokenize, word_tokenize, TweetTokenizer 
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from porter2stemmer import Porter2Stemmer

stemmer = Porter2Stemmer()
lemmatizer = WordNetLemmatizer()
from nltk.corpus import wordnet

word_tokenizer = word_tokenize
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
from nltk.corpus import stopwords

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
    tokens = stem_tokens(word_tokenizer(text.lower().translate(remove_punctuation_map)))
    return ' '.join([token for token in tokens if token not in stop])

def cosine_similarity_matrix(list_of_descriptions):
    
    vectorizer = TfidfVectorizer(tokenizer=normalize)
    tfidf = vectorizer.fit_transform(list_of_descriptions)
    return sklearn.metrics.pairwise.cosine_similarity(tfidf, Y=None, dense_output=True)

def dataframe(list_of_descriptions,list_of_index):
    cosine_similarity_dataframe = pd.DataFrame(cosine_similarity_matrix(list_of_descriptions))
    cosine_similarity_dataframe.columns = list_of_index
    cosine_similarity_dataframe.index = list_of_index
    return cosine_similarity_dataframe

def flag_maker(sim):
    flag=[]
    for i in range(len(sim)):
        flag1 = []
        # temp = sim.sort_values(by = sim.index[i], axis = 1, ascending = False)
        gtt = []
        drop_list = []
        for j in range(len(sim)):      
            if sim.iloc[i][j] > 0.97:
                gtt.append(sim.columns[j])
                drop_list.append(j)        
    #     sim = sim.drop(drop_list, axis = 0)
    #     sim = sim.drop(drop_list, axis = 1)
        #greater_than_threshold(gtt,sim,i)
        
        flag1.append((gtt,sim.index[i]))
        flag.append(flag1)
    print(flag)
    return flag