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
    data = []
    with open(filename,"r") as infile:
      data = infile.readlines()
    len(data)
    data2 = []
    for d in data:
      data2.append(d.strip().split(","))
    len(data2)
    return data2

def top_n(data,n):
    tracks = [] # concatenated, no timestamps
    for d in data:
        tracks.append(";".join(d[:-1]))
    top = Counter(tracks).most_common(n)
    toplist = []
    for t in top:
        toplist.append(t[0].split(";"))
    return toplist

def search_spotify(spotify,toplist):      
    notfound = 0
    for tr in toplist:
       try:
         results = spotify.search(q=" ".join(tr), type='track')
         sleep(0.1)
         name = results['tracks']['items'][0]['name']
       except Exception as e:
         print(e)
         notfound += 1
         print("Could not find track: " + " / ".join(tr))
    print("Total tracks not found: " + str(notfound))
