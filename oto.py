#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import sys
from benrifunctions import *
from traceback import print_exc
from mutagen.id3 import ID3, COMM, APIC, GRP1, MCDI, MVIN, MVNM, PCNT, PCST, SEEK, SYTC, TALB, TBPM, TCAT, TCMP, TCOM, TCON, TCOP, TDAT, TDEN, TDES, TDLY, TDOR, TDRC, TDRL, TDTG, TENC, TEXT, TFLT, TGID, TIME, TIT1, TIT2, TIT3, TKEY, TKWD, TLAN, TLEN, TMED, TMOO, TOAL, TOFN, TOLY, TOPE, TORY, TOWN, TPE1, TPE2, TPE3, TPE4, TPOS, TPRO, TPUB, TRCK, TRDA, TRSN, TRSO, TSIZ, TSO2, TSOA, TSOC, TSOP, TSOT, TSRC, TSSE, TSST, TXXX, TYER, USER, USLT, WCOM, WCOP, WFED, WOAF, WOAR, WOAS, WORS, WPAY, WPUB, WXXX, TMCL
from mutagen.asf import ASF
from mutagen.wave import WAVE
from mutagen.mp4 import MP4, MP4Cover
from mutagen.easymp4 import EasyMP4

from mutagen.flac import FLAC, Picture
import decrypt_163key

import binascii

#can I have a denylist of what can't be written, even unfriendly-like?

#remove dupes when you can
#id3Frames=['TALB', 'TBPM', 'TCMP', 'TCOM', 'TCON', 'TCOP', 'TDRC', 'TENC', 'TEXT', 'TLEN', 'TMED', 'TMOO', 'TIT1', 'TIT2', 'TIT3', 'TPE1', 'TPE2', 'TPE3', 'TPE4', 'TPOS', 'TPUB', 'TRCK', 'TOLY', 'TSO2', 'TSOA', 'TSOC', 'TSOP', 'TSOT', 'TSRC', 'TSST', 'TLAN', 'WXXX', 'COMM', 'APIC', 'TSSE', 'MCDI', 'USLT', "TXXX", "WOAR", "TOPE", "WCOM", "WCOP", "WFED", "WOAF", "WOAR", "WOAS", "WORS", "WPAY", "WPUB"]
id3Frames=["APIC", "GRP1", "MCDI", "MVIN", "MVNM", "PCNT", "PCST" "RVAD", "SEEK", "SYTC", "TALB", "TBPM", "TCAT", "TCMP", "TCOM", "TCON", "TCOP", "TDAT", "TDEN", "TDES", "TDLY", "TDOR", "TDRC", "TDRL", "TDTG", "TENC", "TEXT", "TFLT", "TGID", "TIME", "TIT1", "TIT2", "TIT3", "TKEY", "TKWD", "TLAN", "TLEN", "TMED", "TMOO", "TOAL", "TOFN", "TOLY", "TOPE", "TORY", "TOWN", "TPE1", "TPE2", "TPE3", "TPE4", "TPOS", "TPRO", "TPUB", "TRCK", "TRDA", "TRSN", "TRSO", "TSIZ", "TSO2", "TSOA", "TSOC", "TSOP", "TSOT", "TSRC", "TSSE", "TSST", "TXXX", "TYER", "USER", "USLT", "WCOM", "WCOP", "WFED", "WOAF", "WOAR", "WOAS", "WORS", "WPAY", "WPUB", "WXXX", "COMM", "TMCL"]
urlFrames=["WCOM", "WCOP", "WFED", "WOAF", "WOAR", "WOAS", "WORS", "WPAY", "WPUB", "WXXX"]
def id3FrameMaker(key, newText):
	#class mutagen.id3.POPM(email='', rating=0)
	#if the newText is email@mail.com|001, that pattern is simple enough to regex or stringsplit, since only certain characters are allowed in each
	
