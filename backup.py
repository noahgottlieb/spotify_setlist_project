#Load Environment variables
from dotenv import load_dotenv
import os
import base64 
from requests import post,get
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

scope = "playlist-modify-private"  # Add necessary scopes here
token_2 = spotipy.util.prompt_for_user_token(
    username=None,
    scope=scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="http://localhost/",
)

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
    return {"Authorization": "Bearer " + token}


#def make_playlist(token, playlist_name, playlist_description, user_id):
#    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
#    data = {"name": playlist_name, "description": playlist_description, "public": True}
#    headers = get_auth_header(token)
#    response = post(url, headers=headers, json=data)
#    return response

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url,headers = headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists..")
        return None
    return json_result[0]

def get_songs_by_artist (token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url,headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def make_playlist(token, playlist_name, playlist_description, user_id):
    sp = spotipy.Spotify(auth=token)
    sp.trace = False  # Disable request logging (optional)

    # Set up playlist details
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=playlist_description)
    return playlist


token = get_token()
result = search_for_artist(token,"future")
artist_id = result["id"]
user_id = 'w7yp1pgf2uijxhie92zllkt1g'

#print(make_playlist(token_2,"test playlist","my very first playlist create through an API",user_id))
songs = get_songs_by_artist(token_2, artist_id)

for idx,song in enumerate(songs):
    print(song['name'])
