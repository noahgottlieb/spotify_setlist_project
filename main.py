#Load Environment variables
from dotenv import load_dotenv
import os
import base64 
from requests import post
import json
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    #Concat client id and client secret, encode in base 64 pass to spotify and get access token
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf_8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_results = json.loads(result.content)
    token = json_results["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer" + token}

token = get_token()
auth_header = get_auth_header(token)

print(auth_header)