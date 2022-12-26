import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyAPI(object):
    sp = None
    my_playlist_link = "https://open.spotify.com/playlist/49bz8n0NjpHqY4w0cIxJnp?si=4d4d578498f34afa"
    my_tracks = None
    billboard_url = 'https://open.spotify.com/playlist/6UeSakyzhiEt4NB3UAd6NQ?si=375a0e0038c24c1f'
    billboard_tracks = None
    billboard_index = 0
    current_artist = None
    artist_top_track = None
    artist_top_track_index = 0
    current_track = None
    preview_url = None
    search_tracks_buffer = None
    search_tracks_index = 0
    search_artist_buffer = None
    search_artist_index = 0

    def __init__(self):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())
        playlist_URI = self.my_playlist_link.split("/")[-1].split("?")[0]
        self.my_tracks = self.sp.playlist_tracks(playlist_URI)["items"]

        billboard_URI = self.billboard_url.split("/")[-1].split("?")[0]
        self.billboard_tracks = self.sp.playlist_tracks(billboard_URI)["items"]

    def get_random_track_url_from_myplaylist(self):
        random_track = random.choice(self.my_tracks)
        self.preview_url = random_track["track"]["preview_url"]
        self.current_track = random_track["track"]

    def preview_track(self):
        if self.preview_url is None:
            return "No track loaded!"
        return self.preview_url

    def search_tracks(self, text):
        self.search_tracks_index = 0
        result = self.sp.search(q=text, type="track", limit=5)[
            "tracks"]["items"]
        self.search_tracks_buffer = result
        self.current_track = result[0]
        self.preview_url = result[0]['preview_url']

    def search_next_track(self):
        if self.search_tracks_buffer == None:
            return
        self.search_tracks_index += 1
        if self.search_tracks_index < 5:
            next_track = self.search_tracks_buffer[self.search_tracks_index]
            self.current_track = next_track
            self.preview_url = next_track['preview_url']

    def search_artist(self, text):
        self.search_artist_index = 0
        result = self.sp.search(q=text, type="artist", limit=5)[
            "artists"]["items"]
        self.search_artist_buffer = result
        self.current_artist = result[0]

    def search_next_artist(self):
        if self.search_artist_buffer == None:
            return
        self.search_artist_index += 1
        if self.search_artist_index < 5:
            next_artist = self.search_artist_buffer[self.search_artist_index]
            self.current_artist = next_artist

    def get_artist_top_track(self):
        self.artist_top_track_index = 0
        self.artist_top_track = self.sp.artist_top_tracks(
            self.current_artist['uri'])['tracks'][:10]
        self.current_track = self.artist_top_track[0]
        self.preview_url = self.current_track['preview_url']

    def get_artist_top_track_next(self):
        self.artist_top_track_index += 1
        if self.artist_top_track_index < 5:
            next_track = self.artist_top_track[self.artist_top_track_index]
            self.current_track = next_track
            self.preview_url = next_track['preview_url']

    def billboard_chart(self):
        chart = "TOP 20 on Billboard:\n"
        for i in range(20):
            track_name = self.billboard_tracks[i]["track"]["name"]
            artist_name = self.billboard_tracks[i]["track"]["artists"][0]["name"]
            chart = chart + str(i + 1) + " : " + \
                artist_name + " - " + track_name
            if i != 19:
                chart += '\n'
        return chart

    def billboard_load_track(self, i):
        i = i - 1
        if i > len(self.billboard_tracks):
            i = 0
        self.billboard_index = i
        load_track = self.billboard_tracks[i]
        self.preview_url = load_track["track"]["preview_url"]
        self.current_track = load_track["track"]

    def billboard_load_next(self):
        if self.billboard_index > len(self.billboard_tracks):
            self.billboard_index = 0
        self.billboard_index += 1
        next_track = self.billboard_tracks[self.billboard_index]["track"]
        self.current_track = next_track

    def billboard_load_random(self):
        self.billboard_index = random.randint(0, len(self.billboard_tracks))
        random_track = self.billboard_tracks[self.billboard_index]
        self.preview_url = random_track["track"]["preview_url"]
        self.current_track = random_track["track"]

    def get_album_cover_art(self):
        return self.current_track['album']['images'][0]['url']

    def get_curr_track_url(self):
        return self.current_track["external_urls"]["spotify"]

    def get_curr_track_name(self):
        return self.current_track['name']

    def get_curr_track_artist(self):
        return self.current_track['artists'][0]['name']

    def get_curr_artist_image(self):
        return self.current_artist['images'][0]['url']

    def get_curr_artist_url(self):
        return self.current_artist["external_urls"]['spotify']

    def get_curr_artist_name(self):
        return self.current_artist['name']

    def get_curr_artist_genre(self):
        return self.current_artist['genres'][0]
