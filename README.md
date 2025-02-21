# DSIL-Enrolling

Backend component to add subdomain to named zone file and add Keycloak realm and user for the client as well as kubernetes namespace

Backend exposes single POST REST endpoint 
````
/api/client"
````
endpoint takes JSON structure of the client data as paramter and have to be provided with valid bearer token in "Authorization" header
Data structure of the client data is as follows:
````
{
    "name": "<client_name>",
    "keycloak": {
        "admin": "<admin_user>",
        "password": "<admin_password>"
    }
}
````

<client_name> is used as subdomain name as well as Keycloak realm name and Kubernetes namespace name

API end point can be called like this (Javascript example):
````
async function createClient(token, data) {
    try {
        console.log("createClient:");
        const response = await fetch(`${BACKEND_URL}/api/client`, {
            method: "POST",
            headers: {
                'Authorization': `Bearer ${token}`,
                'Access-Control-Allow-Origin': '*', 
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Content-Length': data.length
            },
            body: data
        });
        const resp = await response.json();
        console.log(resp);
    } 
    catch (error) {
        console.error("Failed to fetch schedule data:", error);
    }
}
````
token must be obtained from Keycloak in the frontend app

## Testing
To test the API you can use curl but you must get valid token for authentication. You can do that for example like this:
```
curl -X POST "https://cloud.ouludatalab.fi/realms/master/protocol/openid-connect/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=server_api" \
     -d "client_secret=your_client_secret"
     -d "grant_type=password" \
     -d "username=your_username" \
     -d "password=your_password" \
     -d "scope=openid profile email roles"
```
Then you can use Curl to call the API:
````
curl -X GET "http://cloud.ouludatalab.fi:5000/api/client" -H "Authorization: Bearer eyJhbGciO..." -d "{\"name\": \"apitest\", \"keycloak\": { \"admin\": \"admin2\", \"password\": \"password2\"}}"
````

## Keycloak configuration
You need to create client in Keycloak and in client scopes take "dedicated scopes" and add a Mapper to realm roles in order to have roles list included  in the access token

## Kubernetes conbfiguration
In order to create a client namespace in kubernetes cluster you need to provide cluster config file. 
````
microk8s config > ./kubeconfig.yaml
````
In docker-compose.yml that file is mounted on the container and KUBECONFIG environment variable set:
````
services:
  server-api:
    ...
    environment:
     ...
      KUBECONFIG: /root/.kube/config
    volumes:
     ...
      - ./kubeconfig.yaml:/root/.kube/config
````