#	if key in id3Frames:
	try:
		frame=getattr(sys.modules["mutagen.id3"], key)
		if key=='MCDI' or key=='SYTC':
			try:
				#frame=MCDI(data=bytes.fromhex(newText))
				frame=frame(data=bytes.fromhex(newText))
			except:
				return None
		elif key in urlFrames:
			frame=frame(url=newText)
			if key=="WXXX":
				frame.desc=newText
		elif key=='USLT':
			frame=frame(text=newtext, encoding=1, lang="eng", desc=u"")
		elif key=='PCNT':
			try:
				frame=frame(count=int(newText))
			except:
				return None
		elif key=='PCST':
			try:
				frame=frame(value=int(newText))
			except:
				return None
		elif key=='SEEK':
			try:
				frame=frame(offset=int(newText))
			except:
				return None
		else:
			#frame=frame.__init__(frame, text=[newText])
			frame=frame(text=[newText])

		#print(key+" "+newText)
		return frame
	except:
		print_exc()
		return None

class EasySong:
	songpath=""
	extension=""
	easyToRawTable={'comments': 'COMM',
			'album': 'TALB',
			'bpm': 'TBPM',
			'compilation': 'TCMP',
			'composer': 'TCOM',
			'copyright': 'TCOP',
			'date': 'TDRC',
			'encodedby': 'TENC',
			'encodersettings': 'TSSE',
			'genre': 'TCON',
			'lyricist': 'TEXT',
			'length': 'TLEN',
			'media': 'TMED',
			'mood': 'TMOO',
			'grouping': 'TIT1',
			'title': 'TIT2',
			'version': 'TIT3',
			'artist': 'TPE1',
			'albumartist': 'TPE2',
			'conductor': 'TPE3',
			'arranger': 'TPE4',
			'discnumber': 'TPOS',
			'organization': 'TPUB',
			'tracknumber': 'TRCK',
			'author': 'TOLY',
			'albumartistsort': 'TSO2',
			'albumsort': 'TSOA',
			'composersort': 'TSOC',
			'artistsort': 'TSOP',
			'titlesort': 'TSOT',
			'isrc': 'TSRC',
			'discsubtitle': 'TSST',
			'language': 'TLAN',
			'website': 'WXXX',
			'cdinfo': 'MCDI',
			'lyrics': 'USLT'}
	rawToEasyTable={"COMM":"comments",
			"TALB": "album",
			"TBPM": "bpm",
			"TCMP": "compilation",
			"TCOM": "composer",
			"TCOP": "copyright",
			"TDRC": "date",
			"TENC": "encodedby",
			"TSSE": "encodersettings",
			"TCON": "genre",
			"TEXT": "lyricist",
			"TLEN": "length",
			"TMED": "media",
			"TMOO": "mood",
			"TIT1": "grouping",
			"TIT2": "title",
			"TIT3": "version",
			"TPE1": "artist",
			"TPE2": "albumartist",
			"TPE3": "conductor",
			"TPE4": "arranger",
			"TPOS": "discnumber",
			"TPUB": "organization",
			"TRCK": "tracknumber",
			"TOLY": "author",
			"TSO2": "albumartistsort",
			"TSOA": "albumsort",
			"TSOC": "composersort",
			"TSOP": "artistsort",
			"TSOT": "titlesort",
			"TSRC": "isrc",
			"TSST": "discsubtitle",
			"TLAN": "language",
			"WXXX": "website",
			"MCDI": "cdinfo",
			"USLT": "lyrics"}
	#you read, or you delete, but you can't easily write!
	crankyTags=["WOAR", "PRIV", "GEOB", "RVA2", "WCOP", "WOAF", "WOAS", "PCNT", "POPM", "WPUB", "TIPL", "PRIV", "USER", "PCST", "TMCL", "UFID"]
	rawTag=None
	def __init__(self, songpath=""):
		self.songpath=songpath
		self.extension=os.path.splitext(self.songpath)[1].lower()
	def save(self, songpath):
		self.rawTag.save(songpath)
		if not self.songpath:
			self.songpath=songpath
	def saveMe(self):
		self.rawTag.save(self.songpath)
	def __setitem__(self, key, value):
		if key in self.easyToRawTable:
			self.removeMatchingRaw(self.easyToRawTable[key])
			if value:
				frame=id3FrameMaker(self.easyToRawTable[key], str(value))
				if frame:
					self.rawTag[self.easyToRawTable[key]]=frame
					self.saveMe()
		elif key in self.rawToEasyTable:
			self.removeMatchingRaw(key)
			if value:
				frame=id3FrameMaker(key, str(value))
				if frame:
					self.rawTag[key]=frame
					self.saveMe()
	def __getitem__(self, key):
		if key in self.easyToRawTable:
			if self.easyToRawTable[key] in self.rawTag.keys():
				if key=="website":
					return [self.rawTag[self.easyToRawTable[key]].url]
				elif key=="cdinfo":
					#print("MCDI is "+self.rawTag[self.easyToRawTable[key]].data.decode())
					#print(binascii.hexlify(self.rawTag[self.easyToRawTable[key]].data))
					return [binascii.hexlify(self.rawTag[self.easyToRawTable[key]].data)]
				else:
					return [listToStringSemicolon(self.rawTag[self.easyToRawTable[key]])]
			else:
				for targetKey in self.rawTag.keys():
					targetKeyTest=targetKey
					if ":" in targetKeyTest:
						targetKeyTest=targetKey.split(":")[0]
					if self.easyToRawTable[key]==targetKeyTest:
						if targetKeyTest=="WXXX":
							return [self.rawTag[targetKey].url.strip()]
						elif targetKeyTest=="MCDI":
							#print(binascii.hexlify(self.rawTag[targetKey].data))
							return [binascii.hexlify(self.rawTag[targetKey].data)]
						else:
							return [listToStringSemicolon(str(self.rawTag[targetKey]))]
				else:
					return ""
		elif key in self.rawToEasyTable:
			if key=="WXXX" or key=="COMM" or key=="MCDI":
				for targetKey in self.rawTag.keys():
					targetKeyTest=targetKey
					if ":" in targetKeyTest:
						targetKeyTest=targetKey.split(":")[0]
					if key==targetKeyTest:
						if targetKeyTest=="WXXX":
							return [self.rawTag[targetKey].url]
						elif targetKeyTest=="MCDI":
							#print(binascii.hexlify(self.rawTag[targetKey].data))
							return [binascii.hexlify(self.rawTag[targetKey].data)]
						else:
							return [listToStringSemicolon(self.rawTag[targetKey])]
			else:
				if key in self.rawTag.keys():
					return [listToStringSemicolon(self.rawTag[key])]
				else:
					return ""
		else:			
			return ""
	def __delitem__(self, key):
		if self.easyToRawTable[key] in self.rawTag:
			del self.rawTag[self.easyToRawTable[key]]
		elif key in self.rawTag:
			del self.rawTag[key]
	def __missing__(self, key):
		return ""
	def __contains__(self, key):
		if ":" in key:
			print(key+" has as colon")
			key=key.split(":")[0]
		if key in self.easyToRawTable:
			#print(self.easyToRawTable[key]+" a ways away "+str(self.keys()))
			if key in self.keys() or (self.extension==".mp3" and len(self.rawTag.getall(self.easyToRawTable[key]))):
				return True
			else:
				return False
		elif key in self.rawToEasyTable or (self.extension==".mp3" and len(self.rawTag.getall(key))):
			if key in self.rawTag.keys():
				return True
			else:
				return False
		else:
			return False
	def keys(self):
		friendlyKeys=[]
		for key in self.rawTag.keys():
			friendlyKey=key
			if ":" in key:
				friendlyKey=key.split(":")[0]
			if self.rawTag[key]:
				if key in self.rawToEasyTable:
					friendlyKeys.append(self.rawToEasyTable[key])
				else:
					if friendlyKey in self.rawToEasyTable:
						friendlyKeys.append(self.rawToEasyTable[friendlyKey])
		return friendlyKeys
	def keysRaw(self):
		friendlyKeys=[]
		for key in self.rawTag.keys():			
			friendlyKey=key
			if ":" in friendlyKey:
				friendlyKey=friendlyKey.split(":")[0]
			friendlyKeys.append(friendlyKey)
		return self.rawTag.keys()
	def removeMatchingRaw(self, key):
		toDelete=[]
		for targetKey in self.rawTag.keys():
			targetKeyTest=targetKey
			if ":" in targetKeyTest:
				targetKeyTest=targetKey.split(":")[0]
			if key==targetKeyTest:
				toDelete.append(targetKey)
		if len(toDelete):
			for i in toDelete:
				del self.rawTag[i]
	def removeWebsites(self):
		toDelete=[]
		for targetKey in self.rawTag.keys():
			targetKeyTest=targetKey
			if ":" in targetKeyTest:
				targetKeyTest=targetKey.split(":")[0]
			if "WXXX"==targetKeyTest:
				toDelete.append(targetKey)
		if len(toDelete):
			for i in toDelete:
				del self.rawTag[i]
	def removeComments(self):
		toDelete=[]
		for targetKey in self.rawTag.keys():
			targetKeyTest=targetKey
			if ":" in targetKeyTest:
				targetKeyTest=targetKey.split(":")[0]
			if "COMM"==targetKeyTest:
				toDelete.append(targetKey)
		if len(toDelete):
			for i in toDelete:
				del self.rawTag[i]
	def unfriendlyKeys(self):
		unfriendlyKeys=[]
		for key in self.rawTag.keys():
			friendlierKey=key
			if ":" in key:
				friendlierKey=key.split(":")[0]
			if friendlierKey not in self.rawToEasyTable and friendlierKey not in self.easyToRawTable and friendlierKey!="APIC":
				#print(key)
				unfriendlyKeys.append(key)
		return unfriendlyKeys
	def getUnfriendly(self, key):
		if key in self.rawTag:
			for crankyTag in self.crankyTags:
				if key.startswith(crankyTag):
					return [listToStringSemicolon(self.rawTag[key].pprint()[5:])]
			try:
				return [listToStringSemicolon(self.rawTag[key])]
			except:
				return [listToStringSemicolon(self.rawTag[key].pprint()[5:])]
		else:
			return None
	def removeUnfriendly(self, key):
		if key in self.rawTag:
			del self.rawTag[key]
			self.saveMe()
	def setUnfriendly(self, key, value):
		if key in self.rawTag:
			del self.rawTag[key]
			self.saveMe()
		if value:
			setupKey=key
			extra=""
			if ":" in setupKey:
				setupKey, extra=setupKey.split(":", 1)
			try:
				frame=id3FrameMaker(setupKey, str(value))
				if frame:
					if extra:
						frame.desc=extra
					self.rawTag[key]=frame
					self.saveMe()
			except:
				print_exc()

