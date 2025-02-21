from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWKClient
import os
import subprocess
import yaml
import git
import requests
from kubernetes import client, config
from keycloak.keycloak_admin import KeycloakAdmin

app = Flask(__name__)

CORS(app)
print(os.getenv("KEYCLOAK_SERVER_URL"))
print(os.getenv("CLIENT_ID"))
print(os.getenv("CLIENT_SECRET"))

KEYCLOAK_SERVER = os.getenv("KEYCLOAK_SERVER_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REALM = os.getenv("REALM")
DNS_ZONE_FILE = os.getenv("DNS_ZONE_FILE")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Load the kubeconfig
config.load_kube_config("/root/.kube/config")
v1 = client.CoreV1Api()

# Function to validate the token with Keycloak
def validate_token(token):
	url = f"{KEYCLOAK_SERVER}/realms/{REALM}/protocol/openid-connect/userinfo"
	headers = {"Authorization": f"Bearer {token}"}
	response = requests.get(url, headers=headers)
	print(f"validate_token: {response} url: {url}")
	if response.status_code == 200:
		user_info = response.json()
		print(f"user_info: {user_info}")
		roles = user_info.get("realm_access", {}).get("roles", [])
		print(f"Roles: {roles}")
		if "admin" in roles:
			return True, user_info
	return False, None

# Function to add CNAME record
def add_cname_record(client_name):
	try:
		cname_entry = f"{client_name}    IN    CNAME    dsil.collab-cloud.eu.\n"
		with open(DNS_ZONE_FILE, "a") as f:
			f.write(cname_entry)
		return True
	except Exception as e:
		print(f"Error writing to DNS zone file: {e}")
		return False

def create_namespace(client_name):
	try:
		namespace = client.V1Namespace(metadata=client.V1ObjectMeta(name=client_name))
		v1.create_namespace(namespace)
		return True
	except Exception as e:
		print(f"Error creating Kubernetes namespace: {e}")
		return False
def get_admin_token_for_realm(client_name, admin_user, admin_password):
    url = f"{KEYCLOAK_SERVER}/realms/{client_name}/protocol/openid-connect/token"
    payload = {
        "client_id": "admin-cli",
        "username": admin_user,
        "password": admin_password,
        "grant_type": "password",
    }
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error getting token: {response.text}")
        return None

# Function to create Keycloak realm and user
def create_keycloak_realm(client_name, admin_user, admin_password, token):
	keycloak_url = f"{KEYCLOAK_SERVER}/admin/realms"
	# Create the realm payload
	realm_payload = {"realm": client_name, "enabled": True}

	# Send request to create realm with the access token
	response = requests.post(
    	keycloak_url,
    	json=realm_payload,
    	headers={"Authorization": f"Bearer {token}"}
	)
	if response.status_code != 201:
		print(f"Error creating realm: {response.text}")
		return False
	return True

# Function to create Keycloak realm and user
def create_keycloak_realmuser(client_name, admin_user, admin_password, token):
	keycloak_url = f"{KEYCLOAK_SERVER}/admin/realms"
	new_realm_token = get_admin_token_for_realm(client_name, admin_user, admin_password)
	if not new_realm_token:
		print("Error getting admin token for new realm")
		return False

	# Realm creation was successful, now create the user
	# Create user payload
	user_payload = {
		"username": admin_user,
		"enabled": True,
		"credentials": [{"type": "password", "value": admin_password, "temporary": True}],
	}

	# URL for creating user in the new realm
	user_url = f"{KEYCLOAK_SERVER}/admin/realms/{client_name}/users"
	# Send request to create user with the new realm's admin token
	response = requests.post(
		user_url,
		json=user_payload,
		headers={"Authorization": f"Bearer {new_realm_token}"}
	)
	if response.status_code != 201:
		print(f"Error creating user: {response.text}")
		return False
	return True

@app.route("/api/client", methods=["POST"])
def create_client():
	token = request.headers.get("Authorization").split(" ")[-1]
	is_valid, user_info = validate_token(token)
	print(token)
	print("---------------")
	print(user_info)
	if not is_valid:
		return jsonify({"error": "Invalid token or insufficient permissions"}), 403
	data = request.json
	print(f"Data: {data}")
	client_name = data.get("name")
	print(f"Client name: {client_name}")
	keycloak_admin = data.get("keycloak", {}).get("admin")
	keycloak_password = data.get("keycloak", {}).get("password")
	if not client_name or not keycloak_admin or not keycloak_password:
		return jsonify({"error": "Missing required parameters"}), 400
	if not add_cname_record(client_name):
		return jsonify({"error": "Failed to add DNS record"}), 500
	if not create_namespace(client_name):
		return jsonify({"error": "Failed to create namespace"}), 500
	if not create_keycloak_realm(client_name, keycloak_admin, keycloak_password, token):
		return jsonify({"error": "Failed to create Keycloak realm"}), 500
	if not create_keycloak_realmuser(client_name, keycloak_admin, keycloak_password, token):
		return jsonify({"error": "Failed to create Keycloak realmuser"}), 500
	return jsonify({"message": "Client created successfully"}), 201

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080, debug=True)

