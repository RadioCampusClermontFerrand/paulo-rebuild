# -*- coding: utf-8 -*-

import csv
import re
import os
import difflib
import mutagen
import os.path
import shutil
import distutils.util
import sys

def prompt(query):
   sys.stdout.write('%s [y/N]: ' % query)
   val = raw_input()
   try:
       ret = val != "" and distutils.util.strtobool(val)
   except ValueError:
       sys.stdout.write('Please answer with a y/n\n')
       return prompt(query)
   return ret

def copy(target, source):
    if not os.path.exists(os.path.dirname(target)):
        os.makedirs(os.path.dirname(target))
    shutil.copyfile(source, target)

def charger_entries(csvFile, outputDir):
    result = []
    nbempty=0
    with open(csvFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if os.path.isfile(outputDir + "/" + row[0] + "/" + row[1]):
                continue
            if row[1] == "":
                nbempty += 1
                continue
            result.append(PauloEntry(*row))
    print "Fichiers destination vides: ", nbempty 
    return result
        
def charger_mp3(inputDir):
    result = []
    for root, dirs, files in os.walk(inputDir):
        for f in files:
            if f.endswith(".mp3"): # or f.endswith(".wav"):
                result.append(MediaFile(root + "/" + f))
                #if len(result) == 200:
                    #return result
    return result
        
        
class AudioMetaData:
    def __init__(self, title=None, album=None, artist=None):
        self.title = title
        self.album = album
        self.artist = artist

    def similarity(self, otherTitle):
        return (5 * self.symSimilarityString(self.title, otherTitle.title) + \
                self.symSimilarityString(self.album, otherTitle.album) + \
                4 * self.symSimilarityString(self.artist, otherTitle.artist)) / 10

    def symSimilarityString(self, pattern, string):
        return (self.similarityString(pattern, string) + self.similarityString(string, pattern)) / 2

    def similarityString(self, pattern, string):
        if pattern is None and string is None:
            return 0.5
        elif pattern is None or string is None:
            return 0
        else:
            queryMatcher = difflib.SequenceMatcher(None, pattern.lower(), string.lower())
            return queryMatcher.ratio()

    def __str__(self):
        return "\tArtist: " + str(self.artist) + "\n\tTitle: " + str(self.title) + "\n\tAlbum: " + str(self.album)

def nonify(string):
    string = None if string == "\\N" else string
    return string

class PauloEntry:
    def __init__(self, bande="", mp3file="", title="", album="", artist="", style="", idFile=0):
        self.metadata = AudioMetaData(nonify(title), nonify(album), nonify(artist))
        self.bande = bande
        self.mp3file = mp3file
        self.style = style
        self.idFile = idFile
        
    def getStartFileName(self):
        m = re.match(r"(?P<prefix>.*)_\d+.mp3", self.mp3file)
        if m:
            return m.group('prefix')
        else:
            return ""
    def getMetaData(self):
        return self.metadata
    def __str__(self):
        return self.mp3file + "\n" + str(self.metadata)
    def getTargetFile(self):
        return self.bande + "/" + self.mp3file
    def toCSVLine(self):
        return self.toCSVElem(self.bande) + "," + self.toCSVElem(self.mp3file) + "," + self.toCSVElem(self.metadata.title) + \
            "," + self.toCSVElem(self.metadata.album) + "," + self.toCSVElem(self.metadata.artist) + "," + self.toCSVElem(self.style) + "," + self.toCSVElem(self.idFile)
    def toCSVElem(self, string):
        return "\""+str(string)+"\""


class MediaFile:
    def __init__(self, filename):
        self.filename = filename
        self.metadatas = []
        self.metadatas.append(self.loadMetadata())
        #self.metadatas.append(self.estimateMetadataFromFileName())
        
    def loadMetadata(self):
        try:
            desc = mutagen.File(self.filename)
            title = str(desc.get("TIT2"))
            album = str(desc.get("TALB"))
            artist = str(desc.get("TPE1"))
            return AudioMetaData(title, album, artist)
        except:
            return AudioMetaData()
    
    def estimateMetadataFromFileName(self):
        # TODO
        return AudioMetaData()
    
    def getMetaDatas(self):
        return self.metadatas

    def __str__(self):
        return self.filename + "\n" + str(self.metadatas[0])