class WAV(EasySong):
	rawTag=WAVE()
	def __init__(self, songpath=""):
		super().__init__(songpath)
		if self.songpath:
			self.rawTag=WAVE(self.songpath)

class WMedia(EasySong):
	rawToEasyTable={"Artist":"artist",
"WM/AlbumArtist":"albumartist",
"WM/TrackNumber":"tracknumber",
"WM/Year":"date",
"Title":"title",
"WM/AlbumTitle":"album",
"WM/Genre":"genre",
"WM/Composer":"composer",
"WM/Conductor":"conductor",
"WM/BeatsPerMinute":"bpm",
"Copyright":"copyright",
"WM/Lyrics": "lyrics"}
	easyToRawTable={"artist":"Artist",
"albumartist":"WM/AlbumArtist",
"tracknumber":"WM/TrackNumber",
"date":"WM/Year",
"title":"Title",
"album":"WM/AlbumTitle",
"genre":"WM/Genre",
"composer":"WM/Composer",
"conductor":"WM/Conductor",
"bpm":"WM/BeatsPerMinute",
"copyright":"Copyright",
"lyrics":"WM/Lyrics"}

	rawTag=ASF()
	def __init__(self, songpath=""):
		super().__init__(songpath)
		if self.songpath:
			self.rawTag=ASF(self.songpath)
	def __setitem__(self, key, value):
		key=str(key)
		if key in self.easyToRawTable:
			self.removeMatchingRaw(self.easyToRawTable[key])
			if value:
				self.rawTag[self.easyToRawTable[key]]=value
		elif key in self.rawToEasyTable:
			self.removeMatchingRaw(key)
			if value:
				self.rawTag[key]=value
		if key in self.easyToRawTable and self.easyToRawTable[key]=="WM/TrackNumber":
			self.rawTag["WM/Track"]=str(int(value)-1)
		self.saveMe()
