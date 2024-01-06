#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4, EasyMP4Tags
from traceback import print_exc
from mutagen.id3 import ID3, COMM, APIC
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from oto import *
from io import BytesIO
import wx
import re
import os
import sys
import glob
from benrifunctions import *

#mp4Missing=["composer", "conductor", "encodedby", "version", "organization",
#mp4Missing=["conductor", "encodedby", "version", "organization", "website", "isrc"]
EasyMP4Tags.RegisterTextKey("composer", "©wrt")
EasyMP4Tags.RegisterTextKey("encodedby", "©too")
EasyMP4Tags.RegisterTextKey("lyrics", "©lyr")
#you sure about isrc?
#mp4Missing=["conductor", "version", "organization", "website", "isrc", "encodersettings", "cdinfo", "length", "lyrics"]
mp4Missing=["conductor", "version", "organization", "website", "isrc", "encodersettings", "cdinfo", "length"]
mp4Raw=['©nam', '©alb', '©ART', 'aART', '©day', '©cmt', 'desc', '©grp', '©gen', 'cprt', 'soal', 'soaa', 'soar', 'sonm', 'soco', 'MusicBrainz Artist Id', 'MusicBrainz Track Id', 'MusicBrainz Album Id', 'MusicBrainz Album Artist Id', 'MusicIP PUID', 'MusicBrainz Album Status', 'MusicBrainz Album Type', 'MusicBrainz Release Country', "tmpo", "wrt", "trkn", "disk", "©wrt", "©lyr", "©too"]

#whenever possible, refer to something by its plain English name?
mp4RawDict={'desc': 'description', 'purd': 'purchase date', '©grp': 'grouping', 'purl': 'podcast URL', 'egid': 'podcast episode GUID', 'catg': 'podcast category', 'keyw': 'podcast keywords', 'soal': 'album sort order', 'soaa': 'album artist sort order', 'soar': 'artist sort order', 'sonm': 'title sort order', 'soco': 'composer sort order', 'sosn': 'show sort order', 'tvsh': 'show name', '©wrk': 'work', '©mvn': 'movement', 'cpil': 'part of a compilation', 'pgap': 'part of a gapless album', 'pcst': 'podcast', '©mvc': 'Movement Count', '©mvi': 'Movement Index', 'shwm': 'work/movement', 'stik': 'Media Kind', 'hdvd': 'HD Video', 'rtng': 'Content Rating', 'tves': 'TV Episode', 'tvsn': 'TV Season', 'plID': 'plID', 'cnID': 'cnID', 'geID': 'geID', 'atID': 'atID', 'sfID': 'Apple Store ID', 'cmID': 'cmID', 'akID': 'akID', 'apID': 'Apple ID Email', 'ownr': 'Apple ID Name', 'pinf': 'pinf'}

#for i in range(0, len(mp4RawUnfriendly)):
#	EasyMP4Tags.RegisterTextKey(mp4Unfriendly[i], mp4RawUnfriendly[i])

mp3Only=["cdinfo", "length"]

standardTags=["artist", "albumartist", "tracknumber",
"discnumber", "date", "title", "album", "genre",
"composer", "conductor", "encodedby", "encodersettings",
"bpm", "organization", "website",
"copyright", "isrc", "version",
"cdinfo", "length",
"comments", "lyrics"]

def getVorbisUnfriendlyTags(songtag):
	unfriendly={}
	for key in songtag.keys():
		if key not in standardTags and key.lower()!="coverart" and key.lower()!="metadata_block_picture" and key.lower()!="comment":
			unfriendly[key]=songtag[key]
	return unfriendly
	
def getMP4UnfriendlyTags(songtag):
	unfriendly={}
	theMp4=MP4(songtag.filename)
	for key in theMp4.keys():
		if key not in mp4Raw and key.lower()!="covr":
			unfriendly[key]=theMp4[key]
	return unfriendly

def getUnfriendlyTags(songtag):
	#do I want to take an EasyMP4 and make an MP4 really quick?
	#then I'd need a separate list of friendly and unfriendly
	unfriendly={}
	if type(songtag)==EasierMP3 or type(songtag)==WAV:
		for key in songtag.keys():
			if key not in standardTags:
				unfriendly[key]=songtag[key]
	elif type(songtag)==EasyMP4:
		unfriendly=getMP4UnfriendlyTags(songtag)
	elif type(songtag)==OggVorbis or type(songtag)==FLAC:
		unfriendly=getVorbisUnfriendlyTags(songtag)
#		for key in mp4Unfriendly:
#			if key in songtag:
#				unfriendly[key]=str(songtag[key])
	return unfriendly
	
imagesWildcard = "jpg (*.jpg)|*.jpg;*.JPG;*.jpeg;*.JPEG;*.jpe;*.JPE|png (*.png)|*.png;*.PNG"

