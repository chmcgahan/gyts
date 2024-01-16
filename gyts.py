#!/usr/bin/python3

"""
todo: all the todo's
    add multithreading
    dockerise it ?
    put on a real server (render seems promising)
    add testing files ? what to test - and how ?
    add a database ? just to store the number of visitors, the number of songs downloaded ?
    react (front end in general) (need more storage)
    use poetry (--- need python 3.9, need xcode, need more storage...)
"""

import os
from flask import Flask, session, request, redirect, url_for, render_template
from flask_session import Session
import spotipy

from get_tracks import get_cu_playlists, get_playlist_tracks
from dl_youtube import download_track_youtube, download_playlist_youtube

import ipdb
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['FLASK_DEBUG']=1

app.config['ENV'] = 'development' if app.config.get('FLASK_DEBUG') == '1' else 'production'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")


@app.route('/')
def index():
    cache_handler, auth_manager = get_cache_and_auth_manager()
    
    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('index.html', auth_url=auth_url)

    # Step 3. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return render_template('index.html', me=spotify.me()['display_name'])

@app.route('/login')
def login():
    cache_handler, auth_manager = get_cache_and_auth_manager()
    auth_url = auth_manager.get_authorize_url()
    return url_for(auth_url)

@app.route('/logout')
def logout():
    session.pop("token_info", None)
    return redirect('/')

@app.route('/playlists')
def playlists():
    cache_handler, auth_manager = get_cache_and_auth_manager()
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    sp = spotipy.Spotify(auth_manager=auth_manager)
    # return sp.current_user_playlists()
    return get_cu_playlists(sp)

@app.route('/mytracks')
def my_tracks():
    cache_handler, auth_manager = get_cache_and_auth_manager()
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return get_playlist_tracks(sp, render=True)

@app.route('/download_track/<track_id>')
def download_track(track_id):
    cache_handler, auth_manager = get_cache_and_auth_manager()
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    
    sp = spotipy.Spotify(auth_manager=auth_manager)
    download_track_youtube(sp, track_id)
    return redirect('/')

@app.route('/download_playlist/<playlist_id>')
def download_playlist(playlist_id):
    cache_handler, auth_manager = get_cache_and_auth_manager()
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    
    sp = spotipy.Spotify(auth_manager=auth_manager)
    playlist_name = sp.user_playlist(user=None, playlist_id=playlist_id, fields="name")
    tracks_dict = get_playlist_tracks(sp, playlist_id=playlist_id)

    #TODO: first render the playlist's tracks with a button to download it
    return download_playlist_youtube(sp, tracks_dict, playlist_name['name'])


def get_cache_and_auth_manager():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    return cache_handler, spotipy.oauth2.SpotifyOAuth(scope='playlist-read-private \
                                                      user-library-read',
                                                client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                cache_handler=cache_handler,
                                                show_dialog=True)

@app.errorhandler(403)
def not_authorized(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=app.config.get('FLASK_DEBUG') == 0, port=10000)
