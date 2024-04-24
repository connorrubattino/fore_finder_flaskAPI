from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from . import db
from .models import Golfer
from datetime import datetime, timezone

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify(username, password):
    golfer = db.session.execute(db.select(Golfer).where(Golfer.username==username)).scalar_one_or_none()
    if golfer is not None and golfer.check_password(password):
        return golfer
    return None

@basic_auth.error_handler
def handle_error(status_code):
    return {'error': 'Incorrect username and/or password. Please try again'}, status_code

@token_auth.verify_token
def verify(token):
    golfer = db.session.execute(db.select(Golfer).where(Golfer.token==token)).scalar_one_or_none()
    if golfer is not None and golfer.tokenExp > datetime.now(timezone.utc):
        return golfer
    return None

@token_auth.error_handler
def handle_error(status_code):
    return {'error': 'Incorrect token. Please try again'}, status_code