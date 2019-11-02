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