from time import sleep
import pprint
import spotipy
import spotipy.oauth2 as oauth2
from collections import Counter

def get_spotify(filename):
    with open(filename,"r") as infile:
      credentials = infile.readline()
    clientid, clientsecret = credentials.strip().split(",")

    credentials = oauth2.SpotifyClientCredentials(
            client_id=clientid,
            client_secret=clientsecret)
    token = credentials.get_access_token()
    spotify = spotipy.Spotify(auth=token)
    return spotify

def get_stats(filename):
    rawdata = []
    with open(filename,"r") as infile:
      rawdata = infile.readlines()
    len(rawdata)
    data = []
    for d in rawdata:
      data.append(d.strip().split(","))
    len(data)
    return data

def top_n(data,n):
    tracks = [] # concatenated, no timestamps
    # last column of csv contains timestamps (we don't need those)
    # Counter cannot deal with list-objects, that's why I join the strings
    for d in data:
        tracks.append(";".join(d[:-1]))
    top = Counter(tracks).most_common(n) 
    toplist = []
    for t in top:
        toplist.append(t[0].split(";"))
    return toplist

# quick n dirty main function that prints what I need
def search_spotify(spotify,toplist):      
    notfound = 0
    for tr in toplist:
       try:
         results = spotify.search(q=" ".join(tr).lower(), type='track')
         sleep(0.1) # max 10 queries per second is more than enough
         name = results['tracks']['items'][0]['name']
       except Exception as e:
         print(e)
         notfound += 1
         print("Could not find track: " + " / ".join(tr))
    print("Total tracks not found: " + str(notfound))
