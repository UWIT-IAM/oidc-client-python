import os
import datetime
import logging
import flask
import logging

from flask import Flask, jsonify
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc.user_session import UserSession

app = Flask(__name__)

# https://medium.com/@trstringer/logging-flask-and-gunicorn-the-manageable-way-2e6f0b8beb2f
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

app.logger.debug('Loading app.py')

app.config.from_pyfile('settings.py')
app.config.update({'PERMANENT_SESSION_LIFETIME': datetime.timedelta(days=7).total_seconds()})

issuer      = app.config['OIDC_ISSUER']
client      = app.config['OIDC_CLIENT']
secret      = app.config['OIDC_SECRET']
auth_params = app.config['OIDC_SCOPES']

client_metadata = ClientMetadata(client_id=client, client_secret=secret)
config = ProviderConfiguration(issuer=issuer, client_metadata=client_metadata, auth_request_params=auth_params)

auth = OIDCAuthentication({'default': config}, app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/login')
@auth.oidc_auth('default')
def login():
    print('we logged in')
    user_session = UserSession(flask.session)
    return jsonify(access_token=user_session.access_token,
                   id_token=user_session.id_token,
                   userinfo=user_session.userinfo)

@app.route('/logout')
@auth.oidc_logout
def logout():
    return "You've been successfully logged out!"

@auth.error_view
def error(error=None, error_description=None):
    return jsonify({'error': error, 'message': error_description})

if __name__ == '__main__':
    auth.init_app(app)
    app.run()