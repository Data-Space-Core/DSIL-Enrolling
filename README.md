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

