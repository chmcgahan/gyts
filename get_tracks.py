import ipdb
from spotipy.oauth2 import SpotifyClientCredentials
from flask import render_template

class Track:
	def __init__(self, id, name, artist):
		self.id = id
		self.name = name
		self.artist = artist

	def __str__(self):
		return f"Track {self.name} by {self.artist}"

class Playlist:
	def __init__(self, id, name, tracks, owner, tracks_count) -> None:
		self.id = id
		self.name = name
		self.tracks = tracks
		self.owner = owner
		self.tracks_count = tracks_count

	def __str__(self) -> str:
		return f"Playlist {self.name} from {self.owner} has {len(self.tracks)} tracks."
	
	def download_playlist(self):
		return True

def get_cu_playlists(sp):
	playlists_dict = {}
	cu_playlists = sp.current_user_playlists(limit=50, offset=0)['items']
	for pl in cu_playlists:
		pl_name = pl.get("name")
		pl_owner = pl.get("owner")['display_name']
		pl_tracks_id = pl.get("tracks")['href']
		pl_id = pl.get('id')
		pl_tracks_count = pl.get('tracks')['total']
		if pl_name and pl_owner and pl_tracks_id and pl_id:
			playlists_dict[pl_id] = Playlist(id=pl_id, tracks=pl_tracks_id,name=pl_name, owner=pl_owner, tracks_count=pl_tracks_count)
	return render_template('playlists.html', playlist=playlists_dict)

def get_playlist_tracks(sp, playlist_id=False, render=False):
	tracks_dict = {}
	if not playlist_id:
		tracks_json = sp.current_user_saved_tracks(limit=50, offset=0)
	else:
		tracks_json = sp.playlist_items(playlist_id=playlist_id)
	
	tracks = tracks_json['items']
	# can change this to allow more than 100 songs, tho it would take a long time
	if tracks_json['next']:
		tracks_json = sp.next(tracks_json)
		tracks.extend(tracks_json['items'])
	
	for tr in tracks:
		tr_id = tr['track']['id']
		tr_artist = tr['track']['artists'][0]['name']
		tr_name = tr['track']['name']
		if tr_id and tr_artist and tr_name:
			tracks_dict[tr_id] = Track(id=tr_id, name=tr_name, artist=tr_artist)
	if render:
		return render_template('tracks.html', tracks=tracks_dict)
	else:
		return tracks_dict