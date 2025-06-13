#!/usr/bin/python3

from pathlib import Path
import sqlite3 as sl
import mutagen

conn = sl.connect('music.db')

paths = conn.execute("SELECT DISTINCT filepath FROM music;").fetchall()
albums, artists, tracks = conn.execute("""
	SELECT 
		COUNT(DISTINCT album) as albums,
		COUNT(DISTINCT artist) as artists,
		COUNt(DISTINCT title) as tracks 
	FROM music;
	""").fetchone()
print(artists, 'artists,', albums, 'albums,', tracks, 'songs')

for p in paths:
	path = p[0]
	#print(path)
	artists = conn.execute("SELECT DISTINCT artist FROM music WHERE filepath=?;", (path,)).fetchall()
	if len(artists) != 1:
		albumartists = conn.execute("SELECT DISTINCT albumartist FROM music WHERE filepath=?;", (path,)).fetchall()
		if len(albumartists) != 1:
			print(f'{path} has more than one album artist: ', albumartists)
		else:
			albumartist = albumartists[0][0]
			#print(f'{path} has multiple artist, but one album artist {albumartist}, phew')
			if albumartist == None:
				printf(f'{path} has more than one artist, but does not have an album artist')

	albums = conn.execute("SELECT DISTINCT album FROM music WHERE filepath=?;", (path,)).fetchall()
	if len(albums) != 1:
		print(f'{path} has more than one album: ', albums)

	disctotals = conn.execute("SELECT DISTINCT disctotal FROM music WHERE filepath=?;", (path,)).fetchall()
	if len(disctotals) != 1:
		print(f'{path} has more than one disc total: ', disctotals)

	discs = conn.execute("SELECT DISTINCT disc FROM music WHERE filepath=?;", (path,)).fetchall()
	for disc in discs:
		disc = disc[0]
		tracktotals = conn.execute("SELECT DISTINCT tracktotal FROM music WHERE filepath=? AND disc=?;", (path,disc)).fetchall()
		if len(tracktotals) != 1:
			print(f'{path} has more than one track total: ', tracktotals)
		else:
			tracktotal = tracktotals[0][0]
			if not tracktotal:
				print(f'{path} has no track total')
			else:
				count, highesttrack = conn.execute("SELECT COUNT(filename), MAX(track) FROM music WHERE filepath=? AND disc=?;", (path,disc)).fetchone()
				if count != tracktotal:
					print(f'{path} number of files ({count}) does not match track count ({tracktotal})')
				if highesttrack != tracktotal:
					print(f'{path} has improperly numbered tracks')
