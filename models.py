# database models
from sqlalchemy import exc
from app import db
from passlib.hash import pbkdf2_sha256 as sha256

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(120), nullable = False)
    integrations = db.relationship('Integration', backref='user', lazy=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username = username).first()
    
    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username
            }
        return {'users': list(map(lambda x: to_json(x), User.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)
    
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))
    
    def add(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)

class Integration(db.Model):
	__tablename__ = 'integrations'

	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	messenger = db.Column(db.String(120), nullable = False)
	whatsapp = db.Column(db.String(120), nullable = False)
	line = db.Column(db.String(120), nullable = False)
	twitter = db.Column(db.String(120), nullable = False)
	telegram = db.Column(db.String(120), nullable = False)
	skype = db.Column(db.String(120), nullable = False)
	viber = db.Column(db.String(120), nullable = False)
	sms = db.Column(db.String(120), nullable = False)
	slack = db.Column(db.String(120), nullable = False)

	def __init__(self, user_id, messenger, whatsapp, line, twitter, telegram, skype, viber, sms, slack):
		self.user_id = user_id
		self.messenger = messenger
		self.whatsapp = whatsapp
		self.line = line
		self.twitter = twitter
		self.telegram = telegram
		self.skype = skype
		self.viber = viber
		self.sms = sms
		self.slack = slack

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	def update_data(self):
		data = self.query.filter_by(user_id = self.user_id).first()
		data.messenger = self.messenger
		data.whatsapp = self.whatsapp
		data.line = self.line
		data.twitter = self.twitter
		data.telegram = self.telegram
		data.skype = self.skype
		data.viber = self.viber
		data.sms = self.sms
		data.slack = self.slack

		db.session.commit()

	@classmethod
	def find_by_user_id(cls, id):
		return cls.query.filter_by(user_id = id).first()

	def serialize(self):
		return {
			'user_id': self.user_id, 
			'messenger': self.messenger,
			'whatsapp': self.whatsapp,
			'line': self.line,
			'twitter': self.twitter,
			'telegram': self.telegram,
			'skype': self.skype,
			'viber': self.viber,
			'sms': self.sms,
			'slack': self.slack
		}

class Intent(db.Model):
	__tablename__ = 'intents_bot'

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(), nullable = False)
	utterances = db.Column(db.String(), nullable = False)
	responses = db.Column(db.String(), nullable = False)
	entities = db.Column(db.String(), nullable = False)
	context_set = db.Column(db.String(), nullable = False)
	context_filter = db.Column(db.String(), nullable = False)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

class ClassifierProp(db.Model):
	__tablename__ = 'intents'

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(), nullable = False)
	words = db.Column(db.String(), nullable = False)
	classes = db.Column(db.String(), nullable = False)
	documents = db.Column(db.String(), nullable = False)
	ignore_words = db.Column(db.String(), nullable = False)
	bot_model_url = db.Column(db.String(), nullable = False)

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()