class EasierMP3(EasySong):
	songpath=""
	rawTag=ID3()
	def __init__(self, songpath=""):
		super().__init__(songpath)
		if self.songpath:
			#print(self.songpath)
			self.rawTag=ID3(self.songpath)
			#print("I'm an EasierMP3! "+self.rawTag)
#			print("I'm an EasierMP3! "+self.rawTag.pprint())
			#print("I'm an EasierMP3! "+str(list(self.rawTag.keys())))
	def __getitem__(self, key):
		key=str(key)
		if key.startswith("WXXX"):
			key="WXXX"
		if key.startswith("USLT"):
			key="USLT"
		if key=="COMM" or key=="comments":
			return self.readComments()
		elif key=="WXXX" or key=="website":
			return self.readWebsite()
		elif key=="USLT" or key=="lyrics":
			return self.readLyrics()
		else:
			return super().__getitem__(key)
	def __setitem__(self, key, value):
		key=str(key)
		if key.startswith("WXXX") or key=="website":
			self.writeWebsite(value)
		elif key=="COMM" or key=="comments":
			self.writeComments(value)
		elif key=="USLT" or key=="lyrics":
			self.writeLyrics(value)
		else:
			super().__setitem__(key, value)
	def __delitem__(self, key):
		key=str(key)
		if key.startswith("WXXX"):
			key="WXXX"
		if key.startswith("USLT"):
			key="USLT"
		if key=="WXXX" or key=="website":
			self.rawTag.delall("WXXX")
		elif key=="COMM" or key=="comments":
			self.rawTag.delall("COMM")
		elif key=="USLT" or key=="lyrics":
			self.writeLyrics("")
		else:
			super().__delitem__(key)
	def readComments(self):
		finalComment=""
		commentResults=self.rawTag.getall("COMM")
		if commentResults:
			id3v1tag=""
			for comment in commentResults:
				foundV1=False
				if comment.desc:
					if comment.desc in ["ID3v1 Comment", "ID3v1", "ID3 v1 Comment"] and len(comment.text):
						foundV1=True
						for subcomment in comment.text:
							id3v1tag+=subcomment.strip()+"\n"
					else:
						if comment.desc.strip()!="Comment":
							finalComment+=comment.desc.strip()+": "
				if len(comment.text) and not foundV1:
					for subcomment in comment.text:
						finalComment+=subcomment.strip()+"\n"
			if id3v1tag.strip() not in finalComment.strip():
				finalComment+=id3v1tag.strip()
			return [decrypt_163key.main(finalComment.strip())]
		return ""
	def writeComments(self, value):
		if value:
			#print("Value is "+value)
			self.rawTag.setall("COMM", [COMM(text=[value])])
		else:
			self.rawTag.delall("COMM")
		try:
			self.rawTag.save()
		except:
			print_exc()
	def readWebsite(self):
		finalSites=""
		wxxxResults=self.rawTag.getall("WXXX")
		if wxxxResults:
			for wxxx in wxxxResults:
				if wxxx.url:
					finalSites+=wxxx.url.strip()+"\n"
			return [finalSites.strip()]
		return None

	def writeWebsite(self, value):
		self.rawTag.delall("WXXX")
		if value:
			#print("Value is "+value)
			self.rawTag.setall("WXXX", [WXXX(url=value)])			
		try:
			self.rawTag.save()
		except:
			print_exc()

	def readLyrics(self):
		finalContent=""
		results=self.rawTag.getall("USLT")
		if results:
			for result in results:
				finalContent+=result.text+"\n"
			#print(finalContent)
			return [finalContent.strip()]
		return None

	def writeLyrics(self, value):
		if value:
			self.rawTag.setall("USLT", [USLT(text=value, encoding=1, lang="eng", desc=u"")])
		else:
			self.rawTag.delall("USLT")
		try:
			self.rawTag.save()
		except:
			print_exc()

