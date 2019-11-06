# main script to start the server
from flask import Flask, request, json
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

import numpy as np
import random
import tensorflow as tf
import keras
from keras.models import load_model

import nltk

# NER
# from nltk.tag.stanford import StanfordNERTagger
# jar = './stanford-ner.jar'
# model = './ner-model-indonesia.ser.gz'

# Prepare NER tagger with english model
# ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')

# import StemmerFactory class
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

app = Flask(__name__)
api = Api(app)

ENV = 'dev'

if ENV == 'dev' :
	app.debug = True
	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/chatbotagent'
else :
	app.debug = False
	app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'

db = SQLAlchemy(app)

@app.before_first_request
def create_tables():
    db.create_all()

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedToken.is_jti_blacklisted(jti)

import views, models, resources
from models import User, RevokedToken, Integration, Intent, Agent

api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.SecretResource, '/secret')

api.add_resource(resources.SaveIntegration, '/integration/save')

api.add_resource(resources.SaveIntents, '/intent/save')
api.add_resource(resources.ShowIntents, '/intent/show')

api.add_resource(resources.GenerateBotProp, '/bot/generateprops')
api.add_resource(resources.ShowAgent, '/bot/show')

api.add_resource(resources.Training, '/bot/training')

# load the model, and pass in the custom metric function
global graph
graph = tf.get_default_graph()
model = load_model('models/model_ChatBot.h5')

# create a data structure to hold user context
context = {}

def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=False):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)

    return(np.array(bag))

def classify(sentence, words, documents, classes):
    ERROR_THRESHOLD = 0.65
    
    # generate probabilities from the model
    p = bow(sentence, words)
    
    d = len(p)
    f = len(documents)-2
    a = np.zeros([f, d])
    tot = np.vstack((p,a))
    
    with graph.as_default():
        #results = model.predict([bow(sentence, words)])[0]
        results = model.predict(tot)[0]
        
        # filter out predictions below a threshold
        results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
        # sort by strength of probability
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append((classes[r[0]], r[1]))
        # return tuple of intent and probability
        return return_list

def response(sentence, intents, words, documents, classes, userID, show_details=False):
    results = classify(sentence, words, documents, classes)

    print('Result:',results)
    print('Sentence:', sentence)

    # if we have a classification then find the matching intent tag (intent)
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents['intents']:
                # find an intent matching the first result
                if i['intent'] == results[0][0]:
                    # set context for this intent if necessary
                    if 'context_set' in i:
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']

                    # check if this intent is contextual and applies to this user's conversation
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print ('intent:', i['intent'])
                        # a random response from the intent
                        return (random.choice(i['responses']))
            results.pop(0)
    else:
        print('No result')

@app.route('/webhook', methods=['POST'])
def webhook():
    message = request.form['message']
    id = request.form['id']

    intents = Intent.return_all()

    agent = Agent.find_by_user_id(id)

    classes = json.loads(agent.classes)
    documents = json.loads(agent.documents)
    words = json.loads(agent.words)

    responsai = response(message, intents, words, documents, classes, id)

    return {'response': responsai}

if __name__ == "__main__":
    app.run()

