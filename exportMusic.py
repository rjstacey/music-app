#!/usr/bin/python3

from pathlib import Path
import os, subprocess
from shutil import copy2
import sqlite3 as sl
import mutagen
import sys, getopt, re
from music import MusicFile

class Options:
	def __init__(self, argv):
		name = argv.pop(0)
		self.outputdir = './MyMusic'
		try:
			opts, args = getopt.getopt(argv, "ho:", ["odir="])
		except getopt.GetoptError:
			print(f'{name} -o <outputdir>')
			sys.exit(2)
		for opt, arg in opts:
			if opt == '-h':
				print(f'{name} -o <outputdir>')
				sys.exit()
			elif opt in ("-o", "--odir"):
				self.outputdir = arg

import unicodedata

def normalize(filename):
    cleanedFilename = unicodedata.normalize('NFKD', filename) #.encode('ASCII', 'ignore')
    return re.sub(r"[\/\\:*?<>|^]+", r'_', cleanedFilename)

def genFilename(entry):
	name = ''
	numdiscs = entry['totaldisc'] or 1
	if numdiscs > 1:
		name += f"{entry['disc']}-"
	name += f"{int(entry['track'] or '0'):02} {entry['title']}"
	filename, ext = os.path.splitext(entry['filename'])
	return normalize(name) + ext

def genType(entry):
	if entry['filetype'] == 'flac' or entry['filetype'] == 'mp4':
		return f"{entry['filetype']}-{entry['bits_per_sample']}-{entry['sample_rate']}"
	elif entry['filetype'] == 'mp3':
		return f"{entry['filetype']}-{entry['bitrate_mode']}-{entry['bitrate']}"
	else:
		return entry['filetype']


def copyFile(outputdir, entry):
	src = os.path.join(entry['filepath'], entry['filename'])
	dest = os.path.join(outputdir, normalize(entry['albumartist']))
	if not os.path.exists(dest):
		os.mkdir(dest)
	dest = os.path.join(dest, normalize(entry['album']))
	if not os.path.exists(dest):
		os.mkdir(dest)
	dest = os.path.join(dest, genFilename(entry))
	
	print('\t', genType(entry), '\t', f"{int(entry['track'] or '0'):02} {entry['title']}")
	if not os.path.exists(dest):
		if entry['filetype'] == 'flac' or entry['filetype'] == 'mp4':
			if entry['bits_per_sample'] > 16 or entry['sample_rate'] > 44100:
				subprocess.run(['./sox', src, '-b', '16', '-r', '44100', '-t', 'flac', dest, '-G'])
			else:
				copy2(src, dest)
		elif entry['filetype'] == 'mp3':
			copy2(src, dest)

def main(options):
	conn = sl.connect('music.db')
	conn.row_factory = sl.Row

	rows = conn.execute("SELECT DISTINCT albumartist FROM music ORDER BY albumartist;")
	artists = list(map(lambda r: r['albumartist'], rows))
	for artist in artists:
		print(artist)
		rows = conn.execute("SELECT DISTINCT album FROM music WHERE albumartist=? ORDER BY album;", (artist,))
		albums = list(map(lambda r: r['album'], rows))
		for album in albums:
			print(f'\t{album}')
			rows = conn.execute("SELECT * FROM music WHERE albumartist=? AND album=? ORDER BY filepath, disc, track;", (artist,album))
			for entry in rows:
				copyFile(options.outputdir, entry)
				

if __name__ == "__main__":
	options = Options(sys.argv)
	main(options)