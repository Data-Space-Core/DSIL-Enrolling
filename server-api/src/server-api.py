from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWKClient
import os
import requests
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

# Function to validate the token with Keycloak
def validate_token(token):
	url = f"{KEYCLOAK_SERVER}/realms/{REALM}/protocol/openid-connect/userinfo"
	headers = {"Authorization": f"Bearer {token}"}
	response = requests.get(url, headers=headers)

	if response.status_code == 200:
		user_info = response.json()
		roles = user_info.get("realm_access", {}).get("roles", [])
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

# Function to create Keycloak realm and user
def create_keycloak_realm_and_user(client_name, admin_user, admin_password):
	keycloak_admin = KeycloakAdmin(
		server_url=KEYCLOAK_SERVER,
		username=admin_user,
		password=admin_password,
		realm_name="master",
		client_id="admin-cli",
	)

	# Create the realm
	realm_payload = {"realm": client_name, "enabled": True}
	keycloak_admin.create_realm(realm_payload)
	# Add user
	user_payload = {
		"username": admin_user,
		"enabled": True,
		"credentials": [{"type": "password", "value": admin_password, "temporary": True}],
	}
	keycloak_admin.realm_name = client_name
	keycloak_admin.create_user(user_payload)
	return True

@app.route("/api/client", methods=["POST"])
def create_client():
	token = request.headers.get("Authorization").split(" ")[-1]
	is_valid, user_info = validate_token(token)

	if not is_valid:
		return jsonify({"error": "Invalid token or insufficient permissions"}), 403
	data = request.json
	client_name = data.get("name")
	keycloak_admin = data.get("keycloak", {}).get("admin")
	keycloak_password = data.get("keycloak", {}).get("password")
	if not client_name or not keycloak_admin or not keycloak_password:
		return jsonify({"error": "Missing required parameters"}), 400
	if not add_cname_record(client_name):
		return jsonify({"error": "Failed to add DNS record"}), 500

	if not create_keycloak_realm_and_user(client_name, keycloak_admin, keycloak_password):
		return jsonify({"error": "Failed to create Keycloak realm or user"}), 500
	return jsonify({"message": "Client created successfully"}), 201

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080, debug=True)

