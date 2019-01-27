import pylast
import spotipy
import datetime
import calendar
import time

###################### EDIT THESE VALUES ##################
# lastm creds
apikey_lastfm = ""
apisecret_lastfm = ""
username_lastfm = ""
password_hash_lastfm = "" # echo "password" | md5sum

# time period
start = datetime.datetime(2011, 7, 21, 15, 10)
end = datetime.datetime(2011, 7, 21, 15, 15)

# spotify creds
spotify_client_id = ""
spotify_client_secret = ""
redirect_url = "" # set this in spotify api key settings

# target playlist (will be newly created)
playlistname = "last-fm-timemachine"
##########################################################

def song_to_str(tophit):
    return " - ".join(tophit['name'],tophit['artists'][0]['name'], tophit['album']['name'])

def main():
    # set up connection with last.fm API
    network = pylast.LastFMNetwork(api_key=apikey_lastfm,api_secret=apisecret_lastfm,username=username_lastfm,password_hash=password_hash_lastfm)
    user = network.get_user(username_lastfm)
    # test of working API
    country = user.get_country()
    regi = user.get_registered()
    print("User",user.name,"registered on",datetime.datetime.fromtimestamp(int(regi)),"from",country)

    # convert start and end to format last.fm understands
    utc_start = calendar.timegm(start.utctimetuple())
    utc_end = calendar.timegm(end.utctimetuple())

    print("Start:",start)
    print("End:",end)
    results_lastfm = user.get_recent_tracks(limit=None, time_from=utc_start, time_to=utc_end)
    #put results in chronological order
    results_lastfm.reverse()
    print(len(results_lastfm),"results found within this time period.")

    # spotify
    # we start with the oauth dance
    # we use the "authorization code" authorization flow (option 1)
    # docs here: https://developer.spotify.com/documentation/general/guides/authorization-guide/
    # good example of oauth dance implementation:  https://stackoverflow.com/questions/25711711/spotipy-authorization-code-flow

    # info about scopes here: https://developer.spotify.com/documentation/general/guides/scopes/
    scope = "playlist-modify-private playlist-read-private"
    
    # specify oauth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=spotify_client_id,client_secret=spotify_client_secret,redirect_uri=redirect_uri,scope=scope)
    # user gives permission for our scope
    print("Open this URL in your browser. Authorize the application. Spotify will then redirect you to the redirect-url you chose when you registered your application. Copy-paste the full url of that redirect (including request parameters) into the terminal.")
    print(sp_oauth.get_authorize_url())
    print("Url:")
    url = input()
    # user passes authorization code on to application
    code = sp_oauth.parse_response_code(redirect_url)
    # application passes authorization code to spotify and obtains an access token
    token_info = sp_oauth.get_access_token(code)
    token = token_info['access_token']
    # application authorises itself with access token and can now function with the scope
    spotify = spotipy.Spotify(token)

    print("You are now authorized for user",spotify.me()['name'])

    spotify_user_id = spotify.me()['id']

    # create a new playlist
    spotify.user_playlist_create(user=spotify_user_id,name=playlistname,public="False") # note that we don't have privileges (scope) for creating public playlists

    # check existence and tracks
    playlists = spotify.user_playlists(user=spotify_user_id)
    for p in playlists['items'][:5]: # new playlist should be in top 5
      print(p['name'],p['id'])

    test_playlist_id = [playlist for playlist in playlists['items'] if playlist['name'] == playlistname][0]['id']
    spotify.user_playlist_tracks(user=spotify_user_id,playlist_id=test_playlist_id)

    # search for the songs from your last-fm history
    songs_to_add = []
    songs_not_found = []
    for song in results_lastfm:
        print("Searching:",song.track.artist.name, song.track.title)
        query = song.track.artist.name + " " + song.track.title
        results = spotify.search(type='track',market='NL',q=query)
        if results['tracks']['total'] > 0:
            tophit = results['tracks']['items'][0]
            print("Found song:", song_to_str(tophit))
            songs_to_add.append(tophit['id'])
        else:
            print("Error: song not found.")
            songs_not_found.append(" - ".join([song.track.artist.name, song.track.title]))

    # statistics about searching
    print()
    print("Total found:",len(songs_to_add))
    print("Total unknowns:",len(songs_not_found))
    print()

    for song in songs_not_found:
      print(song)

    # add the found sounds to the newly created playlist
    max_per_request = 100
    l = songs_to_add
    songs_to_add_chunks = [l[i:i + max_per_request] for i in range(0, len(l), max_per_request)]
    for chunk in songs_to_add_chunks:
      spotify.user_playlist_add_tracks(user=spotify_user_id,playlist_id=test_playlist_id,tracks=chunk)
      time.sleep(1)
