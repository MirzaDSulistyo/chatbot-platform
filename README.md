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


ref flask :
https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
https://scotch.io/tutorials/build-a-restful-api-with-flask-the-tdd-way
https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
https://www.codementor.io/garethdwyer/building-a-crud-application-with-flask-and-sqlalchemy-dm3wv7yu2


ref flask keras :
https://stackoverflow.com/questions/49400440/using-keras-model-in-flask-app-with-threading
https://kobkrit.com/tensor-something-is-not-an-element-of-this-graph-error-in-keras-on-flask-web-server-4173a8fe15e1
https://towardsdatascience.com/deploying-keras-deep-learning-models-with-flask-5da4181436a2