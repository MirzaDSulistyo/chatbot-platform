# API endpoints
from flask import request, jsonify, json
from flask_restful import Resource, reqparse
from models import User, RevokedToken, Integration, Intent, Agent
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

# import NLTK framework
import nltk

# import StemmerFactory class
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

import tensorflow as tf
sess = tf.Session()
from keras import backend as K

K.set_session(sess)
K.set_learning_phase(0)

import numpy as np
import random

from keras.applications import VGG19
from tensorflow import keras
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation
from keras import utils
from keras import layers
from keras.optimizers import adam

import matplotlib.pyplot as plt

from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import utils
from tensorflow.python.saved_model import tag_constants, signature_constants
from tensorflow.python.saved_model.signature_def_utils_impl import build_signature_def, predict_signature_def
from tensorflow.contrib.session_bundle import exporter

model_version = "2"

graph = tf.get_default_graph()

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)


class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        
        if User.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}
        
        new_user = User(
            username = data['username'],
            password = User.generate_hash(data['password'])
        )
        
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = User.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}
        
        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity = current_user.id)
            refresh_token = create_refresh_token(identity = current_user.id)
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    @jwt_required
    def get(self):
        return User.return_all()
    
    def delete(self):
        return User.delete_all()


class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42,
            'user': get_jwt_identity()
        }


class SaveIntegration(Resource):
	@jwt_required
	def post(self):

		new_data = Integration(
			user_id = get_jwt_identity(),
            messenger = request.form['messenger'],
            whatsapp = request.form['whatsapp'],
            line = request.form['line'],
            twitter = request.form['twitter'],
            telegram = request.form['telegram'],
            skype = request.form['skype'],
            viber = request.form['viber'],
            sms = request.form['sms'],
            slack = request.form['slack']
        )

		if Integration.find_by_user_id(get_jwt_identity()):
			try:
				new_data.update_data()
				return {
					'message': 'Integration successfully updated',
					'data': new_data.serialize(),
					'status': 200
				}, 200
			except:
				return {'message': 'Something went wrong on update data', 'status': 500}, 500

		try:
			new_data.save_to_db()
			return {
				'message': 'Integration successfully saved',
				'data': new_data.serialize(),
				'status': 200
			}, 200
		except:
			return {'message': 'Something went wrong on save data', 'status': 500}, 500


class SaveIntents(Resource):
    @jwt_required
    def post(self):

        dataUtterances = request.form.getlist('utterances[]')
        dataResponses = request.form.getlist('responses[]')
        dataEntities = request.form.getlist('entities[]')

        print(json.dumps(dataUtterances))
        print(dataResponses)
        print(dataEntities)

        new_data = Intent(
            user_id = get_jwt_identity(),
            name = request.form['name'],
            utterances = json.dumps(dataUtterances),
            responses = json.dumps(dataResponses),
            entities = json.dumps(dataEntities),
            context_set = request.form['context_set'],
            context_filter = request.form['context_filter']
        )

        existedData = Intent.find_by_name(request.form['name'])

        if not existedData:
            try:
                new_data.save_to_db()
                return {
                    'message': 'Intent successfully saved',
                    'data': new_data.serialize(),
                    'status': 200
                }, 200
            except:
                return {'message': 'Something went wrong on save data', 'status': 500}, 500
        return {'message': 'Date cannot be duplicate', 'status': 500}, 500

class ShowIntents(Resource):
    @jwt_required
    def get(self):
        return Intent.return_all()

class GenerateBotProp(Resource):
    @jwt_required
    def post(self):
        intents = Intent.return_all()

        words = []
        classes = []
        documents = []
        ignore_words = ['?']
        # loop through each sentence in our intents patterns
        for intent in intents['intents']:
            for pattern in intent['utterances']:
                # tokenize each word in the sentence
                w = nltk.word_tokenize(pattern)
                # add to our words list
                words.extend(w)
                # add to documents in our corpus
                documents.append((w, intent['intent']))
                # add to our classes list
                if intent['intent'] not in classes:
                    classes.append(intent['intent'])

        # stem and lower each word and remove duplicates
        words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
        words = sorted(list(set(words)))

        # remove duplicates
        classes = sorted(list(set(classes)))

        print (len(documents), "documents")
        print (len(classes), "classes", classes)
        print (len(words), "unique stemmed words", words)

        new_agent = Agent(
			user_id = get_jwt_identity(),
            name = request.form['name'],
            words = json.dumps(words),
            classes = json.dumps(classes),
            documents = json.dumps(documents),
            ignore_words = json.dumps(ignore_words),
            agent_model_url = request.form['agent_model_url']
        )

        if Agent.find_by_user_id(get_jwt_identity()):
            try:
                new_agent.update_data()
                return {
                    'message': 'Agent successfully updated',
                    'data': new_agent.serialize(),
                    'status': 200
                }, 200
            except:
                return {'message': 'Something went wrong on updating data', 'status': 500}, 500

        try:
            new_agent.save_to_db()
            return {
                'message': 'Agent successfully created',
                'data': new_agent.serialize(),
                'status': 200
            }, 200
        except:
            return {'message': 'Something went wrong on saving data', 'status': 500}, 500

class ShowAgent(Resource):
    @jwt_required
    def get(self):
        agent = Agent.find_by_user_id(get_jwt_identity())
        return {'agent': agent.serialize()}

class Training(Resource):
    @jwt_required
    def get(self):
        agent = Agent.find_by_user_id(get_jwt_identity())

        classes = json.loads(agent.classes)
        documents = json.loads(agent.documents)
        words = json.loads(agent.words)

        print (len(documents), "documents")
        print (len(classes), "classes", classes)
        print (len(words), "unique stemmed words", words)

        global graph
        with graph.as_default():
            # create our training data
            training = []
            output = []
            # create an empty array for our output
            output_empty = [0] * len(classes)

            # training set, bag of words for each sentence
            for doc in documents:
                # initialize our bag of words
                bag = []
                # list of tokenized words for the pattern
                pattern_words = doc[0]
                # stem each word
                pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
                # create our bag of words array
                for w in words:
                    bag.append(1) if w in pattern_words else bag.append(0)

                # output is a '0' for each tag and '1' for current tag
                output_row = list(output_empty)

                output_row[classes.index(doc[1])] = 1

                training.append([bag, output_row])
            
            # shuffle our features and turn into np.array
            random.shuffle(training)
            training = np.array(training)

            # create train and test lists
            train_x = list(training[:,0])
            train_y = list(training[:,1])

            model = Sequential()
            model.add(Dense(8, input_shape=[len(train_x[0],)]))
            model.add(Dense(8))
            model.add(Dense(8))
            model.add(Dense(len(train_y[0]), activation='softmax'))

            model.summary()
            model.compile(loss='categorical_crossentropy', optimizer=tf.train.AdamOptimizer(), metrics=['acc'])
            history = model.fit(np.array(train_x), np.array(train_y), epochs=1000, batch_size=8)

            model.save('models/model_ChatBot.h5')

            history_dict = history.history
            history_dict.keys()
            acc = history.history['acc']
            loss = history.history['loss']
            epochs = range(1, len(acc) + 1)

            return {'message': 'training agent done'}