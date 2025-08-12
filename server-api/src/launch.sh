#!/bin/bash
set -e  # exit on error

# --- Environment variables ---
export CLIENT_ID="server-api"
export CLIENT_SECRET="eb3yrKqw6xgzThGuH4aU7P0b4kwFvFSQ"
export KEYCLOAK_SERVER_URL="https://resonance.collab-cloud.eu/auth"
export REALM="master"
export DNS_ZONE_FILE="/opt/server-api/db.resonance"
export KUBECONFIG="/opt/server-api/config"
export PARENT_DOMAIN="resonance.collab-cloud.eu."
export DNS_SERVER1="http://130.188.160.1:6363"
export DNS_SERVER2="http://130.188.160.65:6363"

# Flask-specific
export PYTHONUNBUFFERED=1
export FLASK_APP="server-api.py"
export FLASK_ENV="production"

# --- Start application ---
exec flask run --host=0.0.0.0 --port=9090
#exec python3 server-api.py
