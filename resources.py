# API endpoints
from flask import request, jsonify, json
from flask_restful import Resource, reqparse
from models import User, RevokedToken, Integration
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

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
	def post(self):

		array = request.form.getlist('intents[]')

		print(request.form.getlist('intents[]'))

		return {
			'message': 'Intents Saving',
			'data': array,
			'string': json.dumps(array),
			'status': 200
		}, 200

