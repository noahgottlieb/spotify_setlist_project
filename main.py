
#Load Environment variables
from dotenv import load_dotenv
import os
from requests import post,get
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import pandas as pd

load_dotenv()
#Pull Environment variables from .env file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
setlist_api_key = os.getenv("SETLIST_API_KEY")

#Define spotipy scope
scope = " playlist-modify-public playlist-modify-private playlist-read-private"   # Add necessary scopes here
token = spotipy.util.prompt_for_user_token(
    username=None,
    scope=scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="http://localhost/",
)

#Authentication with Spotipy
#Every GET or POST will need to authenticate with Spotipy using the users credentials
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

#Make a brand new playlist
def make_playlist(token, playlist_name, playlist_description, user_id):
    sp = spotipy.Spotify(auth=token)
    sp.trace = False  # Disable request logging (optional)

    # Set up playlist details
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=playlist_description)
    return playlist

#Get the Spotify backend artist id for the artist name
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

#Get the Spotify backend track URI's for each of the song names
def get_tracks(token,artist,song_name):
    # Set up the API endpoint and parameters
    url = 'https://api.spotify.com/v1/search'
    headers  = get_auth_header(token)
    params = {
        'q': f'track:{song_name} artist:{artist}',
        'type': 'track',
    }
    result = get(url, headers=headers, params=params)
    data = None
    try:
        data = json.loads(result.content)['tracks']['items'][0]['uri']
    except IndexError:
        pass
    return data

#Add each of the track URI's to the predefined playlist from make_playlist
def add_song_to_playlist(playlist_id,token,track_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = post(url,headers=headers, json = track_uris)
    print(f"{track_uris} added to {playlist_id} successfully")

    if result.status_code == 400:
        error_message = result.json()['error']['message']  # Extract the error message from the response
        print(f"Error: {error_message}")
    else:
        print('Your Spotify playlist is ready!')

#Get the artists most recent, filled out setlist from setlist.fm
def get_setlist_artist(api,artist_name):
    url = 'https://api.setlist.fm/rest/1.0/search/setlists'
    headers = {
        'Accept': 'application/json',
        'x-api-key': api
    }
    params = {
        'artistName': artist_name,
        'p': 1
    }
    response = get(url,headers=headers,params=params)


    set = json.loads(response.content)["setlist"]
    
    #Iterate past blank setlists to get the most up to date filled out setlist
    finish = ''
    index = 0
    while finish !='done':
        result = json.loads(response.content)["setlist"][index]["sets"]["set"]
        if len(result) > 0:
            finish='done'
            continue
        else:
            index+=1

    return [result,index]

#Get the setlist details like the tour date, venue, city, state, country to add to the playlist title/subtitle
def get_playlist_title(api,artist_name,index):
    url = 'https://api.setlist.fm/rest/1.0/search/setlists'
    headers = {
        'Accept': 'application/json',
        'x-api-key': api
    }
    params = {
        'artistName': artist_name,
        'p': 1
    }
    response = get(url,headers=headers,params=params)
    unpack = json.loads(response.content)['setlist'][index]
    tour_date = unpack['eventDate']
    date_obj = datetime.strptime(tour_date, '%d-%m-%Y')
    formatted_tour_date = date_obj.strftime('%B %d, %Y')

    try:
        tour_name = unpack['tour']['name']
    except KeyError:
        tour_name = None
    venue = unpack['venue']['name']
    city = unpack['venue']['city']['name']
    state =unpack['venue']['city']['state']
    country = unpack['venue']['city']['country']['name']
    if tour_name != None:
        playlist_title = artist_name.title() + ' ' + tour_name + ' on '+formatted_tour_date
        playlist_description = 'Played at ' + venue +' in ' + city+', '+state + ', ' + country

    else:
        playlist_title = artist_name.title() + ' on '+formatted_tour_date
        playlist_description = 'Played at ' + venue +' in ' + city+', '+state + ', ' + country


    return [playlist_title,playlist_description]

def format_song_and_artist(token,set,track_uris):
    index = 0
    for sets in set:
   
     for songs in sets['song']:

    #Ignore the tape variables, these are just songs played prior to the show starting
        try:
           songs['tape']
        except KeyError:
            try:
                #If there is a cover in the set list, add to the dataframe
               if  len(songs['cover']) > 0:

                artist_name = songs['cover']['sortName']            
                artist_id = search_for_artist(token,artist_name)["id"]
                song = songs['name']
                song_id = get_tracks(token,artist_name,song)

                #Add to the track_uri list for ingestion into playlist
                track_uris.append(song_id)
                
                #Add to index
                index += 1

            except KeyError:
                artist_id = search_for_artist(token,artist)["id"]
                song = songs['name']
                song_id = get_tracks(token,artist,song)

                track_uris.append(song_id)

                index += 1

    return track_uris
#########################################################################################################################################
"""
Here is where the execution of the code begins
"""
#Get user input for the 
artist = input("Please enter the artist you would like to get the latest setlist from ")

#TODO: Update this variable to pull in any users id
user_id = 'w7yp1pgf2uijxhie92zllkt1g'

#Based on the users input, find the artists most recent, non-null setlist and the index of that setlist
setlist ={}
set = get_setlist_artist(setlist_api_key,artist)[0]
index = get_setlist_artist(setlist_api_key,artist)[1]



#Name the playlist based on the the details from the set
playlist_name = get_playlist_title(setlist_api_key,artist,index)[0]
#TODO: Update the name and description to be...better
playlist_description = get_playlist_title(setlist_api_key,artist,index)[1]

#Create a new blank playlist
playlist_id = make_playlist(token,playlist_name,playlist_description,user_id)["id"]


#Create a list of track_uris in order of the set to pass to the playlist (Also captures covers)
track_uris =[]
df = pd.DataFrame(columns = ['artist_id','artist','song_id','song'])
format_song_and_artist(token,set,track_uris)

#Remove any tracks the code was unable to capture
track_uris = list(filter(lambda x: x is not None,track_uris))

#Add the list of songs to your playlist
add_song_to_playlist(playlist_id,token,track_uris)
