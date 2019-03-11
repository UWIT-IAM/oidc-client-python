# Python OIDC with UW IdP

Running this locally and hitting the endpoint `/login` will redirect you to the IdP.  However, by design, your client ID and host url that you run this on must be registered at our IdP and match what gets posted to the IdP endpoints.

## Setup - Running Locally

1. Copy `.env-tmp` to `.env` and add real values
2. Run `FLASK_ENV=development FLASK_APP=app.py flask run`

## Setup - Running in Docker

1. Copy `.env-tmp` to `.env` and add real values
1. `docker build -t oidc-python:latest .`
1. `docker run --env-file .env -p 8000:8000 oidc-python`

## Setup - Running in Minikube

1. Install and start minikube, make sure your context is minikube `kubectl config current-context`
1. Tell minikube to use your local docker `eval $(minikube docker-env)`
1. Build the image `docker build -t oidc-python:latest .`
1. Create a kubernetes secret.

       echo "actual client id" > OIDC_CLIENT
       echo "actual client secret" > OIDC_SECRET
       echo "actual flask session key" > SECRET_KEY
       kubectl create secret generic oidc-python --from-file=./OIDC_SECRET --from-file=./OIDC_CLIENT --from-file=./SECRET_KEY

1. Create a service.yml and deployment.yml using `/examples/kubernetes`
1. Apply the yml `kubectl apply -f ./examples/kubernetes/`
1. Make a request to `/`, you should not get a 404 `curl $(minikube service oidc-python --url)`

## Setup - Running in Kubernetes

1. [Configure docker](https://cloud.google.com/container-registry/docs/pushing-and-pulling) to use gcloud `gcloud auth configure-docker`
1. Tag and push

       docker build -t gcr.io/uwit-mci-iam/oidc-python:1.0.0 .
       docker push gcr.io/uwit-mci-iam/oidc-python:1.0.0

1. Use deployment and service located at https://github.com/UWIT-IAM/gcp-k8/tree/master/dev/oidc-python