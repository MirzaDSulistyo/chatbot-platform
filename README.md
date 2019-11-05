$ mkdir flask-jwt
$ cd flask-jwt

$ virtualenv -p python3 venv

# following command will activate virtual environment on macOs/Linux
$ source venv/bin/activate

# on Windows run next 
# (see here https://virtualenv.pypa.io/en/stable/userguide/)
# \venv\Scripts\activate

(venv) pip install flask flask-restful flask-jwt-extended passlib flask-sqlalchemy

flask-jwt
├── views.py     # views of the server
├── models.py    # database models
├── resources.py # API endpoints
└── run.py       # main script to start the server

(venv) FLASK_APP=app.py FLASK_DEBUG=1 flask run

virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt

pip freeze > requirements.txt

# serve back-end at localhost:5000
FLASK_APP=run.py flask run

ref : https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb

Now we can start migrating database. First run,
python manage.py db init

This will create a folder named migrations in our project folder. To migrate using these created files, run
python manage.py db migrate

Now apply the migrations to the database using
python manage.py db upgrade

ref : https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc