import pandas as pd
import json
import numpy as np
from json2html import json2html

from flask import Flask, request, render_template

from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

""" initializations """
app = Flask(__name__)
CACHE = True # use eleasticsearch index to cache the tone analysis results
ES = Elasticsearch([{'host': 'localhost', 'port': 9200}])
DF = pd.read_csv('../data/7282_1.csv').replace([np.nan], [None])
DF = DF[DF.categories == 'Hotels'] # use hotels only category
DF.name = DF.name.str.casefold() # normalize hotel names lettercase
HOTEL_NAMES = DF.name.unique().tolist()

def ibm_tone(name):
    global CACHE, HOTEL_NAMES, ES, DF
    authenticator = IAMAuthenticator('{api_key}') # enter ibm tone api key here
    tone_analyzer = ToneAnalyzerV3(
        version='{version}', # enter ibm tone api version here
        authenticator=authenticator
    )
    tone_analyzer.set_service_url('{api_url}') # enter ibm tone api url here
    data = DF[DF.name == name]
    responses = []
    for review in data['reviews.text'].to_list():
        responses.append(tone_analyzer.tone(review, sentences=False))
    emotions = {}
    for response in responses:
        try:
            for emotion in response.result['document_tone']['tones']:
                tone_name = emotion['tone_name']
                if tone_name not in emotions:
                    emotions[tone_name] = []
                emotions[tone_name].append(emotion['score'])
        except Exception as e:
            print(e)
    for emotion in emotions:
        emotions[emotion] = np.mean(emotions[emotion])
    return emotions
    
    
def index_hotel(name):
    global CACHE, HOTEL_NAMES, ES, DF
    if not ES.indices.exists('hotels'):
        ES.indices.create('hotels')
    try:
        res = ES.get(index="hotels", id=name)
        res = res['_source'] 
    except NotFoundError as e:
        data = DF[DF.name == name]
        res = {}
        for key in ['address', 'city', 'country', 'latitude', 'longitude', 'postalCode', 'province']:
            res[key] = data[key].iloc[0]
        
        res['emotions'] = ibm_tone(name)
            
        res['reviews'] = []
        for _, row in data.iterrows():
            keys = ['date', 'dateAdded', 'doRecommend', 'id', 'rating', 'text', 'title', 'userCity', 'username', 'userProvince']
            review_data = {key: row['reviews.' + key] for key in keys}
            res['reviews'].append(review_data)
        res = json.dumps(res)
        ES.index(index="hotels", id=name, body=res)
        res = json.loads(res)
    return res

@app.route('/')
def index():
    return render_template("index.html")
    
# flask component #1: tone analysis
@app.route('/Overview/', methods=['POST'])
def Overview():
    global CACHE, HOTEL_NAMES, ES
    name = request.get_data().decode()
    name = name.lower()
    if name not in HOTEL_NAMES:
        return "Hotel '" + name + "' not found."
    if not CACHE:
        emotions = ibm_tone(name)
    else:
        emotions = index_hotel(name)['emotions']
    return pd.DataFrame.from_dict({'Emotions': list(emotions.keys()), 'Score': list(emotions.values())}).to_html()
    
    
# flask component #2: elasticsearch indexing
@app.route('/Detailed/', methods=['POST'])
def Detailed():
    global CACHE, HOTEL_NAMES, ES, DF
    name = request.get_data().decode()
    name = name.lower()
    if name not in HOTEL_NAMES:
        return "Hotel '" + name + "' not found."
    res = index_hotel(name)
    return json2html.convert(json = res)


    
if __name__ == '__main__':
    app.run()