from flask import Flask   # Import the Flask class from the flask module
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS # Import CORS to allow Cross Origin Resource Sharing
from config import Config


# Create an instance of Flask called app which will be the central object
app = Flask(__name__)
# Set the configuration for the app
app.config.from_object(Config)
# Allow Cross Origin Resource Sharing
CORS(app)


#create an instance of SQLAlchemy called db which will be the central object for our database
db = SQLAlchemy(app)
# Create an instance of Migrate with the app and db
migrate = Migrate(app, db)

#import the routes and models to the app -- need this below the app or else will cause circular import because when it goes over to routes to look for app, app will not yet be defined
from . import routes, models