artTypeDict={3:"Album Art",
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
reverseArtTypeDict={'Album Art':3,
'Back':4,
'Leaflet':5,
'Other Art':0,
'File Icon':1,
'Other File Icon':2,
'Media':6,
'Lead Artist':7,
'Artist':8,
'Conductor':9,
'Band':10,
'Composer':11,
'Lyricist':12,
'Recording Location':13,
'During Recording':14,
'During Performance':15,
'Screen Capture':16,
'Fish':17,
'Illustration':18,
'Band Logotype':19,
'Publisher Logotype':20}

apicarttypedict={3:"Cover",
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

def makeintoafilename(thetext):
	return thetext.replace("?", "").replace("/", "-").replace(":", "-")

def picTypeGetter(pic):
	if hasattr(pic, "mime") and len(pic.mime):
		return pic.mime
	elif hasattr(pic, "FORMAT_JPEG") or hasattr(pic, "FORMAT_PNG"):
		if hasattr(pic, "FORMAT_JPEG") and "PNG" not in str(pic):
			 return "image/jpeg"
		elif hasattr(pic, "FORMAT_PNG") and "PNG" in str(pic):
			return "image/png"
	elif hasattr(pic, "data") and pic.data.startswith(b'\x89PNG'):
		return "image/png"

def getAlbumFromFilename(song):
	songid3data=None
	extension=os.path.splitext(song)[1].lower()
	if extension.lower()==".mp3":
		try:
			songid3data = EasyID3(song)
		except:
			return None
	elif extension.lower()==".ogg":
		try:
			songid3data=OggVorbis(song)
		except:
			return None
	elif extension.lower()==".flac":
		try:
			songid3data=FLAC(song)
		except:
			return None
	elif extension.lower()==".mp4" or extension.lower()==".m4a":
		try:
			songid3data=EasyMP4(song)
		except:
			return None

	elif extension.lower()==".wav":
		try:
			songid3data=WAVE(song)
		except:
			return None	
	if songid3data:
		fileNameToBe=""
		if "album" in songid3data:
			if type(songid3data["album"])==list:
				fileNameToBe=songid3data["album"][0].strip()
			else:
				fileNameToBe=songid3data["album"].strip()
		elif "TALB" in songid3data:
			fileNameToBe=songid3data["TALB"].text[0].strip()
		return makeintoafilename(fileNameToBe)
	else:
		return ""


currentdirectory=os.getcwd()#sys.path[0]

wildcard = "mp3 (*.mp3)|*.mp3;*.MP3|ogg (*.ogg)|*.ogg;*.OGG|flac (*.flac)|*.flac;*.FLAC|mp4, m4a (*.mp4, *.m4a)|*.mp4;*.MP4;*.m4a;*.M4A|ASF (*.asf, *.wma, *.wmv)|*.asf;*.ASF;*.wma;*.WMA;*.wmv;*.WMV|WAV (*.wav)|*.wav;*.WAV"

class TheWindow(wx.Panel):
	def __init__(self, parent, id):
	#create the panel
		wx.Panel.__init__(self, parent, id)
		self.loadedSongsList=[]
		self.deletiondict={}
		self.tempalbumartstorage=[]
		self.tempalbumartfilenamestorage=[]
		self.tempalbumartmimestorage=[]
		self.opentag=-1

		self.currentarttype=3
		self.wouldbeartfilename=None

		self.bigsizer=wx.BoxSizer(wx.VERTICAL)
		self.sizertagspart = wx.BoxSizer(wx.VERTICAL)
		#self.sizertagspart = wx.BoxSizer(wx.HORIZONTAL)
		self.sizerbuttonsparttop = wx.BoxSizer(wx.HORIZONTAL)
		#self.loadedsizer = wx.BoxSizer(wx.VERTICAL)
		#do I HAVE to store the whole song path here? probably, even if it's stored elsewhere, distinguish
		self.loadedSongs=wx.ListBox(self, style=wx.LB_MULTIPLE|wx.LB_NEEDED_SB)#size=(250, 250)
		self.loadedSongs.Bind(wx.EVT_LISTBOX, self.onSelect)

		self.sizertagspart.Add(self.loadedSongs, 1, wx.EXPAND)
		#add the tags into their own sizer

		self.tagssizer = wx.BoxSizer(wx.VERTICAL)

		self.artistsizer = wx.BoxSizer(wx.HORIZONTAL)

		self.artistcard=wx.StaticText(self, label="Artist:")
		self.artistfield=wx.TextCtrl(self)
		self.artistcheck=wx.CheckBox(self, -1, "All")

		self.artistsizer.Add(self.artistcard, 0)
		self.artistsizer.Add(self.artistfield, 6)#how about horizontal expansion? add to the artist sizer? NO! The toppartsizer
		self.artistsizer.Add(self.artistcheck, 1)

		self.albumartistsizer = wx.BoxSizer(wx.HORIZONTAL)

		self.albumartistcard=wx.StaticText(self, label="Album Artist:")
		self.albumartistfield=wx.TextCtrl(self)
		self.albumartistcheck=wx.CheckBox(self, -1, "All")

		self.albumartistsizer.Add(self.albumartistcard, 0)
		self.albumartistsizer.Add(self.albumartistfield, 6)
		self.albumartistsizer.Add(self.albumartistcheck, 1)

		self.numberssizer = wx.BoxSizer(wx.HORIZONTAL)

		self.trackcard=wx.StaticText(self, label="Track:")
		self.trackfield=wx.TextCtrl(self)

		self.numberssizer.Add(self.trackcard, 1)
		self.numberssizer.Add(self.trackfield, 2)

		self.discnumbercard=wx.StaticText(self, label="Disc Number:")
		self.discnumberfield=wx.TextCtrl(self)
		self.discnumbercheck=wx.CheckBox(self, -1, "All")

		self.numberssizer.Add(self.discnumbercard, 0)
		self.numberssizer.Add(self.discnumberfield, 2)
		self.numberssizer.Add(self.discnumbercheck, 1)

		self.datecard=wx.StaticText(self, label="Date:")
		self.datefield=wx.TextCtrl(self)
		self.datecheck=wx.CheckBox(self, -1, "All")

		self.numberssizer.Add(self.datecard, 1)
		self.numberssizer.Add(self.datefield, 2)
		self.numberssizer.Add(self.datecheck, 1)

		self.titlesizer = wx.BoxSizer(wx.HORIZONTAL)

		self.titlecard=wx.StaticText(self, label="Title:")
		self.titlefield=wx.TextCtrl(self)

		self.titlesizer.Add(self.titlecard, 0)
		self.titlesizer.Add(self.titlefield, 6)

		self.albumsizer = wx.BoxSizer(wx.HORIZONTAL)

		self.albumcard=wx.StaticText(self, label="Album:")
		self.albumfield=wx.TextCtrl(self)
		self.albumcheck=wx.CheckBox(self, -1, "All")

		self.albumsizer.Add(self.albumcard, 0)
		self.albumsizer.Add(self.albumfield, 6)
		self.albumsizer.Add(self.albumcheck, 1)

		self.genreandcomposersizer = wx.BoxSizer(wx.HORIZONTAL)

		self.genrecard=wx.StaticText(self, label="Genre:")
		self.genrefield=wx.TextCtrl(self)
		self.genrecheck=wx.CheckBox(self, -1, "All")

		self.composercard=wx.StaticText(self, label="Composer:")
		self.composerfield=wx.TextCtrl(self)
		self.composercheck=wx.CheckBox(self, -1, "All")

		self.genreandcomposersizer.Add(self.genrecard, 1)
		self.genreandcomposersizer.Add(self.genrefield, 5)
		self.genreandcomposersizer.Add(self.genrecheck, 1)		
		self.genreandcomposersizer.Add(self.composercard, 1)
		self.genreandcomposersizer.Add(self.composerfield, 5)
		self.genreandcomposersizer.Add(self.composercheck, 1)

		self.conductorencodedbyencodersizer = wx.BoxSizer(wx.HORIZONTAL)

		self.conductorcard=wx.StaticText(self, label="Conductor:")
		self.conductorfield=wx.TextCtrl(self)
		self.conductorcheck=wx.CheckBox(self, -1, "All")

		self.encodedbycard=wx.StaticText(self, label="Encoded By:")
		self.encodedbyfield=wx.TextCtrl(self)
		self.encodedbycheck=wx.CheckBox(self, -1, "All")

		self.encodersettingscard=wx.StaticText(self, label="Encoder Settings:")
		self.encodersettingsfield=wx.TextCtrl(self)
		self.encodersettingscheck=wx.CheckBox(self, -1, "All")

		self.conductorencodedbyencodersizer.Add(self.conductorcard, 1)
		self.conductorencodedbyencodersizer.Add(self.conductorfield, 5)
		self.conductorencodedbyencodersizer.Add(self.conductorcheck, 1)
		self.conductorencodedbyencodersizer.Add(self.encodedbycard, 1)
		self.conductorencodedbyencodersizer.Add(self.encodedbyfield, 5)
		self.conductorencodedbyencodersizer.Add(self.encodedbycheck, 1)
		self.conductorencodedbyencodersizer.Add(self.encodersettingscard, 1)
		self.conductorencodedbyencodersizer.Add(self.encodersettingsfield, 5)
		self.conductorencodedbyencodersizer.Add(self.encodersettingscheck, 1)

		self.bpmorgwebsitesizer = wx.BoxSizer(wx.HORIZONTAL)

		self.bpmcard=wx.StaticText(self, label="BPM:")
		self.bpmfield=wx.TextCtrl(self)
		self.bpmcheck=wx.CheckBox(self, -1, "All")

		self.organizationcard=wx.StaticText(self, label="Organization:")
		self.organizationfield=wx.TextCtrl(self)
		self.organizationcheck=wx.CheckBox(self, -1, "All")

		self.websitecard=wx.StaticText(self, label="Website:")
		self.websitefield=wx.TextCtrl(self)
		self.websitecheck=wx.CheckBox(self, -1, "All")

		self.bpmorgwebsitesizer.Add(self.bpmcard, 0)
		self.bpmorgwebsitesizer.Add(self.bpmfield, 1)
		self.bpmorgwebsitesizer.Add(self.bpmcheck, 1)
		self.bpmorgwebsitesizer.Add(self.organizationcard, 1)
		self.bpmorgwebsitesizer.Add(self.organizationfield, 5)
		self.bpmorgwebsitesizer.Add(self.organizationcheck, 1)
		self.bpmorgwebsitesizer.Add(self.websitecard, 1)
		self.bpmorgwebsitesizer.Add(self.websitefield, 5)
		self.bpmorgwebsitesizer.Add(self.websitecheck, 1)

		self.copyrightisrcversionsizer = wx.BoxSizer(wx.HORIZONTAL)

		self.copyrightcard=wx.StaticText(self, label="Copyright:")
		self.copyrightfield=wx.TextCtrl(self)
		self.copyrightcheck=wx.CheckBox(self, -1, "All")

		self.isrccard=wx.StaticText(self, label="ISRC:")
		self.isrcfield=wx.TextCtrl(self)
		self.isrccheck=wx.CheckBox(self, -1, "All")

		self.versioncard=wx.StaticText(self, label="Version:")
		self.versionfield=wx.TextCtrl(self)
		self.versioncheck=wx.CheckBox(self, -1, "All")

		self.copyrightisrcversionsizer.Add(self.copyrightcard, 0)
		self.copyrightisrcversionsizer.Add(self.copyrightfield, 1)
		self.copyrightisrcversionsizer.Add(self.copyrightcheck, 1)
		self.copyrightisrcversionsizer.Add(self.isrccard, 0)
		self.copyrightisrcversionsizer.Add(self.isrcfield, 1)
		self.copyrightisrcversionsizer.Add(self.isrccheck, 1)
		self.copyrightisrcversionsizer.Add(self.versioncard, 0)
		self.copyrightisrcversionsizer.Add(self.versionfield, 1)
		self.copyrightisrcversionsizer.Add(self.versioncheck, 1)

		self.cdinfolengthsizer = wx.BoxSizer(wx.HORIZONTAL)

		self.cdinfocard=wx.StaticText(self, label="CD Info:")
		self.cdinfofield=wx.TextCtrl(self)
		self.cdinfocheck=wx.CheckBox(self, -1, "All")

		self.lengthcard=wx.StaticText(self, label="Length:")
		self.lengthfield=wx.TextCtrl(self)
		self.lengthcheck=wx.CheckBox(self, -1, "All")

		self.cdinfolengthsizer.Add(self.cdinfocard, 1)
		self.cdinfolengthsizer.Add(self.cdinfofield, 1)
		self.cdinfolengthsizer.Add(self.cdinfocheck, 1)

		self.cdinfolengthsizer.Add(self.lengthcard, 0)
		self.cdinfolengthsizer.Add(self.lengthfield, 1)
		self.cdinfolengthsizer.Add(self.lengthcheck, 1)

		
		self.commentssizer = wx.BoxSizer(wx.HORIZONTAL)

		self.commentscard=wx.StaticText(self, label="Comments:")
		self.commentsfield=wx.TextCtrl(self, style = wx.TE_MULTILINE)
		self.commentscheck=wx.CheckBox(self, -1, "All")

		self.commentssizer.Add(self.commentscard, 1)
		self.commentssizer.Add(self.commentsfield, 8, wx.EXPAND)
		self.commentssizer.Add(self.commentscheck, 1)

		self.tagssizer.Add(self.artistsizer, 1, wx.EXPAND)
		self.tagssizer.Add(self.albumartistsizer, 1, wx.EXPAND)
		self.tagssizer.Add(self.numberssizer, 1)
		self.tagssizer.Add(self.titlesizer, 1, wx.EXPAND)
		self.tagssizer.Add(self.albumsizer, 1, wx.EXPAND)
		self.tagssizer.Add(self.genreandcomposersizer, 1)
		self.tagssizer.Add(self.conductorencodedbyencodersizer, 1)
		self.tagssizer.Add(self.bpmorgwebsitesizer, 1)
		self.tagssizer.Add(self.copyrightisrcversionsizer, 1)
		self.tagssizer.Add(self.cdinfolengthsizer, 1)
		self.tagssizer.Add(self.commentssizer, 5, wx.EXPAND)

		self.sizertagspart.Add(self.tagssizer, 1, wx.RIGHT|wx.EXPAND)

		self.button1 = wx.Button(self, label="Select S&ongs")
		self.button1.Bind(wx.EVT_BUTTON, self.BringUpSong)

#gonna have to change the save functionality, maybe?
		self.button2 = wx.Button(self, label="&Save")
		self.button2.Bind(wx.EVT_BUTTON, self.SaveTheTags)

		self.button3 = wx.Button(self, label="&Remove Selected")
		self.button3.Bind(wx.EVT_BUTTON, self.RemoveSelectedSongs)

		self.button4 = wx.Button(self, label="&Clear")
		self.button4.Bind(wx.EVT_BUTTON, self.ClearTheSongs)

		self.button5 = wx.Button(self, label="Select Art")
		self.button5.Bind(wx.EVT_BUTTON, self.BringUpArt)

		self.button6 = wx.Button(self, label="Remove Art")
		self.button6.Bind(wx.EVT_BUTTON, self.RemoveArt)

		self.button7 = wx.Button(self, label="Export Art")
		self.button7.Bind(wx.EVT_BUTTON, self.ExportTheArt)

		self.button8 = wx.Button(self, label="Export All Art of This Song")
		self.button8.Bind(wx.EVT_BUTTON, self.ExportAllArtThisSong)

		self.button9 = wx.Button(self, label="Export Art of All Songs")
		self.button9.Bind(wx.EVT_BUTTON, self.ExportAllArt)
		

		self.button10 = wx.Button(self, label="View Art")
		self.button10.Bind(wx.EVT_BUTTON, self.ViewTheArt)

		self.button11 = wx.Button(self, label="Remove All Art")
		self.button11.Bind(wx.EVT_BUTTON, self.RemoveAllArt)

		self.button12 = wx.Button(self, label="Export Lyrics")
		self.button12.Bind(wx.EVT_BUTTON, self.SaveLyricsToText)

		self.button13 = wx.Button(self, label="Export All Art With Filenames")
		self.button13.Bind(wx.EVT_BUTTON, self.ExportAllArtWithFilenames)
		
		self.buttonquit = wx.Button(self, label="&Quit")
		self.buttonquit.Bind(wx.EVT_BUTTON, self.Quitter)

		menuBar = wx.MenuBar()

		artMenuBar = wx.Menu()
		self.artTypeMenu = wx.Menu()
		for arttype in sorted(artTypeDict.values()):
			artTypeMenuItem=wx.MenuItem(self.artTypeMenu, wx.ID_ANY, arttype, arttype, wx.ITEM_RADIO)
			self.artTypeMenu.Bind(wx.EVT_MENU, self.ReloadSongs(reverseArtTypeDict[arttype]), artTypeMenuItem)
			self.artTypeMenu.Append(artTypeMenuItem)
			if arttype=="Album Art":
				artTypeMenuItem.Check()
		artMenuBar.AppendSubMenu(self.artTypeMenu, "Art Type", "Art Type")

		timeDataMenuBar = wx.Menu()
		self.restoreTimeDataCheck=wx.MenuItem(timeDataMenuBar, wx.ID_ANY, "Save Time Data", "Save Time Data", wx.ITEM_CHECK)
		timeDataMenuBar.Append(self.restoreTimeDataCheck)

		menuBar.Append(artMenuBar, '&Options')
		menuBar.Append(timeDataMenuBar, '&Time Data')

		self.tagTricksMenu = wx.Menu()
		replaceStringInTags=self.tagTricksMenu.Append(wx.ID_EDIT, "Replace String in Tags")
		
		menuBar.Append(self.tagTricksMenu, 'T&ag Tricks')

		parent.SetMenuBar(menuBar)
		self.tagTricksMenu.Bind(wx.EVT_MENU, self.MenuHandle)
		#ready for the rest of the tags now, enough space

		self.sizerbuttonsparttop.Add(self.button1, 1)
		self.sizerbuttonsparttop.Add(self.button2, 1)
		self.sizerbuttonsparttop.Add(self.button3, 1)
		self.sizerbuttonsparttop.Add(self.button4, 1)

		self.sizerbuttonspartmiddle = wx.BoxSizer(wx.HORIZONTAL)

		self.sizerbuttonspartmiddle.Add(self.button5, 1)
		self.sizerbuttonspartmiddle.Add(self.button6, 1)
		self.sizerbuttonspartmiddle.Add(self.button7, 1)
		self.sizerbuttonspartmiddle.Add(self.button8, 1)
		self.sizerbuttonspartmiddle.Add(self.button9, 1)
		
		self.sizerbuttonspartbottom = wx.BoxSizer(wx.HORIZONTAL)
		
		self.sizerbuttonspartbottom.Add(self.button10, 1)
		self.sizerbuttonspartbottom.Add(self.button11, 1)
		self.sizerbuttonspartbottom.Add(self.button12, 1)
		self.sizerbuttonspartbottom.Add(self.button13, 1)
		self.sizerbuttonspartbottom.Add(self.buttonquit, 1)

		self.artandlyricssizer = wx.BoxSizer(wx.VERTICAL)

		self.artsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.theblank=wx.Image(200, 200, True)
		self.theblank.SetMaskColour(0,0,0)
		self.thepic=self.theblank.ConvertToBitmap()
		self.theart=wx.StaticBitmap(self, 1, self.theblank.ConvertToBitmap(), pos=wx.Point(0,0))
		self.artallcheck=wx.CheckBox(self, -1, "&All")
		self.artsizer.Add(self.theart, 5)
		self.artsizer.Add(self.artallcheck, 1)
		self.lyricscard=wx.StaticText(self, label="Lyrics:")
		self.lyricsfield= wx.TextCtrl(self, style = wx.TE_MULTILINE)
		self.unfriendlyTagsCard=wx.StaticText(self, label="Unfriendly Tags:")
		self.unfriendlyTags = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_MULTILINE)


		self.unfriendlybuttonsizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.setUnfriendlyButton = wx.Button(self, label="Set")
		#only works when one song is selected, edits the in-list object, but won't write to the file until saving
		self.setUnfriendlyButton.Bind(wx.EVT_BUTTON, self.SetUnfriendly)

		self.deleteUnfriendlyButton = wx.Button(self, label="Delete")
		self.deleteUnfriendlyButton.Bind(wx.EVT_BUTTON, self.DeleteUnfriendly)

		self.clearUnfriendlyButton = wx.Button(self, label="Clear")
		self.clearUnfriendlyButton.Bind(wx.EVT_BUTTON, self.ClearUnfriendly)

		self.unfriendlybuttonsizer.Add(self.setUnfriendlyButton, 1)
		self.unfriendlybuttonsizer.Add(self.deleteUnfriendlyButton, 1)
		self.unfriendlybuttonsizer.Add(self.clearUnfriendlyButton, 1)

		self.artandlyricssizer.Add(self.artsizer, 1)

		self.artandlyricssizer.Add(self.lyricscard, 0)
		self.artandlyricssizer.Add(self.lyricsfield, 5, wx.EXPAND|wx.RIGHT)
		self.artandlyricssizer.Add(self.unfriendlyTagsCard, 0)
		self.artandlyricssizer.Add(self.unfriendlyTags, 5, wx.EXPAND|wx.RIGHT)
		self.artandlyricssizer.Add(self.unfriendlybuttonsizer, 1)

		self.tagsandartsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.tagsandartsizer.Add(self.sizertagspart, 1, wx.LEFT)
		self.tagsandartsizer.Add(self.artandlyricssizer)
		#self.tagsandartsizer.Add(self.artsizer, 1, wx.RIGHT|wx.EXPAND)

		self.bigsizer.Add(self.sizerbuttonsparttop, 1, wx.EXPAND)
		self.bigsizer.Add(self.sizerbuttonspartmiddle, 1, wx.EXPAND)
		self.bigsizer.Add(self.sizerbuttonspartbottom, 1, wx.EXPAND)
		self.bigsizer.Add(self.tagsandartsizer, 1)
		self.SetSizer(self.bigsizer)
        
		self.SetAutoLayout(True)
		self.Layout()

		try:
			songs=sys.argv[1:]
			for song in songs:
				song=os.path.abspath(song)
				if song not in self.loadedSongs.GetStrings():
					songidentified=self.songIdentifier(song)
					if songidentified!=None:
						self.loadedSongs.Append(song)
						self.tagSong(songidentified, song)
						self.deletiondict[song]=0
						try:
							pic=self.getArtFromSong(song, self.currentarttype)
							if pic==None or pic.art==None:
								self.tempalbumartstorage.append({self.currentarttype:None})
								self.tempalbumartmimestorage.append({self.currentarttype:None})
								self.tempalbumartfilenamestorage.append({self.currentarttype:None})
							else:
								tempalbumartstorage=BytesIO(pic.art)
								try:
									theImage=wx.Bitmap(wx.Image(tempalbumartstorage))
									self.tempalbumartstorage.append({self.currentarttype:theImage})
								except:
									print_exc()
									print(song)
									self.tempalbumartstorage.append({self.currentarttype:None})
								self.tempalbumartmimestorage.append({self.currentarttype:pic.mime})
								self.tempalbumartfilenamestorage.append({self.currentarttype:None})
								tempalbumartstorage.close()
						except:
							print_exc()
					else:
						print("No recognizable tag!?")
			if len(self.loadedSongs.GetStrings())==1:
				self.loadedSongs.Select(0)
				self.onSelect(wx.EVT_LISTBOX)

		except:
			print_exc()

	def clearVisibleArt(self):
		self.theart.SetBitmap(self.theblank.ConvertToBitmap())

	def getArtFromSong(self, song, pictype):
		songid3data=self.songIdentifierForArt(song)
		extension=os.path.splitext(song)[1].lower()
		if extension==".mp3" or extension==".wav":
			#print(songid3data.keys())
			for i in songid3data.keys():
				if "APIC" in i or u"APIC" in i:
					if songid3data[i].type==pictype:
						return EasyArt(songid3data[i])
#				else:
					#print(i+": "+str(songid3data[i]))
			return None
		elif extension==".flac":
			if len(songid3data.pictures)>0:
				for picture in songid3data.pictures:
					if picture.type==pictype:
						return EasyArt(picture)
			else:
				return None
		elif extension==".ogg":
			
			if "METADATA_BLOCK_PICTURE" in songid3data:
				if type(songid3data["METADATA_BLOCK_PICTURE"])==list:
					overwrote=False
					for blockpicindex in range(0, len(songid3data["METADATA_BLOCK_PICTURE"])):
						if songid3data["METADATA_BLOCK_PICTURE"][blockpicindex].type==pictype:
							return EasyArt(songid3data["METADATA_BLOCK_PICTURE"][blockpicindex])
				else:
					if songid3data["METADATA_BLOCK_PICTURE"].type==pictype:
						return EasyArt(songid3data["METADATA_BLOCK_PICTURE"])
			elif "COVERART" in songid3data:
				if type(songid3data["COVERART"])==list:
					overwrote=False
					for blockpicindex in range(0, len(songid3data["COVERART"])):
						if songid3data["COVERART"][blockpicindex].type==pictype:
							return EasyArt(songid3data["COVERART"][blockpicindex])
				else:
					if songid3data["COVERART"].type==pictype:
						return EasyArt(songid3data["COVERART"])
			else:
				return None
		elif extension==".mp4" or extension==".m4a":
			songid3data=MP4(song)
			if "covr" in songid3data:

				if len(songid3data["covr"])>0:
					return EasyArt(songid3data["covr"][0])
			else:
				return None
		else:
			return None

	def getArts(self, song):
		#I need a new class, AgnosticAlbumArt
		#picture data itself, mime, cover art type, and functions to convert it to various formats
		#and constructors that let it take the various album art formats as arguments
		#EasyArt!
		extension=os.path.splitext(song)[1].lower()
		songid3data=self.songIdentifierForArt(song)
		allpics=[]
		if extension==".mp3" or extension==".wav":
			#print(songid3data.keys())
			for i in songid3data.keys():
				if "APIC" in i or u"APIC" in i:
					allpics.append(EasyArt(songid3data[i]))
		elif extension==".flac":
			if len(songid3data.pictures)>0:
				for pic in songid3data.pictures:
					allpics.append(EasyArt(pic))
		elif extension==".ogg":
			if "METADATA_BLOCK_PICTURE" in songid3data:
				for i in songid3data["METADATA_BLOCK_PICTURE"]:
					allpics.append(EasyArt(i))
			if "COVERART" in songid3data:
				for i in songid3data["COVERART"]:
					allpics.append(EasyArt(i))
		elif extension==".mp4" or extension==".m4a":
			songid3data=MP4(song)
#			for i in songid3data.keys():
#				if i!="covr":
#					print(i+": "+str(songid3data[i]))
#				else:
#					print(i+": "+str(len(str(songid3data[i]))))
			if "covr" in songid3data:
				if len(songid3data["covr"])>0:
					allpics.append(EasyArt(songid3data["covr"][0]))
		return allpics

	def songIdentifierForArt(self, song):
		#it returns a tags object
		tagObject=None
		extension=os.path.splitext(song)[1].lower()
		timeData=saveFileTimeData(song)
		if extension.lower()==".mp3":
			try:
				tagObject=ID3(song)
			except:
				tag=ID3()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		elif extension.lower()==".mp4" or extension.lower()==".m4a":
			#does it only work with ID3, from mutagen.id3?
			try:
				tagObject=EasyMP4(song)
			except:
				tag=EasyMP4()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		elif extension.lower()==".ogg":
			try:
				tagObject=OggVorbis(song)
			except:
				tag=OggVorbis()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		elif extension.lower()==".flac":
			try:
				tagObject=FLAC(song)
			except:
				tag=FLAC()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		elif extension.lower()==".wav":
			try:
				tagObject=WAVE(song)
			except:
				tag=WAVE()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		return tagObject

	def songDeleteArtSave(self, songid3data, extension, songpath):
		if self.restoreTimeDataCheck.IsChecked():
			timeData=saveFileTimeData(songpath)
		songid3data=self.songDeleteArtGui(songid3data, extension, False)
		songid3data.save(songpath)
		if self.restoreTimeDataCheck.IsChecked():
			restoreFileTimeData(songpath, timeData[0], timeData[1])
		return songid3data

	def songDeleteArtGui(self, songid3data, extension, all=False):
		if extension.lower()==".mp3" or extension.lower()==".wav":
			thekeys=list(songid3data.keys())
			#print(thekeys)
			for i in thekeys:
				if "APIC" in i or u"APIC" in i:
					if all==True or songid3data[i].type==self.currentarttype:
						del songid3data[i]
		elif extension.lower()==".flac":
			try:
				newpics=[]
				for pic in songid3data.pictures:
					if pic.type!=self.currentarttype:
						newpics.append(pic)
				songid3data.clear_pictures()
				for pic in newpics:
					songid3data.add_picture(pic)
			except:
				print_exc()
		elif extension==".mp4" or extension==".m4a":
			if "covr" in songid3data:
				del songid3data["covr"]
		elif extension==".ogg":
			if type(songid3data["METADATA_BLOCK_PICTURE"])==list:
				for blockpicindex in range(0, len(songid3data["METADATA_BLOCK_PICTURE"])):
					if songid3data["METADATA_BLOCK_PICTURE"][blockpicindex].type==self.currentarttype:
						del songid3data["METADATA_BLOCK_PICTURE"][blockpicindex]
			else:
				if songid3data["METADATA_BLOCK_PICTURE"].type==self.currentarttype:
					songid3data["METADATA_BLOCK_PICTURE"]=None
		return songid3data

	def saveArtToSong(self, songid3data, mime, song, imageData):
		extension=os.path.splitext(song)[1].lower()
		newArt=EasyArt()
		newArt.fromFileData(imageData, mime, self.currentarttype)
		#we're already clearing old m4a album art, but what about the rest?
		#print(mime+" is the mime")
		#print(extension+" is the extension")
		#print(str(self.currentarttype)+" is the cover image")

		#look for all APIC tags with the type of the currentarttype, delete

		if extension==".mp3" or extension==".wav":
			oldArt=[]
			for i in songid3data.keys():
				if "APIC" in i or u"APIC" in i:
					if songid3data[i].type==self.currentarttype:
						oldArt.append(i)
			for i in oldArt:
				print("We have old art! "+i)
				del songid3data[i]
			thearttag=newArt.toId3Art()
			if extension==".wav" or extension==".mp3":
				songid3data["APIC"]=thearttag
			else:
				songid3data.add(thearttag)

		elif extension==".flac":
			oldArt=[]
			for i in songid3data.keys():
				if type(songid3data[i])==Picture and songid3data[i].type==self.currentarttype:
					oldArt.append(i)
			for i in oldArt:
				del songid3data[i]	
			thearttag=newArt.toVorbisArt()
			songid3data.add_picture(thearttag)
		elif extension==".ogg":
			oldArt=[]
			for i in songid3data.keys():
				if type(songid3data[i])==Picture and songid3data[i].type==self.currentarttype:
					oldArt.append(i)
			for i in oldArt:
				del songid3data[i]
			if type(songid3data["METADATA_BLOCK_PICTURE"])==list:
				overwrote=False
				for blockpicindex in range(0, len(songid3data["METADATA_BLOCK_PICTURE"])):
					if songid3data["METADATA_BLOCK_PICTURE"][blockpicindex].type==self.currentarttype:
						songid3data["METADATA_BLOCK_PICTURE"][blockpicindex]=newArt.toVorbisArt()
						overwrote=True
				if overwrote==False:
					songid3data["METADATA_BLOCK_PICTURE"].append(newArt.toVorbisArt())
			else:
				if songid3data["METADATA_BLOCK_PICTURE"].type==self.currentarttype:
					songid3data["METADATA_BLOCK_PICTURE"]=newArt.toVorbisArt()
				else:
					oldpic=songid3data["METADATA_BLOCK_PICTURE"]
					songid3data["METADATA_BLOCK_PICTURE"]=[oldpic, newArt.toVorbisArt()]
		elif extension==".mp4" or extension==".m4a":
			print(self.wouldbeartfilename)
			songid3data=MP4(song)
			songid3data.tags["covr"] = [newArt.toMp4Art()]
		if self.restoreTimeDataCheck.IsChecked():
			timeData=saveFileTimeData(song)
		songid3data.save(song)
		if self.restoreTimeDataCheck.IsChecked():
			restoreFileTimeData(song, timeData[0], timeData[1])


	def songSaveArt(self, song, placeInList, multiples):
		#use self.opentag and access self.loadedSongsList
		extension=os.path.splitext(song)[1].lower()
		songid3data=self.songIdentifierForArt(song)
		mime=""
		if multiples==0:
			if self.deletiondict[song]==1:
				songid3data=self.songDeleteArtSave(songid3data, extension, song)
				self.deletiondict[song]=0
			else:
				if self.tempalbumartfilenamestorage[placeInList][self.currentarttype]:
#				if self.wouldbeartfilename:
					mime=self.tempalbumartmimestorage[placeInList][self.currentarttype]
					if mime and self.tempalbumartfilenamestorage[placeInList][self.currentarttype]:
						imageData=open(self.tempalbumartfilenamestorage[placeInList][self.currentarttype], "rb").read()
						#imageData=open(self.wouldbeartfilename, "rb").read()
						self.saveArtToSong(songid3data, mime, song, imageData)
		elif multiples==1:
			if self.artallcheck.IsChecked()==1 and song not in self.deletiondict:#are we using the current loaded image, or self.tempalbumartstorage?		
				songid3data=self.songDeleteArtSave(songid3data, extension, song)
#				if self.wouldbeartfilename:
				mime=self.tempalbumartmimestorage[placeInList][self.currentarttype]
				if mime and self.tempalbumartfilenamestorage[placeInList][self.currentarttype]:
					imageData=open(self.tempalbumartfilenamestorage[placeInList][self.currentarttype], "rb").read()
					if imageData:
						imageData=imageData.read()
						self.saveArtToSong(songid3data, mime, song, imageData)
			else:
				if self.deletiondict[song]==1:
					songid3data=self.songDeleteArtSave(songid3data, extension, song)
					self.deletiondict[song]=0
				else:
					if self.tempalbumartstorage[placeInList][self.currentarttype]:
						#We want to get the new art
						mime=self.tempalbumartmimestorage[placeInList][self.currentarttype]
						if mime and self.tempalbumartfilenamestorage[placeInList][self.currentarttype]:
							imageData=open(self.tempalbumartfilenamestorage[placeInList][self.currentarttype], "rb")
							if imageData:
								imageData=imageData.read()
								self.saveArtToSong(songid3data, mime, song, imageData)
				#it'll appear in the list of loaded tags, but not in the tag itself!

	def showArtOfSingleSelectedSong(self):
		if type(self.opentag)!=list and self.opentag>-1:
			self.thepic=self.tempalbumartstorage[self.opentag][self.currentarttype]
			if self.thepic:
				self.theart.SetBitmap(self.thepic.ConvertToImage().Rescale(200,200).ConvertToBitmap())
			else:
				self.theart.SetBitmap(self.theblank.ConvertToBitmap())
				
			#self.theart.name=self.thepic

	def cleaners(self):
		self.artistfield.SetValue("")
		self.albumartistfield.SetValue("")
		self.trackfield.SetValue("")
		self.discnumberfield.SetValue("")
		self.datefield.SetValue("")
		self.titlefield.SetValue("")
		self.albumfield.SetValue("")
		self.genrefield.SetValue("")
		self.composerfield.SetValue("")
		self.conductorfield.SetValue("")
		self.encodedbyfield.SetValue("")
		self.encodersettingsfield.SetValue("")
		self.bpmfield.SetValue("")
		self.organizationfield.SetValue("")
		self.websitefield.SetValue("")
		self.copyrightfield.SetValue("")
		self.isrcfield.SetValue("")
		self.versionfield.SetValue("")
		self.cdinfofield.SetValue("")
		self.lengthfield.SetValue("")
		self.commentsfield.SetValue("")
		self.lyricsfield.SetValue("")
		self.unfriendlyTags.SetValue("")

	def readTag(self, songtagsource, song):
		tags={}
		#print(songtagsource.keys())
		extension=os.path.splitext(song)[1].lower()

		if "comments" in songtagsource and extension==".flac":
			timeData=saveFileTimeData(song)
			songtagsource["comment"]=listToStringSemicolon(songtagsource["comments"])
			tags["comments"]=listToStringSemicolon(songtagsource["comment"])
			del songtagsource["comments"]
			songtagsource.save()
			restoreFileTimeData(song, timeData[0], timeData[1])
		if "comment" in songtagsource:
			tags["comments"]=listToStringSemicolon(songtagsource["comment"])
		elif "comments" in songtagsource:
			if extension==".flac":
				timeData=saveFileTimeData(song)
				songtagsource["comment"]=listToStringSemicolon(songtagsource["comments"])
				tags["comments"]=listToStringSemicolon(songtagsource["comment"])
				del songtagsource["comments"]
				songtagsource.save()
				restoreFileTimeData(song, timeData[0], timeData[1])
			else:
				tags["comments"]=listToStringSemicolon(songtagsource["comments"])
		for tag in standardTags:
			if tag in songtagsource:
				tags[tag]=listToStringSemicolon(songtagsource[tag])
			else:
				if tag not in tags:
					tags[tag]=""
		unfriendly={}		
		if extension==".mp3" or extension==".wav":
			
			for key in songtagsource.unfriendlyKeys():
				unfriendly[key]=songtagsource.getUnfriendly(key)
		else:
			unfriendly=getUnfriendlyTags(songtagsource)
		if len(unfriendly):
			tags["unfriendly"]=unfriendly
		return tags

	def tagSong(self, songtagsource, song):
		tags=self.readTag(songtagsource, song)
		self.loadedSongsList.append(tags)

	def retagSong(self, songtagsource, index, song):
		tags=self.readTag(songtagsource, song)
		self.loadedSongsList[index]=tags

	def songIdentifier(self, song):
		#it returns a tags object
		tagObject=None
		extension=os.path.splitext(song)[1].lower()
		timeData=saveFileTimeData(song)
		hardID3=None
		if extension.lower() not in [".mp3", ".mp4", ".m4a", ".ogg", ".flac", ".asf", ".wma", ".wmv", ".wav"]:
			return None
		if extension.lower()==".mp3":
			try:
				tagObject=EasierMP3(song)
				
			except:
				print_exc()
				tag=EasierMP3()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		elif extension.lower()==".mp4" or extension.lower()==".m4a":
			#does it only work with ID3, from mutagen.id3?
			try:
				tagObject=EasyMP4(song)
			except:
				tag=EasyMP4()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		elif extension.lower()==".ogg":
			try:
				tagObject=OggVorbis(song)
			except:
				tag=OggVorbis()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		elif extension.lower()==".flac":
			try:
				tagObject=FLAC(song)
			except:
				tag=FLAC()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		elif extension.lower() in [".asf", ".wma", ".wmv"]:
			try:
				#tagObject=ASF(song)
				tagObject=WMedia(song)
			except:
				#tag=ASF()
				tag=WMedia()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		elif extension.lower()==".wav":
			try:
				tagObject=WAV(song)
			except:
				print("No tag?")
				tag=WAV()
				tagObject=tag
				tagObject.save(song)
				restoreFileTimeData(song, timeData[0], timeData[1])
		return tagObject

	def songsavetags(self, song, myplace, multiples):
		timeData=[]
		#use self.opentag and access self.loadedSongsList
		songid3data=self.songIdentifier(song)
		currentTags={}
		for tag in standardTags:
			currentTags[tag]=""
		#gotta add the tags one by one!?!?!?
		if self.restoreTimeDataCheck.IsChecked():
			timeData=saveFileTimeData(song)
		if multiples==0:
			#If we save the hard mode ID3 tag, we gotta make a new EasyID3 tag or else old comment data is restored
			#That's why this code is first
			currentComments=""
			
			if "comment" in songid3data:
				currentComments=songid3data["comment"][0]
				if self.loadedSongsList[myplace]["comments"]!=currentComments:
					songid3data["comment"] = self.loadedSongsList[myplace]["comments"]
			for tag in standardTags:
				if tag in songid3data:					
					if tag=="comments" and type(songid3data)==EasyMP4:
						tag="comment"
					currentTags[tag]=listToStringSemicolon(songid3data[tag])
				if self.loadedSongsList[myplace][tag]!=currentTags[tag]:
					if type(songid3data)!=EasyMP4 or type(songid3data)==EasyMP4 and tag not in mp4Missing:
						if type(songid3data)==EasyMP4 and tag=="bpm" and len(self.loadedSongsList[myplace][tag])==0:
							del songid3data[tag]
						else:
							tagToUse=tag
							if tag=="comments" and type(songid3data)==EasyMP4:
								tagToUse="comment"
							if self.loadedSongsList[myplace][tag]:
								try:
									songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
								except ValueError:
									print("Bad value for tag "+tag+" for file "+song+": "+self.loadedSongsList[myplace][tag])
							else:
								del songid3data[tag]
			if "unfriendly" in self.loadedSongsList[myplace]:
				songid3data.save(song)

				#the save function should loop through the unfriendly tags and setUnfriendly each of them before saving
				#but what about deleted tags? if the file's unfriendlies has a tag the Utaedit version doesn't, delete it

				#anything with Vorbis tags, do they even have unfriendly tags?
				#how about EasyMP4?
				#if they do, I just need to change the modification process for adding and deleting
				#and for getting, a function that takes the tag objects and reports everything not in standardTags
				if issubclass(type(songid3data), EasySong):
					localUnfriendlyKeys=self.loadedSongsList[myplace]["unfriendly"].keys()
					for unfriendlyKey in localUnfriendlyKeys:
						if songid3data.getUnfriendly(unfriendlyKey)!=self.loadedSongsList[myplace]["unfriendly"][unfriendlyKey]:
							songid3data.setUnfriendly(unfriendlyKey, self.loadedSongsList[myplace]["unfriendly"][unfriendlyKey])
					fileUnfriendlyKeys=songid3data.unfriendlyKeys()
					for fileUnfriendlyKey in fileUnfriendlyKeys:
						if fileUnfriendlyKey not in localUnfriendlyKeys:
							songid3data.removeUnfriendly(fileUnfriendlyKey)
				elif type(songid3data)==EasyMP4:
					songid3data.save(song)
					songThatWas=getUnfriendlyTags(songid3data)
					localUnfriendlyKeys=self.loadedSongsList[myplace]["unfriendly"].keys()
					for unfriendlyKey in localUnfriendlyKeys:
						if songThatWas[unfriendlyKey]!=self.loadedSongsList[myplace]["unfriendly"][unfriendlyKey]:
							songThatWas[unfriendlyKey]=self.loadedSongsList[myplace]["unfriendly"][unfriendlyKey]
					deleteThese=[]
					for key in songThatWas.keys():
						if key not in self.loadedSongsList[myplace]["unfriendly"]:
							deleteThese.append(key)
					theMp4=MP4(song)
					for key in songThatWas.keys():
						#print(key+" "+str(songThatWas[key]))
						if key not in theMp4:
							theMp4[key]=[songThatWas[key]]
						elif type(theMp4[key])==bool:
							if songThatWas[key]=="True" or songThatWas[key]=="1":
								theMp4[key]=True
							else:
								theMp4[key]=False
						elif type(theMp4[key][0])==int:
							try:
								theMp4[key][0]=int(songThatWas[key][0])
							except:
								print_exc()
						else:
							#print(type(theMp4[key]))
							theMp4[key][0]=songThatWas[key][0]
					for deleteThis in deleteThese:
						del theMp4[deleteThis]
					theMp4.save(song)
					songid3data=self.songIdentifier(song)
				elif type(songid3data)==FLAC or type(songid3data)==OggVorbis:
					unfriendly=getUnfriendlyTags(songid3data)
					localUnfriendlyKeys=self.loadedSongsList[myplace]["unfriendly"].keys()
					for unfriendlyKey in localUnfriendlyKeys:
						if songid3data[unfriendlyKey]!=self.loadedSongsList[myplace]["unfriendly"][unfriendlyKey]:
							songid3data[unfriendlyKey]=self.loadedSongsList[myplace]["unfriendly"][unfriendlyKey]
					fileUnfriendlyKeys=getUnfriendlyTags(songid3data)
					for fileUnfriendlyKey in fileUnfriendlyKeys:
						if fileUnfriendlyKey not in localUnfriendlyKeys:
							del songid3data[fileUnfriendlyKey]
					songid3data.save(song)
				self.loadUnfriendly()
			songid3data.save(song)
			#print(songid3data)
			self.retagSong(songid3data, myplace, song)
			if self.restoreTimeDataCheck.IsChecked():
				restoreFileTimeData(song, timeData[0], timeData[1])
		elif multiples==1:
			for tag in standardTags:
				if tag in songid3data:
					currentTags[tag]=listToStringSemicolon(songid3data[tag])
			#make mp3-only version so you can do more tags?
			if type(songid3data)!=WMedia:
				if self.commentscheck.IsChecked()==1:
					currentComments=""
					if "comment" in songid3data:
						currentComments=songid3data["comment"][0]
						if self.commentsfield.GetValue()!=currentComments:
							songid3data["comment"] = self.commentsfield.GetValue()
				else:
					#songid3data["comments"] = self.loadedSongsList[myplace]["comments"]

					if "comment" in songid3data:
						songid3data["comment"] = self.loadedSongsList[myplace]["comments"]

#if it's not an ASF tag, gotta check if not ASF
#if it is, then make the final key either the ASF or non-ASF version of the tag
			for tag in standardTags:
				validTag=False
				tagToUse=tag
				if type(songid3data)!=EasyMP4 or type(songid3data)==EasyMP4 and tag not in mp4Missing:
					validTag=True
				if validTag:
				#terminate if this is an ASF file and the tag doesn't have an ASF equivalent
					try:
						if tag=="artist":
							if self.artistcheck.IsChecked()==1:
								if self.artistfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.artistfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="albumartist":
							if self.albumartistcheck.IsChecked()==1:
								if self.albumartistfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.albumartistfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="tracknumber" and len(self.loadedSongsList[myplace][tag].strip()):
							songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="discnumber":
							if self.discnumbercheck.IsChecked()==1:
								if self.discnumberfield.GetValue()!=currentTags[tag]:
									if len(self.discnumberfield.GetValue()):
										songid3data[tagToUse] = self.discnumberfield.GetValue()
									else:
										if tagToUse in songid3data:
											del songid3data[tagToUse]
							else:
								#if len(self.loadedSongsList[myplace][tag]) and tag not in currentTags or currentTags[tag]!=self.loadedSongsList[myplace][tag]:
								if len(self.loadedSongsList[myplace][tag].strip()):
									songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
								else:
									if tagToUse in songid3data:
										del songid3data[tagToUse]

						elif tag=="date":
							if self.datecheck.IsChecked()==1:
								if self.datefield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.datefield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="title":
							songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="album":
							if self.albumcheck.IsChecked()==1:
								if self.albumfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.albumfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="genre":
							if self.genrecheck.IsChecked()==1:
								if self.genrefield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.genrefield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="composer":
							if self.composercheck.IsChecked()==1:
								if self.composerfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.composerfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="conductor":
							if self.conductorcheck.IsChecked()==1:
								if self.conductorfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.conductorfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="encodedby":
							if self.encodedbycheck.IsChecked()==1:
								if self.encodedbyfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.encodedbyfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="encodersettings":
							if self.encodersettingscheck.IsChecked()==1:
								if self.encodersettingsfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.encodersettingsfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="bpm":
							if self.bpmcheck.IsChecked()==1:
								if self.bpmfield.GetValue()!=currentTags[tag]:
									if len(self.bpmfield.GetValue())==0:
										if tagToUse in songid3data:
											del songid3data[tagToUse]
									else:
										songid3data[tagToUse] = self.bpmfield.GetValue()
							else:
								if len(self.loadedSongsList[myplace][tag])==0:
									if tagToUse in songid3data:
										del songid3data[tagToUse]
								else:
									songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="organization":
							if self.organizationcheck.IsChecked()==1:
								if self.organizationfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.organizationfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="website":
							if self.websitecheck.IsChecked()==1:
								if self.websitefield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.websitefield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="copyright":
							if self.copyrightcheck.IsChecked()==1:
								if self.copyrightfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.copyrightfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="isrc":
							if self.isrccheck.IsChecked()==1:
								if self.isrcfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.isrcfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="version":
							if self.versioncheck.IsChecked()==1:
								if self.versionfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.versionfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="cdinfo":
							if self.cdinfocheck.IsChecked()==1:
								if self.cdinfofield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.cdinfofield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="length":
							if self.lengthcheck.IsChecked()==1:
								if self.lengthfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.lengthfield.GetValue()
							else:
								songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="comments":
							if type(songid3data)==EasyMP4:
								tagToUse="comment"
							if self.commentscheck.IsChecked()==1:
								if self.commentsfield.GetValue()!=currentTags[tag]:
									songid3data[tagToUse] = self.commentsfield.GetValue()
							else:
								if tag in self.loadedSongsList[myplace]:
									songid3data[tagToUse] = self.loadedSongsList[myplace][tag]
						elif tag=="lyrics":
							songid3data[tagToUse] = self.loadedSongsList[myplace][tag]

					except ValueError:
						print("Bad value for tag "+tag+" for file "+song+": either "+self.loadedSongsList[myplace][tag]+" or the value in the "+tag+" field.")
			#it's gotta write all modifications! not just the "all songs" ones! title and track!
			#don't just care about myplace! loop through all selections!
			#it only writes to the first one...it should repeat the process of giving new tags for each
			songid3data.save(song)
			self.retagSong(songid3data, myplace, song)
			if self.restoreTimeDataCheck.IsChecked():
				restoreFileTimeData(song, timeData[0], timeData[1])
			#it'll appear in the list of loaded tags, but not in the tag itself!

	def opentagscenterstage(self):
		if self.opentag>-1:
			if self.loadedSongsList[self.opentag]["artist"]!=self.artistfield.GetValue():
				self.loadedSongsList[self.opentag]["artist"]=self.artistfield.GetValue()
			if self.loadedSongsList[self.opentag]["albumartist"]!=self.albumartistfield.GetValue():
				self.loadedSongsList[self.opentag]["albumartist"]=self.albumartistfield.GetValue()
			if self.loadedSongsList[self.opentag]["tracknumber"]!=self.trackfield.GetValue():
				self.loadedSongsList[self.opentag]["tracknumber"]=self.trackfield.GetValue()
			if self.loadedSongsList[self.opentag]["discnumber"]!=self.discnumberfield.GetValue():
				self.loadedSongsList[self.opentag]["discnumber"]=self.discnumberfield.GetValue()
			if self.loadedSongsList[self.opentag]["date"]!=self.datefield.GetValue():
				self.loadedSongsList[self.opentag]["date"]=self.datefield.GetValue()
			if self.loadedSongsList[self.opentag]["title"]!=self.titlefield.GetValue():
				self.loadedSongsList[self.opentag]["title"]=self.titlefield.GetValue()
			if self.loadedSongsList[self.opentag]["album"]!=self.albumfield.GetValue():
				self.loadedSongsList[self.opentag]["album"]=self.albumfield.GetValue()
			if self.loadedSongsList[self.opentag]["genre"]!=self.genrefield.GetValue():
				self.loadedSongsList[self.opentag]["genre"]=self.genrefield.GetValue()
			if self.loadedSongsList[self.opentag]["composer"]!=self.composerfield.GetValue():
				self.loadedSongsList[self.opentag]["composer"]=self.composerfield.GetValue()
			if self.loadedSongsList[self.opentag]["conductor"]!=self.conductorfield.GetValue():
				self.loadedSongsList[self.opentag]["conductor"]=self.conductorfield.GetValue()
			if self.loadedSongsList[self.opentag]["encodedby"]!=self.encodedbyfield.GetValue():
				self.loadedSongsList[self.opentag]["encodedby"]=self.encodedbyfield.GetValue()
			if self.loadedSongsList[self.opentag]["encodersettings"]!=self.encodersettingsfield.GetValue():
				self.loadedSongsList[self.opentag]["encodersettings"]=self.encodersettingsfield.GetValue()
			if self.loadedSongsList[self.opentag]["bpm"]!=self.bpmfield.GetValue():
				self.loadedSongsList[self.opentag]["bpm"]=self.bpmfield.GetValue()
			if self.loadedSongsList[self.opentag]["organization"]!=self.organizationfield.GetValue():
				self.loadedSongsList[self.opentag]["organization"]=self.organizationfield.GetValue()
			if self.loadedSongsList[self.opentag]["website"]!=self.websitefield.GetValue():
				self.loadedSongsList[self.opentag]["website"]=self.websitefield.GetValue()
			if self.loadedSongsList[self.opentag]["copyright"]!=self.copyrightfield.GetValue():
				self.loadedSongsList[self.opentag]["copyright"]=self.copyrightfield.GetValue()
			if self.loadedSongsList[self.opentag]["isrc"]!=self.isrcfield.GetValue():
				self.loadedSongsList[self.opentag]["isrc"]=self.isrcfield.GetValue()
			if self.loadedSongsList[self.opentag]["version"]!=self.versionfield.GetValue():
				self.loadedSongsList[self.opentag]["version"]=self.versionfield.GetValue()
			if self.loadedSongsList[self.opentag]["cdinfo"]!=self.cdinfofield.GetValue():
				self.loadedSongsList[self.opentag]["cdinfo"]=self.cdinfofield.GetValue()
			if self.loadedSongsList[self.opentag]["length"]!=self.lengthfield.GetValue():
				self.loadedSongsList[self.opentag]["length"]=self.lengthfield.GetValue()
			if self.loadedSongsList[self.opentag]["comments"]!=self.commentsfield.GetValue():
				self.loadedSongsList[self.opentag]["comments"]=self.commentsfield.GetValue()
			if self.loadedSongsList[self.opentag]["lyrics"]!=self.lyricsfield.GetValue():
				self.loadedSongsList[self.opentag]["lyrics"]=self.lyricsfield.GetValue()
			
	def onSelect(self, event):
		#if exiting, just forget it, wrap it all in an else
		#you find what you just changed from, and you check if the values have changed from loadedSongsList[oldone]
		#and if different, you change the values
		#happens if you press the X too, after editing?
		if self.opentag>-1:
			self.opentagscenterstage()
			#move the lowers over to the right?

		if len(self.loadedSongs.GetSelections())==0:
			self.opentag=-1
			self.artistfield.SetValue("")
			self.albumartistfield.SetValue("")
			self.trackfield.SetValue("")
			self.discnumberfield.SetValue("")		
			self.datefield.SetValue("")
			self.titlefield.SetValue("")
			self.albumfield.SetValue("")
			#this code is how many years old and I only noticed this on 2020/12/28? well, redundant code that confused me
			self.genrefield.SetValue("")
			self.composerfield.SetValue("")
			self.conductorfield.SetValue("")
			self.encodedbyfield.SetValue("")
			self.encodersettingsfield.SetValue("")
			self.bpmfield.SetValue("")
			self.organizationfield.SetValue("")
			self.websitefield.SetValue("")
			self.copyrightfield.SetValue("")
			self.isrcfield.SetValue("")
			self.versionfield.SetValue("")
			self.cdinfofield.SetValue("")
			self.lengthfield.SetValue("")
			self.commentsfield.SetValue("")
			self.lyricsfield.SetValue("")
			self.unfriendlyTags.SetValue("")

			self.thepic=self.theblank.ConvertToBitmap()
			self.theart.SetBitmap(self.thepic)

		if len(self.loadedSongs.GetSelections())==1:
			#self.multieditingmode=0
#			selectedsong=self.loadedSongs.GetString(self.loadedSongs.GetSelections()[0])
			self.opentag=self.loadedSongs.GetSelections()[0]
			#keep if there is no difference
			#FUCKING HEISENBUG
			self.artistfield.SetValue(self.loadedSongsList[self.opentag]["artist"])
			self.albumartistfield.SetValue(self.loadedSongsList[self.opentag]["albumartist"])
			self.trackfield.SetValue(self.loadedSongsList[self.opentag]["tracknumber"])
			self.discnumberfield.SetValue(self.loadedSongsList[self.opentag]["discnumber"])
			self.datefield.SetValue(self.loadedSongsList[self.opentag]["date"])
			self.titlefield.SetValue(self.loadedSongsList[self.opentag]["title"])
			self.albumfield.SetValue(self.loadedSongsList[self.opentag]["album"])
			self.genrefield.SetValue(self.loadedSongsList[self.opentag]["genre"])
			self.composerfield.SetValue(self.loadedSongsList[self.opentag]["composer"])
			self.conductorfield.SetValue(self.loadedSongsList[self.opentag]["conductor"])
			self.encodedbyfield.SetValue(self.loadedSongsList[self.opentag]["encodedby"])
			self.encodersettingsfield.SetValue(self.loadedSongsList[self.opentag]["encodersettings"])
			self.bpmfield.SetValue(self.loadedSongsList[self.opentag]["bpm"])
			self.organizationfield.SetValue(self.loadedSongsList[self.opentag]["organization"])
			self.websitefield.SetValue(self.loadedSongsList[self.opentag]["website"])
			self.copyrightfield.SetValue(self.loadedSongsList[self.opentag]["copyright"])
			self.isrcfield.SetValue(self.loadedSongsList[self.opentag]["isrc"])
			self.versionfield.SetValue(self.loadedSongsList[self.opentag]["version"])
			self.cdinfofield.SetValue(self.loadedSongsList[self.opentag]["cdinfo"])
			self.lengthfield.SetValue(self.loadedSongsList[self.opentag]["length"])
			#Would this fly?
			#self.commentsfield.SetValue(self.loadedSongsList[self.opentag]["comments"])
			#print(self.loadedSongsList[self.opentag])
			if "comments" in self.loadedSongsList[self.opentag] and self.loadedSongsList[self.opentag]["comments"]!=None:
				self.commentsfield.SetValue(self.loadedSongsList[self.opentag]["comments"])
			else:
				self.commentsfield.SetValue("")
			if "lyrics" in self.loadedSongsList[self.opentag] and self.loadedSongsList[self.opentag]["lyrics"]!=None:
				self.lyricsfield.SetValue(self.loadedSongsList[self.opentag]["lyrics"])
			else:
				self.lyricsfield.SetValue("")

			self.loadUnfriendly()
			try:
				if self.deletiondict[self.loadedSongs.GetStrings()[0]]!=1:
					if self.tempalbumartstorage[self.opentag][self.currentarttype]==None:
						self.theart.SetBitmap(self.theblank.ConvertToBitmap())
					else:
						pic=wx.Bitmap(self.tempalbumartstorage[self.opentag][self.currentarttype].ConvertToImage().Rescale(200,200))
						if self.thepic!=pic:
							self.thepic=pic
							self.theart.SetBitmap(self.thepic)
			except:
				print_exc()
				
		elif len(self.loadedSongs.GetSelections())>1:
			self.opentag=-1
			selected=self.loadedSongs.GetSelections()
			selectedTags=[]
			selectedArt=[]
			for i in selected:
				selectedTags.append(self.loadedSongsList[i])
				selectedArt.append(self.loadedSongs.GetStrings()[i])
			#this scales terribly, changing to a dict
			#sameTag=[1,1,1,1,1,1]
			sameArt=1
			for i in range(1, len(selectedArt)):
				if sameArt==1:
					try:
						if self.getArtFromSong(selectedArt[i], self.currentarttype) and self.getArtFromSong(selectedArt[i], self.currentarttype).art!=self.getArtFromSong(selectedArt[0], self.currentarttype).art:
							#print("Something's not right here.")
						#if selectedArt[i]!=selectedArt[0][0]:
							
							self.thepic=self.theblank.ConvertToBitmap()
							#on change, theart SetBitmap automatically?
							self.theart.SetBitmap(self.thepic)
							
							#print("Not the same art.")
							sameArt=0
							break
					except:
						print_exc()
						self.thepic=self.theblank.ConvertToBitmap()
						#on change, theart SetBitmap automatically?
						self.theart.SetBitmap(self.thepic)
						#print("Not the same art either.")
						sameArt=0
						break
			if sameArt==1:
				pic=self.tempalbumartstorage[self.loadedSongs.GetSelections()[0]][self.currentarttype]
				if pic:
					superpic=wx.Bitmap(pic.ConvertToImage().Rescale(200,200))
				else:
					superpic=self.theblank.ConvertToBitmap()
				if self.thepic!=superpic:
					self.thepic=superpic
					self.theart.SetBitmap(self.thepic)
					
			sameTag={"artist":1,
			"albumartist":1,
			"tracknumber":1,
			"discnumber":1,
			"date":1,
			"title":1,
			"album":1,
			"genre":1,
			"composer":1,
			"conductor":1,			
			"encodedby":1,
			"encodersettings":1,
			"bpm":1,
			"organization":1,
			"website":1,
			"copyright":1,
			"isrc":1,
			"version":1,
			"cdinfo":1,
			"length":1,
			"comments":1,
			"lyrics":1,
			}
			for i in range(1,len(selectedTags)):
				#how about comparing them all to 0?
				#h=i-1
#				else:
#					h=self.opentag
				for potentialSameTag in sameTag.keys():
					if sameTag[potentialSameTag]==1:
						if selectedTags[i][potentialSameTag]!=selectedTags[0][potentialSameTag]:
							sameTag[potentialSameTag]=0
							if potentialSameTag=="artist":
								self.artistfield.SetValue("")
							elif potentialSameTag=="albumartist":
								self.albumartistfield.SetValue("")
							elif potentialSameTag=="tracknumber":
								self.trackfield.SetValue("")
							elif potentialSameTag=="discnumber":
								self.discnumberfield.SetValue("")
							elif potentialSameTag=="date":
								self.datefield.SetValue("")
							elif potentialSameTag=="album":
								self.albumfield.SetValue("")
							elif potentialSameTag=="title":
								self.titlefield.SetValue("")
							elif potentialSameTag=="genre":
								self.genrefield.SetValue("")
							elif potentialSameTag=="composer":
								self.composerfield.SetValue("")
							elif potentialSameTag=="conductor":
								self.conductorfield.SetValue("")
							elif potentialSameTag=="encodedby":
								self.encodedbyfield.SetValue("")
							elif potentialSameTag=="encodersettings":
								self.encodersettingsfield.SetValue("")
							elif potentialSameTag=="bpm":
								self.bpmfield.SetValue("")
							elif potentialSameTag=="organization":
								self.organizationfield.SetValue("")
							elif potentialSameTag=="website":
								self.websitefield.SetValue("")
							elif potentialSameTag=="copyright":
								self.copyrightfield.SetValue("")
							elif potentialSameTag=="isrc":
								self.isrcfield.SetValue("")
							elif potentialSameTag=="version":
								self.versionfield.SetValue("")
							elif potentialSameTag=="cdinfo":
								self.cdinfofield.SetValue("")
							elif potentialSameTag=="length":
								self.lengthfield.SetValue("")
							elif potentialSameTag=="comments":
								self.commentsfield.SetValue("")
							elif potentialSameTag=="lyrics":
								self.lyricsfield.SetValue("")

			if sameTag["artist"]==1:
				self.artistfield.SetValue(selectedTags[0]["artist"])
			if sameTag["albumartist"]==1:
				self.albumartistfield.SetValue(selectedTags[0]["albumartist"])
			if sameTag["tracknumber"]==1:
				self.trackfield.SetValue(selectedTags[0]["tracknumber"])
			if sameTag["discnumber"]==1:
				self.discnumberfield.SetValue(selectedTags[0]["discnumber"])
			if sameTag["date"]==1:
				self.datefield.SetValue(selectedTags[0]["date"])
			if sameTag["title"]==1:
				self.titlefield.SetValue(selectedTags[0]["title"])
			if sameTag["album"]==1:
				self.albumfield.SetValue(selectedTags[0]["album"])
			if sameTag["genre"]==1:
				self.genrefield.SetValue(selectedTags[0]["genre"])
			if sameTag["composer"]==1:
				self.composerfield.SetValue(selectedTags[0]["composer"])
			if sameTag["conductor"]==1:
				self.conductorfield.SetValue(selectedTags[0]["conductor"])
			if sameTag["encodedby"]==1:
				self.encodedbyfield.SetValue(selectedTags[0]["encodedby"])
			if sameTag["encodersettings"]==1:
				self.encodersettingsfield.SetValue(selectedTags[0]["encodersettings"])
			if sameTag["bpm"]==1:
				self.bpmfield.SetValue(selectedTags[0]["bpm"])
			if sameTag["organization"]==1:
				self.organizationfield.SetValue(selectedTags[0]["organization"])
			if sameTag["website"]==1:
				self.websitefield.SetValue(selectedTags[0]["website"])
			if sameTag["copyright"]==1:
				self.copyrightfield.SetValue(selectedTags[0]["copyright"])
			if sameTag["isrc"]==1:
				self.isrcfield.SetValue(selectedTags[0]["isrc"])
			if sameTag["version"]==1:
				self.versionfield.SetValue(selectedTags[0]["version"])
			if sameTag["cdinfo"]==1:
				self.cdinfofield.SetValue(selectedTags[0]["cdinfo"])
			if sameTag["length"]==1:
				self.lengthfield.SetValue(selectedTags[0]["length"])
			if sameTag["comments"]==1:
				self.commentsfield.SetValue(selectedTags[0]["comments"])
			if sameTag["lyrics"]==1:
				self.lyricsfield.SetValue(selectedTags[0]["lyrics"])
			self.unfriendlyTags.SetValue("")

	def BringUpSong(self, event):
		#dlg = wx.FileDialog(None, message="Pick your songs!", defaultDir="", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE)
		dlg = wx.FileDialog(None, defaultDir=os.getcwd(), message="Pick your songs!", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR)
		choice=dlg.ShowModal()
		if choice==wx.ID_OK:
			yoursongs=dlg.GetPaths()
			selections = self.loadedSongs.GetStrings()
			for song in yoursongs:
				song=os.path.abspath(song)
				if song not in selections:
					songidentified=self.songIdentifier(song)
					if songidentified!=None:
						self.loadedSongs.Append(song)
						self.tagSong(songidentified, song)
						self.deletiondict[song]=0
					self.deletiondict[song]=0
					try:
						pic=self.getArtFromSong(song, self.currentarttype)
						if pic==None:
							self.tempalbumartstorage.append({self.currentarttype:None})
							self.tempalbumartmimestorage.append({self.currentarttype:None})
							self.tempalbumartfilenamestorage.append({self.currentarttype:None})
						else:
							tempalbumartstorage=BytesIO(pic.art)
							try:
								theImage=wx.Bitmap(wx.Image(tempalbumartstorage))
								self.tempalbumartstorage.append({self.currentarttype:theImage})
							except:
								print_exc()
								print(song)
								self.tempalbumartstorage.append({self.currentarttype:None})
							self.tempalbumartmimestorage.append({self.currentarttype:pic.mime})
							self.tempalbumartfilenamestorage.append({self.currentarttype:None})
							tempalbumartstorage.close()
					except:
						print_exc()
						
			if len(self.loadedSongs.GetStrings())==1:
				self.loadedSongs.Select(0)
				self.onSelect(wx.EVT_LISTBOX)

	def SetUnfriendly(self, event):
		#One song must be selected!
		#Must it?
		if len(self.loadedSongs.GetSelections())==1:
			setKeyModal = wx.TextEntryDialog(self, "Key to set?")
			if setKeyModal.ShowModal() == wx.ID_OK:
				setKey=setKeyModal.GetValue()
				if setKey:
					setValueModal = wx.TextEntryDialog(self, "Value to set?")
					if setValueModal.ShowModal() == wx.ID_OK:
						setValue=setValueModal.GetValue()
						if "unfriendly" not in self.loadedSongsList[self.loadedSongs.GetSelections()[0]]:
							self.loadedSongsList[self.loadedSongs.GetSelections()[0]]["unfriendly"]={}
						self.loadedSongsList[self.loadedSongs.GetSelections()[0]]["unfriendly"][setKey]=setValue
						#afterwards, reload the song
			self.loadUnfriendly()

	def DeleteUnfriendly(self, event):
		if len(self.loadedSongs.GetSelections())==1 and "unfriendly" in self.loadedSongsList[self.loadedSongs.GetSelections()[0]]:
			deleteKeyModal = wx.TextEntryDialog(self, "Key to delete?")
			if deleteKeyModal.ShowModal() == wx.ID_OK:
				deleteKey=deleteKeyModal.GetValue()
				if deleteKey in self.loadedSongsList[self.loadedSongs.GetSelections()[0]]["unfriendly"]:
					del self.loadedSongsList[self.loadedSongs.GetSelections()[0]]["unfriendly"][deleteKey]
					#afterwards, reload the song
			self.loadUnfriendly()

	def ClearUnfriendly(self, event):
		if len(self.loadedSongs.GetSelections())==1 and "unfriendly" in self.loadedSongsList[self.loadedSongs.GetSelections()[0]]:
			self.loadedSongsList[self.loadedSongs.GetSelections()[0]]["unfriendly"]={}
			self.loadUnfriendly()

	def BringUpArt(self, event):
		#At least one song must be selected!
		if len(self.loadedSongs.GetSelections())>1 and self.artallcheck.IsChecked() or len(self.loadedSongs.GetSelections())==1:
		#for each of the selections, set their tempalbumartimage to it
			dlg = wx.FileDialog(None, defaultDir=os.getcwd(), message="Pick your album art!", wildcard=imagesWildcard, style=wx.FD_OPEN)
			choice=dlg.ShowModal()
			if choice==wx.ID_OK:
				self.wouldbeartfilename=dlg.GetPath()
				apic=wx.Bitmap(self.wouldbeartfilename)
				mime=""
				if self.wouldbeartfilename.split(".")[-1].lower()=="jpg" or self.wouldbeartfilename.split(".")[-1].lower()=="jpeg" or self.wouldbeartfilename.split(".")[-1].lower()=="jpe":
					mime='image/jpeg' # image/jpeg or image/png
				elif self.wouldbeartfilename.split(".")[-1].lower()=="png":
					mime='image/png' # image/jpeg or image/png
				
				print(mime)
				#print(self.tempalbumartfilenamestorage)
				if len(self.loadedSongs.GetSelections())==1:
					self.tempalbumartstorage[self.loadedSongs.GetSelections()[0]][self.currentarttype]=apic
					self.tempalbumartmimestorage[self.loadedSongs.GetSelections()[0]][self.currentarttype]=mime
					self.tempalbumartfilenamestorage[self.loadedSongs.GetSelections()[0]][self.currentarttype]=self.wouldbeartfilename
				elif len(self.loadedSongs.GetSelections())>1:
					for thesong in self.loadedSongs.GetSelections():
						self.tempalbumartstorage[thesong][self.currentarttype]=apic
						self.tempalbumartmimestorage[thesong][self.currentarttype]=mime
						self.tempalbumartfilenamestorage[thesong][self.currentarttype]=self.wouldbeartfilename
				self.thepic=wx.Bitmap(apic.ConvertToImage().Rescale(200,200))
				self.theart.SetBitmap(self.thepic)

	def SaveTheTags(self, event):
		if len(self.loadedSongs.GetSelections())==1:
			self.opentagscenterstage()
			songtosave=self.loadedSongs.GetSelections()[0]
			thesong=self.loadedSongs.GetStrings()[songtosave]
			self.songsavetags(thesong, songtosave, multiples=0)

			self.showArtOfSingleSelectedSong()
			self.songSaveArt(thesong, songtosave, multiples=0)
			if self.artallcheck.IsChecked()==1:
				self.artallcheck.SetValue(False)
		elif len(self.loadedSongs.GetSelections())>1:
			songstosave=self.loadedSongs.GetSelections()
			for songid in songstosave:
				thesong=self.loadedSongs.GetStrings()[songid]
				if songid==self.opentag:
					self.opentagscenterstage()
					self.showArtOfSingleSelectedSong()
				self.songsavetags(thesong, songid, multiples=1)
				self.songSaveArt(thesong, songid, multiples=1)
			if self.artistcheck.IsChecked()==1:
				self.artistcheck.SetValue(False)
			if self.albumartistcheck.IsChecked()==1:
				self.albumartistcheck.SetValue(False)
			if self.discnumbercheck.IsChecked()==1:
				self.discnumbercheck.SetValue(False)
			if self.datecheck.IsChecked()==1:
				self.datecheck.SetValue(False)
			if self.albumcheck.IsChecked()==1:
				self.albumcheck.SetValue(False)
			if self.genrecheck.IsChecked()==1:
				self.genrecheck.SetValue(False)
			if self.composercheck.IsChecked()==1:
				self.composercheck.SetValue(False)
			if self.conductorcheck.IsChecked()==1:
				self.conductorcheck.SetValue(False)
			if self.encodedbycheck.IsChecked()==1:
				self.encodedbycheck.SetValue(False)
			if self.encodersettingscheck.IsChecked()==1:
				self.encodersettingscheck.SetValue(False)
			if self.bpmcheck.IsChecked()==1:
				self.bpmcheck.SetValue(False)
			if self.organizationcheck.IsChecked()==1:
				self.organizationcheck.SetValue(False)
			if self.websitecheck.IsChecked()==1:
				self.websitecheck.SetValue(False)
			if self.copyrightcheck.IsChecked()==1:
				self.copyrightcheck.SetValue(False)
			if self.isrccheck.IsChecked()==1:
				self.isrccheck.SetValue(False)
			if self.versioncheck.IsChecked()==1:
				self.versioncheck.SetValue(False)
			if self.cdinfocheck.IsChecked()==1:
				self.cdinfocheck.SetValue(False)
			if self.lengthcheck.IsChecked()==1:
				self.lengthcheck.SetValue(False)
			if self.commentscheck.IsChecked()==1:
				self.commentscheck.SetValue(False)
			if self.artallcheck.IsChecked()==1:
				self.artallcheck.SetValue(False)

	def RemoveSelectedSongs(self, event):
		#I could take the selection closest to 0, subtract 1, and if that's valid, select it
		if len(self.loadedSongs.GetSelections())==1:
			songtoremove=self.loadedSongs.GetSelections()[0]
			thesong=self.loadedSongs.GetStrings()[songtoremove]
			del self.deletiondict[thesong]
			del self.loadedSongsList[songtoremove]
			self.loadedSongs.Delete(songtoremove)
			if self.opentag==songtoremove:
				self.opentag=-1
				self.cleaners()
			if len(self.loadedSongs.GetStrings())!=1:
				self.cleaners()
				self.loadedSongs.SetSelection(-1)
				#self.onSelect(wx.EVT_LISTBOX)
			del self.tempalbumartstorage[songtoremove]
			del self.tempalbumartmimestorage[songtoremove]
			del self.tempalbumartfilenamestorage[songtoremove]
			self.clearVisibleArt()
				
		elif len(self.loadedSongs.GetSelections())>1:
			songfilenames=list(self.loadedSongs.GetStrings())
			songstoremove=list(self.loadedSongs.GetSelections())
			#sort from latest to earliest in list?
			for songid in reversed(songstoremove):
				self.loadedSongs.Delete(songid)
				#this works. did I bind it to loadedSongsList?
				del self.loadedSongsList[songid]
				del self.deletiondict[songfilenames[songid]]
				#this works. did I bind it to loadedSongsList?
				del self.tempalbumartstorage[songid]
				del self.tempalbumartmimestorage[songid]
				del self.tempalbumartfilenamestorage[songid]
			self.clearVisibleArt()
			#something wrong with self.loadedSongsList?
			#If that, each song gets the next song's tag, and the last song messes things up
			#delete reversed?
			self.cleaners()
			self.loadedSongs.SetSelection(-1)

	def RemoveArt(self, event):
		if len(self.loadedSongs.GetSelections())==1:
			songid3data=self.songIdentifierForArt(self.loadedSongs.GetStrings()[self.loadedSongs.GetSelections()[0]])
			extension=os.path.splitext(self.loadedSongs.GetStrings()[self.loadedSongs.GetSelections()[0]])[1].lower()
			self.deletiondict[self.loadedSongs.GetStrings()[self.loadedSongs.GetSelections()[0]]]=1
			self.tempalbumartstorage[self.loadedSongs.GetSelections()[0]][self.currentarttype]=None
			self.tempalbumartmimestorage[self.loadedSongs.GetSelections()[0]][self.currentarttype]=None
			self.tempalbumartfilenamestorage[self.loadedSongs.GetSelections()[0]][self.currentarttype]=None
			songid3data=self.songDeleteArtGui(songid3data, extension, False)
		else:
			for i in self.loadedSongs.GetSelections():
				songid3data=self.songIdentifierForArt(self.loadedSongs.GetStrings()[i])
				extension=os.path.splitext(self.loadedSongs.GetStrings()[i])[1].lower()
				self.deletiondict[self.loadedSongs.GetStrings()[i]]=1
				self.tempalbumartstorage[i][self.currentarttype]=None
				self.tempalbumartmimestorage[i][self.currentarttype]=None
				self.tempalbumartfilenamestorage[i][self.currentarttype]=None
				songid3data=self.songDeleteArtGui(songid3data, extension, False)
		self.onSelect(wx.EVT_LISTBOX)

	def RemoveAllArt(self, event):
		if len(self.loadedSongs.GetSelections())==1:
			if self.restoreTimeDataCheck.IsChecked():
				timeData=saveFileTimeData(self.loadedSongs.GetStrings()[self.loadedSongs.GetSelections()[0]])
			songid3data=self.songIdentifierForArt(self.loadedSongs.GetStrings()[self.loadedSongs.GetSelections()[0]])
			extension=os.path.splitext(self.loadedSongs.GetStrings()[self.loadedSongs.GetSelections()[0]])[1].lower()
			for i in self.tempalbumartstorage[self.loadedSongs.GetSelections()[0]]:
				self.tempalbumartstorage[self.loadedSongs.GetSelections()[0]][i]=None
				self.tempalbumartmimestorage[self.loadedSongs.GetSelections()[0]][i]=None
				self.tempalbumartfilenamestorage[self.loadedSongs.GetSelections()[0]][i]=None
			songid3data=self.songDeleteArtGui(songid3data, extension, True)
			songid3data.save()
			if self.restoreTimeDataCheck.IsChecked():
				restoreFileTimeData(self.loadedSongs.GetStrings()[self.loadedSongs.GetSelections()[0]], timeData[0], timeData[1])
		else:
			for i in self.loadedSongs.GetSelections():
				if self.restoreTimeDataCheck.IsChecked():
					timeData=saveFileTimeData(self.loadedSongs.GetStrings()[i])
				songid3data=self.songIdentifierForArt(self.loadedSongs.GetStrings()[i])
				extension=os.path.splitext(self.loadedSongs.GetStrings()[i])[1].lower()
				for j in self.tempalbumartstorage[i]:
					self.tempalbumartstorage[i][j]=None
					self.tempalbumartmimestorage[i][j]=None
					if len(self.tempalbumartfilenamestorage[i])>j+1:
						self.tempalbumartfilenamestorage[i][j]=None
				songid3data=self.songDeleteArtGui(songid3data, extension, True)
				songid3data.save()
				if self.restoreTimeDataCheck.IsChecked():
					restoreFileTimeData(self.loadedSongs.GetStrings()[i], timeData[0], timeData[1])
		self.thepic=self.theblank.ConvertToBitmap()
		self.onSelect(wx.EVT_LISTBOX)
		#Can I make this less permanent? so it's applied with Save?
		#And gotta work out the All Checkbox
		#if it's checked and there's nothing in the filename, and nothing in the tempfile, delete
		#when you save a file, if its deletiondict is set to 1, its album art gets deleted


	def ExportTheArt(self, event):
		#export in bulk, make that work?
#		pictoexport=None
		for songtoexportfromIndex in self.loadedSongs.GetSelections():
			songtoexportfrom=self.loadedSongs.GetStrings()[songtoexportfromIndex]#self.loadedSongs.GetStrings():
			#print("Running "+songtoexportfrom)
			exportedpic=self.getArtFromSong(songtoexportfrom, self.currentarttype)
			if exportedpic:
				possiblealbumname=getAlbumFromFilename(songtoexportfrom)
				if not possiblealbumname:
					possiblealbumname=os.path.splitext(os.path.split(songtoexportfrom)[1])[0]
				exportedpic.saveTo(os.path.split(songtoexportfrom)[0], possiblealbumname)

	def ExportAllArtThisSong(self, event):
		#From an individual file!
		for songtoexportfromIndex in self.loadedSongs.GetSelections():
			songtoexportfrom=self.loadedSongs.GetStrings()[songtoexportfromIndex]
			#print("Running "+songtoexportfrom)
			exportedpics=self.getArts(songtoexportfrom)
			possiblealbumname=getAlbumFromFilename(songtoexportfrom)
			if not possiblealbumname:
				possiblealbumname=os.path.splitext(os.path.split(songtoexportfrom)[1])[0]
			for exportedpic in exportedpics:
				if exportedpic:
					exportedpic.saveTo(os.path.split(songtoexportfrom)[0], possiblealbumname)

	def ExportAllArt(self, event):
		#From an individual file?
		#instead of using a counter, base it off the picture type
		#(Album Art) if 3, (Back) if 4, (Leaflet) if 5
		#gotta keep backwards compatibility
		for songtoexportfrom in self.loadedSongs.GetStrings():
			#print("Running "+songtoexportfrom)
			exportedpics=self.getArts(songtoexportfrom)
			#picfilename="albumart"
			possiblealbumname=getAlbumFromFilename(songtoexportfrom)
			if not possiblealbumname:
				possiblealbumname=os.path.splitext(os.path.split(songtoexportfrom)[1])[0]
			for exportedpic in exportedpics:
				if exportedpic:
					exportedpic.saveTo(os.path.split(songtoexportfrom)[0], possiblealbumname)

	def ExportAllArtWithFilenames(self, event):
		for songtoexportfrom in self.loadedSongs.GetStrings():
			#print("Running "+songtoexportfrom)
			exportedpics=self.getArts(songtoexportfrom)
			#picfilename="albumart"
			possiblealbumname=os.path.splitext(os.path.split(songtoexportfrom)[1])[0]
			for exportedpic in exportedpics:
				if exportedpic:
					exportedpic.saveTo(os.path.split(songtoexportfrom)[0], possiblealbumname)

	def ViewTheArt(self, event):
		if self.thepic and len(self.loadedSongs.GetSelections())==1:
			try:
				pictoshow=self.tempalbumartstorage[self.loadedSongs.GetSelections()[0]][self.currentarttype]
				topbarsize=35
				self.artfullview=wx.Frame(self, -1, "Album Art", size=(pictoshow.GetSize()[0],pictoshow.GetSize()[1]+topbarsize) )
				print(self.artfullview.GetWindowBorderSize())
				self.scroll = wx.ScrolledWindow(self.artfullview, -1, size=pictoshow.GetSize())
				width, height = wx.GetDisplaySize()
				xPixels=0
				yPixels=0
				xUnits=0
				yUnits=0
				xScrollRate=0
				yScrollRate=0
				
				#How do I not make the canvas bigger than the image?
				#The number of units could be relative based on the image size?
				"""
				pixelsPerUnitX (int) – Pixels per scroll unit in the horizontal direction.
				pixelsPerUnitY (int) – Pixels per scroll unit in the vertical direction.
				noUnitsX (int) – Number of units in the horizontal direction.
				noUnitsY (int) – Number of units in the vertical direction."""
				if pictoshow.GetSize()[0]>width:
					xPixels=50
					xUnits=int(pictoshow.GetSize()[0]/50)
					xScrollRate=50
				if pictoshow.GetSize()[1]>height:
					yPixels=50
					yUnits=int(pictoshow.GetSize()[1]/50)
					yScrollRate=50
				self.scroll.SetScrollbars(xPixels, yPixels, xUnits, yUnits)
				self.scroll.SetScrollRate(xScrollRate, yScrollRate)
				wx.StaticBitmap(self.scroll, -1, pictoshow)
				self.artfullview.Show(1)

			except:
				print_exc()

	def ReloadSongs(self, arttype):
		def OnReloadSongs(event):
			self.clearVisibleArt()
			self.currentarttype=arttype
			self.deletiondict={}
			for songindex in range(0, len(self.loadedSongs.GetStrings())):
				song=self.loadedSongs.GetStrings()[songindex]
				song=os.path.abspath(song)
				self.deletiondict[song]=0
				try:
					if self.currentarttype not in self.tempalbumartstorage[songindex]:
						pic=self.getArtFromSong(song, self.currentarttype)
						if pic==None:
							self.tempalbumartstorage[songindex][self.currentarttype]=None
						if pic:
							tempalbumartstorage=BytesIO(pic.art)
							self.tempalbumartstorage[songindex][self.currentarttype]=wx.Bitmap(wx.Image(tempalbumartstorage))
							self.tempalbumartmimestorage[songindex][self.currentarttype]=pic.mime
							#Sorry, but if you're not saved, you're out
							self.tempalbumartfilenamestorage[songindex][self.currentarttype]=None
							tempalbumartstorage.close()
						
				except:
					print_exc()
					self.tempalbumartstorage[songindex][self.currentarttype]=None

			if len(self.loadedSongs.GetSelections())<=1:
				self.onSelect(wx.EVT_LISTBOX)
			else:
				self.loadedSongs.Select(-1)
			#print("The length of the art storage is "+str(len(self.tempalbumartstorage)))
		return OnReloadSongs

	def loadUnfriendly(self):
		self.unfriendlyTags.SetValue("")
		if "unfriendly" in self.loadedSongsList[self.opentag]:
			unfriendlyTagsText=""
			#print(self.loadedSongsList[self.opentag]["unfriendly"])
			for unfriendlyTag in self.loadedSongsList[self.opentag]["unfriendly"]:
				unfriendlyTagsText+=unfriendlyTag+": "+listToStringSemicolon(self.loadedSongsList[self.opentag]["unfriendly"][unfriendlyTag])+"\n"
			unfriendlyTagsText=unfriendlyTagsText.strip()
			self.unfriendlyTags.SetValue(unfriendlyTagsText)

	def SaveLyricsToText(self, event):
		for songtoexportfromIndex in self.loadedSongs.GetSelections():
			if len(self.loadedSongsList[songtoexportfromIndex]["lyrics"]):
				songtoexportfrom=self.loadedSongs.GetStrings()[songtoexportfromIndex]#self.loadedSongs.GetStrings():
				lyricsFilename=os.path.splitext(os.path.split(songtoexportfrom)[1])[0]+".txt"
				#make it in the same folder as the song?
				writethistothis(self.loadedSongsList[songtoexportfromIndex]["lyrics"], os.path.join(os.path.split(songtoexportfrom)[0], lyricsFilename))

	def ClearTheSongs(self, event):
		self.loadedSongs.Clear()
		self.loadedSongsList=[]
		self.deletiondict={}
		self.tempalbumartstorage=[]
		self.clearVisibleArt()
		self.cleaners()

	def MenuHandle(self, event):
		id=event.GetId()
		#print(id)
		if id==wx.ID_EDIT:
			findDlg = wx.TextEntryDialog(self, "String to replace?", "Replace String in Tags")
			if findDlg.ShowModal() == wx.ID_OK:
				toFind=findDlg.GetValue()
				if toFind!="":
					replaceDlg = wx.TextEntryDialog(self, "String to replace with?", "Replace String in Tags")
					if replaceDlg.ShowModal() == wx.ID_OK:
						toReplace=replaceDlg.GetValue()
						for songIndex in range(0, len(self.loadedSongsList)):
							for tag in self.loadedSongsList[songIndex]:
								if toFind in self.loadedSongsList[songIndex][tag] and tag!="lyrics":
									self.loadedSongsList[songIndex][tag]=self.loadedSongsList[songIndex][tag].replace(toFind, toReplace)
							if len(self.loadedSongs.GetSelections())<=1:
								self.onSelect(wx.EVT_LISTBOX)
							else:
								self.loadedSongs.Select(-1)
						#then go through all of the tag objects to replace, then reload the songs
					replaceDlg.Destroy()
			findDlg.Destroy()

	def Quitter(self, event):
		dlg=wx.MessageDialog(None, "Are you sure you want to quit?", "Confirm Exit", wx.YES_NO)
		choice=dlg.ShowModal()
		if choice==wx.ID_YES:
			sys.exit()

app = wx.App()
mainframe = wx.Frame(None, -1, "UtaEdit", size = (1024, 800))
# call the derived class
TheWindow(mainframe,-1)
mainframe.Show(1)
app.MainLoop()
