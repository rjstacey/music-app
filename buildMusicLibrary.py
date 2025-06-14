#!/usr/bin/python3

from pathlib import Path
import sqlite3 as sl
import mutagen
from music import MusicFile

conn = sl.connect('music.db')

conn.execute("""
	DROP TABLE IF EXISTS MUSIC;
	""")
conn.execute("""
	CREATE TABLE MUSIC (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		filepath TEXT,
		filename TEXT,
		filetype TEXT,
		bitrate_mode INTEGER,
		bitrate INTEGER,
		bits_per_sample INTEGER,
		sample_rate INTEGER,
		title TEXT,
		artist TEXT,
		albumartist TEXT,
		album TEXT,
		genre TEXT,
		composer TEXT,
		track INTEGER,
		tracktotal INTEGER,
		disc INTEGER,
		disctotal INTEGER,
		releasedate TEXT
	)
	""")

p = Path('../mnt/HD')
#p = Path('../mnt/Classical/Artur Rubinstein') #mp3
#p = Path('../mnt/Classical/András Schiff') #mp4
#p = Path('../mnt/Classical/Anne Akiko Meyers, David Lockington, English Chamber Orchestra') #flac

def tag(tags, key, default=''):
	if key in tags:
		v = tags[key][0]
		try:
			v = v.decode('utf-8')
		except (UnicodeDecodeError, AttributeError):
			pass
		return v
	else:
		return default

def analyze(file):
	try:
		f = mutagen.File(file, easy=False)
	except:
		print(f'Error reading file: {file}')
		return None
	
	if not f:
		return None

	if isinstance(f, mutagen.flac.FLAC):
		filetype = 'flac'
	elif isinstance(f, mutagen.mp4.MP4):
		filetype = 'mp4'
	elif isinstance(f, mutagen.mp3.MP3):
		filetype = 'mp3'
	else:
		return None
		#raise Exception('Unexpected file type')

	# File properties
	entry = MusicFile(str(file.parent), file.name, filetype)

	#print(f'{file.name} "{filetype}"')
	#print(filename)
	# Stream info
	entry.length = f.info.length

	if isinstance(f, mutagen.mp3.MP3):
		entry.setLossyEncoding(f.info.bitrate_mode, f.info.bitrate)
	else:
		entry.setLosslessEncoding(f.info.bits_per_sample, f.info.sample_rate)

	#print(f.info.sample_rate, f.info.bits_per_sample)
	if (filetype == 'mp4'):
		entry.title = tag(f.tags, '\xa9nam')
		entry.artist = tag(f.tags, '\xa9ART')
		entry.albumartist = tag(f.tags, 'aART')
		entry.album = tag(f.tags, '\xa9alb')
		entry.composer = tag(f.tags, '\xa9wrt')
		entry.genre = tag(f.tags, '\xa9gen')
		entry.track = tag(f.tags, 'trkn')
		entry.disc = tag(f.tags, 'disk')
		entry.date = tag(f.tags, '\xa9day')
		entry.media = tag(f.tags, '----:com.apple.iTunes:MEDIA')
		entry.recordlabel = tag(f.tags, '----:com.apple.iTunes:LABEL')
		entry.originaldata = tag(f.tags, '----:com.apple.iTunes:originaldate')
		if isinstance(entry.track, tuple):
			entry.track, entry.tracktotal = entry.track
		else:
			entry.tracktotal = None
		if isinstance(entry.disc, tuple):
			entry.disc, entry.disctotal = entry.disc
		else:
			entry.disctotal = None
		#print(f.tags.pprint())
	elif filetype == 'flac':
		entry.title = tag(f.tags, 'title')
		entry.artist = tag(f.tags, 'artist')
		entry.albumartist = tag(f.tags, 'albumartist')
		entry.album = tag(f.tags, 'album')
		entry.composer = tag(f.tags, 'composer')
		entry.genre = tag(f.tags, 'genre')
		entry.track = tag(f.tags, 'tracknumber')
		entry.tracktotal = tag(f.tags, 'TRACKTOTAL')
		entry.disc = tag(f.tags, 'discnumber')
		entry.disctotal = tag(f.tags, 'DISCTOTAL')
		entry.date = tag(f.tags, 'date')
		entry.media = tag(f.tags, 'MEDIA')
		entry.recordlabel = tag(f.tags, 'LABEL')
		entry.originaldata = tag(f.tags, 'ORIGINALDATE')
		#print(f.tags.pprint())
	elif (filetype == 'mp3'):
		entry.title = tag(f.tags, 'TIT2')
		entry.artist = tag(f.tags, 'TPE1')
		entry.albumartist = tag(f.tags, 'TPE2')
		entry.album = tag(f.tags, 'TALB')
		entry.composer = tag(f.tags, 'TCOM')
		entry.genre = tag(f.tags, 'TCON')
		entry.track = tag(f.tags, 'TRCK')
		entry.disc = tag(f.tags, 'TPOS')
		date = tag(f.tags, 'TDRC')
		entry.date = date if (type(date) == str) else date.get_text()
		entry.media = tag(f.tags, 'TMED')
		entry.recordlabel = tag(f.tags, 'TPUB')
		entry.originaldata = tag(f.tags, 'TDOR')
		try:
			entry.track, entry.tracktotal = entry.track.split('/', 1)
		except ValueError:
			entry.tracktotal = None
		try:
			entry.disc, entry.disctotal = entry.disc.split('/', 1)
		except ValueError:
			entry.disctotal = None
		#print(f.tags.pprint())

	#print(type(entry.date))
	print(f'{entry.getArtist()} - {entry.album}: track {entry.track}/{entry.tracktotal}: "{entry.title}" ')
	conn.execute("""
		INSERT INTO MUSIC(
			filepath, filename, filetype,
			bitrate_mode, bitrate, bits_per_sample, sample_rate, 
			genre, artist, album, title, albumartist, composer, releasedate,
			track, tracktotal, disc, disctotal)
		VALUES (
			?, ?, ?,
			?, ?, ?, ?,
			?, ?, ?, ?, ?, ?, ?,
			?, ?, ?, ?);
		""", (entry.filepath, entry.filename, entry.filetype,
			entry.bitrate_mode, entry.bitrate, entry.bits_per_sample, entry.sample_rate,
			entry.genre, entry.artist, entry.album, entry.title, entry.getArtist(), entry.composer, entry.date,
			entry.track, entry.tracktotal, entry.disc, entry.disctotal))


i = 0

def walk(p):
	for x in p.iterdir():
		global i
		i = i + 1
		#if (i > 1000):
		#	return
		if i % 100 == 0:
			print(i)
		if x.is_dir():
			walk(x)
		else:
			#print(x)
			analyze(x)
			
try:
	walk(p)
except KeyboardInterrupt:
	pass
conn.commit()