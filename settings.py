# http://flask.pocoo.org/docs/1.0/config/#configuring-from-files
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Secrets, in production must come from kubernetes mounted files, otherwise use dotenv
if 'KUBERNETES_SERVICE_HOST' in os.environ:
    OIDC_CLIENT = open("/etc/secrets/OIDC_CLIENT", "r").read()
    OIDC_SECRET = open("/etc/secrets/OIDC_SECRET", "r").read()
    SECRET_KEY  = open("/etc/secrets/SECRET_KEY", "r").read()
else:
    OIDC_CLIENT = os.getenv("OIDC_CLIENT")
    OIDC_SECRET = os.getenv("OIDC_SECRET")
    SECRET_KEY  = os.getenv("SECRET_KEY")

# Env Vars, in production are set by kubernetes, otherwise use dotenv
SERVER_NAME          = os.getenv("SERVER_NAME")
PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME")
OIDC_ISSUER          = os.getenv("OIDC_ISSUER")

# OIDC Scopes... set as space seperated
OIDC_SCOPES={'scope': os.getenv("OIDC_SCOPES").split()}

# Cookies
PERMANENT_SESSION_LIFETIME = int(os.getenv("COOKIE_LIFETIME"))