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
    songlist = []
    for tr in toplist:
        query = " ".join(tr).lower()
        try:
            results = spotify.search(q=query, type='track', market="NL") #setting the market had a big influence on the quality of the results
        except Exception as e:
            print(e)
            continue
        sleep(0.1) # max 10 queries per second is more than enough
        print(results['tracks']['total'], query)
        # if we can't find the song, try again but without the album name
        # might lead to false positives
        if results['tracks']['total'] == 0:
            query = (tr[0] + " " + tr[2]).lower()
            try:
                results = spotify.search(q=query, type='track', market="NL")
            except Exception as e:
                print(e)
                continue
            sleep(0.1) # max 10 queries per second is more than enough
            print(results['tracks']['total'], query)
            if results['tracks']['total'] == 0:
                #pprint.pprint(results)
                notfound += 1
                songlist.append(query)
    print("Total tracks not found: " + str(notfound))
    for song in songlist:
        print(song)
