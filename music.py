
class MusicFile:
	def __init__(self, filepath, filename, filetype):
		self.filepath = filepath
		self.filename = filename
		self.filetype = filetype

	def __str__(self):
		attrs = vars(self)
		return '\n'.join("%s: %s" % item for item in attrs.items())

	def setLossyEncoding(self, bitrate_mode, bitrate):
		self.bitrate_mode = bitrate_mode
		self.bitrate = bitrate
		self.bits_per_sample = None
		self.sample_rate = None

	def setLosslessEncoding(self, bits_per_sample, sample_rate):
		self.bitrate_mode = None
		self.bitrate = None
		self.bits_per_sample = bits_per_sample
		self.sample_rate = sample_rate

	def getArtist(self):
		return self.albumartist if self.albumartist else self.artist

class MusicDisc:
	def __init__(self, disc):
		self.disc
		self.tracks = []

	def addTrack(self, track):
		self.append(track)

class MusicTrack:
	def __init__(self, disc, track, title):
		self.disc = disc
		self.track = track
		self.title = title

class MusicAlbum:
	def __init__(self, conn, albumartist, album):
		self.albumartist = albumartist
		self.album = album
		self.discs = []
		files = conn.execute("""
			SELECT 
				filepath, filename, filetype,
				bitrate_mode, bitrate, bits_per_sample, sample_rate, 
				artist, title, track, totaltrack, disc, totaldisc, releasedate
			FROM music WHERE albumartist=? AND album=?;
			""", (albumartist, album)).fetchall()
		for file in files:
			disc = file[11]
			if not self.discs[disc]:
				self.discs[disc] = []
			musicDisc = self.discs[disc]
			track = file[9]
			musicDisc[track] = MusicTrack(disc, track, title)


	def addDisc(disc, tracks):
		self.discs[disc] = tracks

	def addTrack(disc, track, title):
		self.discs[disc].tracks[track] = MusicTrack(title)
