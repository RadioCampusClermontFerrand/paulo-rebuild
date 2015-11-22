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

def loadEntries(csvFile, outputDir, allEntries = False, msg = True):
    result = []
    nbempty=0
    with open(csvFile, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if not allEntries and os.path.isfile(outputDir + "/" + row[0] + "/" + row[1]):
                continue
            if not allEntries and row[1] == "":
                nbempty += 1
                continue
            result.append(PauloEntry(*row))
    if msg:
        print "  Empty target entries: ", nbempty 
    return result

  
def loadMP3(inputDir):
    result = []
    for root, dirs, files in os.walk(inputDir):
        for f in files:
            if f.endswith(".mp3"): # or f.endswith(".wav"):
                result.append(MediaFile(root + "/" + f, inputDir))
                #if len(result) == 200:
                    #return result
    return result


class InvalidMatchings:
    def __init__(self, filename):
        self.answers = {}
        if os.path.isfile(filename):
            with open(filename, 'rb') as filename:
                reader = csv.reader(filename, delimiter=',', quotechar='"')
                for row in reader:
                    self.addEntry(row[0], row[1])
                

    def save(self, filename):
        if filename != "":
            with open(filename, 'w') as f:
                for entries in self.answers:
                    for elements in self.answers[entries]:
                        f.write("\"" + entries.replace('"', '\\"') + "\",\"" + elements.replace('"', '\\"') + "\"\n")
    
    def addEntry(self, element1, element2):
        if self.answers.get(element1) == None:
            self.answers[element1] = []
        self.answers[element1].append(element2)
    
    def hasEntry(self, element1, element2):
        return self.answers.get(element1) != None and element2 in self.answers[element1]
    
    def getNbAnswers(self):
        nb = 0
        for a in self.answers:
            nb += len(self.answers[a])
        return nb
          

class RawAudioMetaData:
    def __init__(self, string=""):
        self.string = string
    def __str__(self):
        return self.string
            

class AudioMetaData:
    def __init__(self, title=None, album=None, artist=None):
        self.title = title
        self.album = album
        self.artist = artist

    def similaritySingleString(self, string):
        return (5 * self.similarityString(self.title, string, True) + \
                    self.similarityString(self.album, string, True) + \
                    4 * self.similarityString(self.artist, string, True)) / 10

    def similarity(self, otherTitle):
        try:
            self.similaritySingleString(otherTitle.string)
        except AttributeError:
            return (5 * self.symSimilarityString(self.title, otherTitle.title) + \
                    self.symSimilarityString(self.album, otherTitle.album) + \
                    4 * self.symSimilarityString(self.artist, otherTitle.artist)) / 10

    def symSimilarityString(self, pattern, string):
        return (self.similarityString(pattern, string) + self.similarityString(string, pattern)) / 2

    def similarityString(self, pattern, string, quick = False):
        if pattern is None and string is None:
            return 0.5
        elif pattern is None or string is None:
            return 0
        else:
            queryMatcher = difflib.SequenceMatcher(None, pattern.lower(), string.lower())
            if quick:
                return queryMatcher.quick_ratio()
            else:
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

    def getID(self):
        return self.getTargetFile()


class MediaFile:
    def __init__(self, filename, inputDir):
        self.filename = filename
        self.metadatas = []
        self.metadatas.append(self.loadMetadata())
        self.metadatas.append(self.estimateMetadataFromFileName(inputDir))
        
    def loadMetadata(self):
        try:
            desc = mutagen.File(self.filename)
            title = str(desc.get("TIT2"))
            album = str(desc.get("TALB"))
            artist = str(desc.get("TPE1"))
            return AudioMetaData(title, album, artist)
        except:
            return AudioMetaData()
    
    def estimateMetadataFromFileName(self, inputDir):
        if self.filename.startswith(inputDir):
            suffix = self.filename[len(inputDir):]
        else:
            suffix = self.filename
        return RawAudioMetaData(suffix)
    
    def getMetaDatas(self):
        return self.metadatas

    def getID(self):
        return self.filename

    def __str__(self):
        return self.filename + "\n" + str(self.metadatas[0])

