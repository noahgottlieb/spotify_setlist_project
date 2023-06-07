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

scope = " playlist-modify-public playlist-modify-private playlist-read-private"   # Add necessary scopes here
token = spotipy.util.prompt_for_user_token(
    username=None,
    scope=scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="http://localhost/",
)

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def make_playlist(token, playlist_name, playlist_description, user_id):
    sp = spotipy.Spotify(auth=token)
    sp.trace = False  # Disable request logging (optional)

    # Set up playlist details
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=playlist_description)
    return playlist

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

def add_song_to_playlist(playlist_id,token,track_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = post(url,headers=headers, json = track_uris)
    print(result)
    #print(f"{track_uris} added to {playlist_id} successfully")

user_id = 'w7yp1pgf2uijxhie92zllkt1g'
playlist_name = "Noah's Mac Miller playlist"
playlist_description = "my THIRD playlist created through an API"

playlist_id = make_playlist(token,playlist_name,playlist_description,user_id)["id"]
#playlist_id = "1bVr4uiyCYEaxNIMDekEWQ"

artist_id = search_for_artist(token,"mac miller")["id"]

#track_uris = ["spotify:track:5iUQMwxUPdJBFeGkePtM66","spotify:track:1DWZUa5Mzf2BwzpHtgbHPY"]
songs = get_songs_by_artist(token,artist_id)

track_uris =[]
for idx,song in enumerate(songs):
    track_uris.append(song['uri'])

#print(songs_list)
add_song_to_playlist(playlist_id,token,track_uris)
