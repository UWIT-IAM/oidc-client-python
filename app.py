import os
import datetime
import logging
import flask
import logging
import json

from functools import wraps
from flask import Flask, jsonify, redirect, abort, render_template, url_for
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

issuer        = app.config['OIDC_ISSUER']
client        = app.config['OIDC_CLIENT']
secret        = app.config['OIDC_SECRET']
auth_params   = app.config['OIDC_SCOPES']
second_factor = {'id_token': {'acr': {'essential': True, 'value': 'https://refeds.org/profile/mfa'}}}

client_metadata = ClientMetadata(client_id=client, client_secret=secret)
config = ProviderConfiguration(issuer=issuer, client_metadata=client_metadata, auth_request_params=auth_params)
auth = OIDCAuthentication({'default': config}, app)

# Used for returning the authn response to the browser
def get_user_data():
    if flask.session:
        user = UserSession(flask.session)
        print(f'{user.id_token["sub"]} logged in')

        data = {
            'access_token': user.access_token,
            'id_token':     user.id_token,
            'userinfo':     user.userinfo
        }

        return json.dumps(data, indent=2)

def oidc_params(reauth, twofa):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # enables passing in extra params to the IdP during AuthN
            # If user has an SSO session already done without 2fa, and, you want 2fa, then both reauth and 2fa are required
            if reauth:
                auth_params['prompt'] = 'login'
            else:
                if 'prompt' in auth_params: del auth_params['prompt']

            if twofa:
                flask.session['check2fa'] = True
                auth_params['claims'] = second_factor
            else:
                if 'claims' in auth_params: del auth_params['claims']

            config = ProviderConfiguration(issuer=issuer, client_metadata=client_metadata, auth_request_params=auth_params)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def oidc_verify_2fa():
    # once user has authenticated, the acr value must match what we sent to the IdP
    if flask.session['check2fa']:
        user = UserSession(flask.session)
        if user.id_token['acr'] != second_factor['id_token']['acr']['value']:
            print(f'{user.id_token["sub"]} did not correctly do 2FA, token acr values do not match.')
            abort(401)
        else:
            flask.session.pop('check2fa', None)

@app.route('/')
def root():
    return render_template('main.html', tokens=get_user_data())

@app.route('/auth')
@oidc_params(False, False)
@auth.oidc_auth('default')
def basic():
    return render_template('main.html', tokens=get_user_data())

@app.route('/2fa')
@oidc_params(True, True)
@auth.oidc_auth('default')
def twofa():
    oidc_verify_2fa()
    return render_template('main.html', tokens=get_user_data())

@app.route('/reauth')
@oidc_params(True, False)
@auth.oidc_auth('default')
def reauth():
    return render_template('main.html', tokens=get_user_data())

@app.route('/logout')
@auth.oidc_logout
def logout():
    return render_template('main.html')

@app.route('/stepup')
@auth.oidc_logout
def stepup():
    # With the Flask-pyoidc I don't see a better way to do this, so logout is required first
    return redirect('/2fa')

@auth.error_view
def error(error=None, error_description=None):
    return jsonify({'error': error, 'message': error_description})

if __name__ == '__main__':
    auth.init_app(app)
    app.run()