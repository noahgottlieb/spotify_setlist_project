#Load Environment variables
from dotenv import load_dotenv
import os
import base64 
from requests import post,get
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime


load_dotenv()

setlist_api_key = os.getenv("SETLIST_API_KEY")

def setlist_fm_token(api,artist_name):
    url = 'https://api.setlist.fm/rest/1.0/search/setlists'
    headers = {
        'Accept': 'application/json',
        'x-api-key': api
    }
    params = {
        'artistName': artist_name,
        'p': 1
    }
    return [url,headers,params]

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


#Get the artists most recent, filled out setlist from setlist.fm
def get_setlist_artist(api,artist_name):

    url = setlist_fm_token(setlist_api_key,artist)[0]
    headers = setlist_fm_token(setlist_api_key,artist)[1]
    params = setlist_fm_token(setlist_api_key,artist)[2]
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

    url = setlist_fm_token(setlist_api_key,artist)[0]
    headers = setlist_fm_token(setlist_api_key,artist)[1]
    params = setlist_fm_token(setlist_api_key,artist)[2]

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
        playlist_title = tour_name + ' on '+formatted_tour_date + ' at ' +venue +' in ' + city+', '+state + ', ' + country
    else:
        playlist_title = artist_name.title() + ' on '+formatted_tour_date + ' at ' +venue +' in ' + city+', '+state + ', ' + country


    return playlist_title

artist = 'kendrick lamar'
setlist ={}
set = get_setlist_artist(setlist_api_key,artist)[0]
index = get_setlist_artist(setlist_api_key,artist)[1]

#TODO Get be able to iterate through multiple sets and get the songs. If we just take the 
for sets in set:
     
     for songs in sets['song']:
    #Ignore the tape variables, these are just songs played prior to the show starting
        try:
           songs['tape']
        except KeyError:
            try:
               if  len(songs['cover']) > 0:
                   setlist[songs['name']] = songs['cover']['sortName']
            except KeyError:
                setlist[songs['name']] = artist
        
        # setlist.append(songs['name'])
        #print(songs)
print(setlist)
       