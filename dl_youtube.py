import os

from flask import render_template

from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.firefox.options import Options
from pytube import YouTube

import time
import ipdb
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def download_track_youtube(sp=False, track_id=False, track_artist=False, track_name=False, target_dir=False):

	if track_id:
		sp_track = sp.track(track_id=track_id)
		track_artist = sp_track['artists'][0]['name']
		track_name = sp_track['name']
	else:
		track_artist=track_artist
		track_id=track_id

	base_url = "https://youtube.com/results?search_query="
	query_artist = track_artist.replace(" ",'+')
	query_name = track_name.replace(" ","+")

	query = base_url + query_artist + '+' + query_name
	options = Options()

	#TODO: check all useful options in doc 
	options.add_argument('--headless')
	options.add_argument('--incognito')
	options.add_argument("--blink-settings=imagesEnabled=false")
	options.page_load_strategy = 'eager'
	driver = webdriver.Firefox(options=options)
	
	driver.get(query)

	#TODO: find a better way to wait for the driver
	time.sleep(3)

	first_video = driver.find_element(By.XPATH, '//div[@id="contents"]/ytd-video-renderer[1]')
	video_link = first_video.find_element(By.XPATH, './/h3/a').get_attribute('href')

	try:
		yt = YouTube(video_link)
		audio_stream = yt.streams.filter(only_audio=True).first()
		logger.info(f"	Downloading audio: {track_artist} - {track_name}")
		audio_stream.download(target_dir, filename=f"{track_artist} - {track_name}.mp3")

	except Exception as e:
		logger.error(f"Error: {str(e)}")
	
	finally:
		driver.quit()

def download_spotify_playlist(sp, tracks_dict, playlist_name):
	#TODO: multithread to enhance speed
	tracks_dled = {}
	tracks_error = {}

	target_dir = os.path.join(os.path.expanduser("~"), "Downloads", playlist_name)

	start_time = time.time()


	for track_id, track_info in tracks_dict.items():
		try:
			download_track_youtube(track_artist=track_info.artist, track_name=track_info.name, target_dir=playlist_name)
			tracks_dled[track_info.name] = track_info.artist
		except Exception as e:
			logging.error(f"Error: {str(e)}")
			tracks_error[track_info.name] = track_info.artist
	
	end_time = time.time()

	return render_template('playlistdled.html', 
						tracks_dled=tracks_dled, tracks_error=tracks_error, 
						len_dled=len(tracks_dled), len_error=len(tracks_error),
						elapsed_time = round(end_time - start_time, 2))

def download_manual_playlist(sp, tracks_dict, playlist_name):
	#TODO: multithread to enhance speed
	tracks_dled = {}
	tracks_error = {}

	target_dir = os.path.join(os.path.expanduser("~"), "Downloads", playlist_name)

	start_time = time.time()


	for track_id, track_info in tracks_dict.items():
		try:
			download_track_youtube(track_artist=track_info['artist'], track_name=track_info['name'], target_dir=playlist_name)
			tracks_dled[track_info['name']] = track_info['artist']
		except Exception as e:
			logging.error(f"Error: {str(e)}")
			tracks_error[track_info['name']] = track_info['artist']
	
	end_time = time.time()

	return render_template('playlistdled.html', 
						tracks_dled=tracks_dled, tracks_error=tracks_error, 
						len_dled=len(tracks_dled), len_error=len(tracks_error),
						elapsed_time = round(end_time - start_time, 2))