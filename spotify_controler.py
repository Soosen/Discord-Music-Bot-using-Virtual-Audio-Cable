import spotipy
from spotipy.oauth2 import SpotifyOAuth

class Spotify_Controller():
    def __init__(self, client_id, client_secret, redirect_uri):
        self.sp = sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope="user-read-playback-state,user-modify-playback-state"))
        

    def search_for_song(self, song_name):
        results = self.sp.search(q=song_name, type='track', limit=1)

        if results['tracks']['items']:
            # Get the URI of the first track in the search results
            track_uri = results['tracks']['items'][0]['uri']

            return track_uri
        else:
            return None
        
    def play(self, uri):
        self.sp.start_playback(uris=[uri])

    def next_track(self):
        self.sp.next_track()

    def previous_track(self):
        self.sp.previous_track()

    def add_to_queue(self, track_uri):
        self.sp.add_to_queue(uri=track_uri)

    def clear_queue(self):
        #print(self.sp.queue()["queue"])
        #queue_length = len(self.sp.queue())
        #for i in range(queue_length):
        #    self.next_track()
        pass

    def shuffle(self):
        #TODO
        pass

    def pause(self):
        if(self.is_playing()):
            self.sp.pause_playback()

    def resume(self):
        if(not self.is_playing()):
            self.sp.start_playback()

    def volume(self, volume):
        self.sp.volume(volume)

    def start_playlist(self, playlist_uri):
        playlist_tracks = self.sp.playlist_tracks(playlist_uri)
        tracks_uris = []
        if playlist_tracks['items']:
            for song in playlist_tracks["items"]:
                tracks_uris.append(song["track"]["uri"])
        else:
            print("Playlist is empty.")
        
        self.sp.start_playback(uris=tracks_uris)

    def is_playing(self):
        current_playback = self.sp.current_playback()
        return current_playback and current_playback['is_playing']



