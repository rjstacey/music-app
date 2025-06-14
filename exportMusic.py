#!/usr/bin/python3

from pathlib import Path
import os, shutil, subprocess
from shutil import copy2
import sqlite3 as sl
import mutagen
import sys, getopt, re
from music import MusicFile

soxPath = "/usr/bin/sox"
ffmpegPath = "/usr/bin/ffmpeg"

class Options:
	def __init__(self, argv):
		name = argv.pop(0)
		self.outputdir = './MyMusic'
		self.replace = False
		try:
			opts, args = getopt.getopt(argv, "ho:", ["odir="])
		except getopt.GetoptError:
			print(f'{name} [-o <outputdir>] [-r]')
			sys.exit(2)
		for opt, arg in opts:
			if opt == '-h':
				print(f'{name} [-o <outputdir>] [-r]')
				sys.exit()
			elif opt in ("-o", "--odir"):
				self.outputdir = arg
			elif opt == '-r':
				self.replace = True

import unicodedata

def normalize(filename):
    cleanedFilename = unicodedata.normalize('NFKD', filename) #.encode('ASCII', 'ignore')
    return re.sub(r"[\/\\:*?<>|^]+", r'_', cleanedFilename)

def genFilename(entry):
	name = ''
	numdiscs = entry['disctotal'] or 1
	if numdiscs > 1:
		name += f"{entry['disc']}-"
	name += f"{int(entry['track'] or '0'):02} {entry['title']}"
	#filename, ext = os.path.splitext(entry['filename'])
	return normalize(name)# + ext

def genType(entry):
	if entry['filetype'] == 'flac' or entry['filetype'] == 'mp4':
		return f"{entry['filetype']}-{entry['bits_per_sample']}-{entry['sample_rate']}"
	elif entry['filetype'] == 'mp3':
		return f"{entry['filetype']}-{entry['bitrate_mode']}-{entry['bitrate']}"
	else:
		return entry['filetype']

def destinationDir(outputdir, artist, album):
	dest = os.path.join(outputdir, normalize(artist))
	if not os.path.exists(dest):
		os.mkdir(dest)
	dest = os.path.join(dest, normalize(album))
	return dest

def copyFile(destinationDir, entry):
	src = os.path.join(entry['filepath'], entry['filename'])
	description = f"\t\t{int(entry['track'] or '0'):02} {entry['title']} \t{genType(entry)}"

	ext = '.mp3' if entry['filetype'] == 'mp3' else '.m4a'
	filename = genFilename(entry) + ext
	dest = os.path.join(destinationDir, filename)
	if os.path.exists(dest) and options.replace:
		os.remove(dest)

	if (os.path.exists(dest)):
		print(description, ' Already exists')
		return
	
	try:
		if entry['filetype'] == 'flac' or entry['filetype'] == 'mp4':
			print(description, ' Transcoding')
			subprocess.run([ffmpegPath, '-loglevel', 'quiet', '-i', src, '-map', 'a:0', '-c:a', 'aac', '-ar', '44100', '-b:a', '256k', dest])
		elif entry['filetype'] == 'mp3':
			print(description, ' Copying')
			copy2(src, dest)
	except:
		if os.path.exists(dest):
			os.remove(dest)
		exit(1)
		return

def main(options):
	conn = sl.connect('music.db')
	conn.row_factory = sl.Row

	rows = conn.execute("SELECT DISTINCT albumartist FROM music ORDER BY albumartist;")
	artists = list(map(lambda r: r['albumartist'], rows))
	for artist in artists:
		print(artist)
		rows = conn.execute("SELECT DISTINCT album FROM music WHERE albumartist=? ORDER BY album;", (artist,))
		albums = list(map(lambda r: r['album'], rows))
		artistDir = os.path.join(options.outputdir, normalize(artist))
		if not os.path.exists(artistDir):
			os.mkdir(artistDir)
		for album in albums:
			print(f'\t{album}')
			rows = conn.execute("SELECT * FROM music WHERE albumartist=? AND album=? ORDER BY filepath, disc, track;", (artist,album))
			albumDir = os.path.join(artistDir, normalize(album))
			if options.replace:
				shutil.rmtree(albumDir, ignore_errors=True) 
			os.makedirs(albumDir, exist_ok=True)
			for entry in rows:
				copyFile(albumDir, entry)


if __name__ == "__main__":
	options = Options(sys.argv)
	main(options)