class M4A(EasySong):
	rawTag=MP4()
	easyToRawTable={"title":'©nam',
	"album":'©alb',
	"artist":'©ART',
	"albumartist":'aART',
	"date":'©day',
	"comment":'©cmt',
	"description":b'desc',
	"grouping":'©grp',
	"genre":'©gen',
	"copyright":'cprt',
	"albumsort":'soal',
	"albumartistsort":'soaa',
	"artistsort":'soar',
	"titlesort":'sonm',
	"composersort":'soco',
	"musicbrainz_artistid":"MusicBrainz Artist Id",
	"musicbrainz_trackid":"MusicBrainz Track Id",
	"musicbrainz_albumid":"MusicBrainz Album Id",
	"musicbrainz_albumartistid":"MusicBrainz Album Artist Id",
	"musicip_puid":"MusicIP PUID",
	"musicbrainz_albumstatus":"MusicBrainz Album Status",
	"musicbrainz_albumtype":"MusicBrainz Album Type",
	"releasecountry":"MusicBrainz Release Country",
	"bpm":'tmpo',
	"composer":'wrt',
	"tracknumber":'trkn',
	"discnumber":'disk'}
	rawToEasyTable={'©nam': 'title',
	'©alb': 'album',
	'©ART': 'artist',
	'aART': 'albumartist',
	'©day': 'date',
	'©cmt': 'comment',
	'desc': 'description',
	'©grp': 'grouping',
	'©gen': 'genre',
	'cprt': 'copyright',
	'soal': 'albumsort',
	'soaa': 'albumartistsort',
	'soar': 'artistsort',
	'sonm': 'titlesort',
	'soco': 'composersort',
	'MusicBrainz Artist Id': 'musicbrainz_artistid',
	'MusicBrainz Track Id': 'musicbrainz_trackid',
	'MusicBrainz Album Id': 'musicbrainz_albumid',
	'MusicBrainz Album Artist Id': 'musicbrainz_albumartistid',
	'MusicIP PUID': 'musicip_puid',
	'MusicBrainz Album Status': 'musicbrainz_albumstatus',
	'MusicBrainz Album Type': 'musicbrainz_albumtype',
	'MusicBrainz Release Country': 'releasecountry',
	"tmpo": "bpm",
	"wrt": "composer",
	"trkn": "tracknumber",
	"disk": "discnumber"}
	def __init__(self, songpath=""):
		super().__init__(songpath)
		if self.songpath:
			self.rawTag=MP4(self.songpath)
			#print(self.rawTag)
	def __getitem__(self, key):
		key=str(key)
		if key=="trkn" or key=="disk" or key=="tracknumber" or key=="discnumber":
			niceResult=listToStringSemicolon(super().__getitem__(key))
			if key.startswith("dis") or key.startswith("tr"):
				niceResult=str(niceResult).replace("(", "").replace(")", "").replace(", ", "/")
			return niceResult
		else:
			return super().__getitem__(key)

class EasyArt:
	art=None
	artType=3
	mime=None
	filename="cover"
	artTypeDict={3:"Cover",
	4:"Back",
	5:"Leaflet",
	0:"Other Art",
	1:"File Icon",
	2:"Other File Icon",
	6:"Media",
	7:"Lead Artist",
	8:"Artist",
	9:"Conductor",
	10:"Band",
	11:"Composer",
	12:"Lyricist",
	13:"Recording Location",
	14:"During Recording",
	15:"During Performance",
	16:"Screen Capture",
	17:"Fish",
	18:"Illustration",
	19:"Band Logotype",
	20:"Publisher Logotype"}
	friendlyArtTypeDict={3:"Album Art",
	4:"Back",
	5:"Leaflet",
	0:"Other Art",
	1:"File Icon",
	2:"Other File Icon",
	6:"Media",
	7:"Lead Artist",
	8:"Artist",
	9:"Conductor",
	10:"Band",
	11:"Composer",
	12:"Lyricist",
	13:"Recording Location",
	14:"During Recording",
	15:"During Performance",
	16:"Screen Capture",
	17:"Fish",
	18:"Illustration",
	19:"Band Logotype",
	20:"Publisher Logotype"}
	def __init__(self, tag=None):
		if type(tag)==APIC:
			self.art=tag.data
			self.artType=tag.type
			if tag.mime:
				self.mime=tag.mime
		elif type(tag)==Picture:
			self.art=tag.data
			self.artType=tag.type
			if tag.mime:
				self.mime=tag.mime
		elif type(tag)==MP4Cover:
			if hasattr(tag, "MP4Cover.FORMAT_PNG") or hasattr(tag, "FORMAT_PNG"):
				self.mime="image/png"
			elif hasattr(tag, "MP4Cover.FORMAT_JPEG") or hasattr(tag, "FORMAT_JPEG"):
				self.mime="image/jpeg"
			elif hasattr(tag, "data") and tag.data.startswith(b'\x89PNG'):
				self.mime="image/png"
			self.art=tag
		#self.filename=filename
		if self.art!=None and type(self.art)==str:
			self.art=bytes(self.art, "utf-8")
	def fromFileData(self, art, mime, artType=3):
		self.art=art
		if type(self.art)==str:
			self.art=bytes(self.art, "utf-8")
		self.mime=mime
		self.artType=artType
		
	def fromFile(self, art, mime, artType, filename):
		self.art=art
		if type(self.art)==str:
			self.art=bytes(self.art, "utf-8")
		self.mime=mime
		self.artType=artType
		self.filename=filename
	def getId3Key(self):
		return "APIC:"+self.artTypeDict[self.artType]
	def getArtTypeFriendly(self):
		if self.artType in self.friendlyArtTypeDict:
			return self.friendlyArtTypeDict[self.artType]
		else:
			return "Album Art"
	def toId3Art(self):
		image=APIC(
			encoding=3, # 3 is for utf-8
			type=self.artType,
			desc=self.artTypeDict[self.artType],
			data=self.art
		)
		if self.mime:
			image.mime=self.mime
		return image
	def toVorbisArt(self):
		image=Picture()
		image.desc=self.artTypeDict[self.artType]
		image.data=self.art
		image.type=self.artType
		if self.mime:
			image.mime=self.mime
		return image
	def toMp4Art(self):
		if self.mime=="image/png":
			return MP4Cover(self.art, MP4Cover.FORMAT_PNG)
		elif self.mime=="image/jpeg":
			return MP4Cover(self.art, MP4Cover.FORMAT_PNG)
		else:
			return None

	def rename(self, newName):
		self.filename=newName

	def saveFile(self):
		if self.art and self.mime:
			extension=self.mime.split("/")[1]
			if extension=="jpeg":
				extension="jpg"
			artFile=open(self.filename+" ("+self.getArtTypeFriendly()+")."+extension, "wb")
			artFile.write(self.art)
			artFile.close()

	def saveFile(self, saveName):
		if self.art and self.mime:
			extension=self.mime.split("/")[1]
			if extension=="jpeg":
				extension="jpg"
			artFile=open(saveName+" ("+self.getArtTypeFriendly()+")."+extension, "wb")
			artFile.write(self.art)
			artFile.close()

	def saveTo(self, location):
		#print("self.mime is "+self.mime)
		if self.art and self.mime:
			extension=self.mime.split("/")[1]
			if extension=="jpeg":
				extension="jpg"
			artFile=open(os.path.join(location, self.filename+" ("+self.getArtTypeFriendly()+")."+extension), "wb")
			artFile.write(self.art)
			artFile.close()

	def saveTo(self, location, saveName):
		#print("self.mime is "+self.mime)
		if self.art and self.mime:
			extension=self.mime.split("/")[1]
			if extension=="jpeg":
				extension="jpg"
			artFile=open(os.path.join(location, saveName+" ("+self.getArtTypeFriendly()+")."+extension), "wb")
			artFile.write(self.art)
			artFile.close()
