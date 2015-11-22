#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paulo
import getopt
import sys
import os.path

# usage: 
# export PYTHONUNBUFFERED=1
# ./paulo-consolidation.py -c backup-titres.csv -i /media/jm/Elements/backup/musique/ -o /mnt/paulo/home/sound/ -I 0.4 | tee -a log-copy.txt

def usage():
    print "Missing parameters..."

def main(argv):
    csvFile=""
    inputDir=""
    outputDir=""
    interactiveThresold=None
    negativeAnswersFile=""

    try:                                
        opts, args = getopt.getopt(argv, "hc:i:o:I:n:", ["help", "csv=", "input-dir=", "output-dir=", "interactive=", "negative-answers="])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)      
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit()                  
        elif opt in ("-c", "--csv"): 
            csvFile = arg
        elif opt in ("-i", "--input-dir"): 
            inputDir = arg
        elif opt in ("-o", "--output-dir"): 
            outputDir = arg
        elif opt in ("-I", "--interactive"):
            interactiveThresold = float(arg)
        elif opt in ("-n", "--negative-answers="):
            negativeAnswersFile = arg
            
    if csvFile == "":
        print "No csv file. Abort"
        return
    if inputDir == "":
        print "No input dir. Abort"
        return
    if outputDir == "":
        print "No output dir. Abort"
        return
    
    entries = paulo.loadEntries(csvFile, outputDir)
    print " ", len(entries), "loaded entries"

    mp3files = paulo.loadMP3(inputDir)
    print " ", len(mp3files), "mp3"
    
    negativeAnswers = paulo.InvalidMatchings(negativeAnswersFile)
    print " ", negativeAnswers.getNbAnswers(), "existing negative answers"

    matchCount=0
    autoMovedCount=0
    manualMovedCount=0
    result = {}
    nbEntry=0
    for entry in entries:
        print "Processing entry", nbEntry
        nbEntry += 1
        bestScore = interactiveThresold if interactiveThresold != None else 0.6
        for mp3file in mp3files:
            if not negativeAnswers.hasEntry(entry.getID(), mp3file.getID()):
                e_meta = entry.getMetaData()
                es_mp3file = mp3file.getMetaDatas()
                for e_mp3file in es_mp3file:                
                    score = e_meta.similarity(e_mp3file)
                    if score > bestScore:
                        result[entry] = [score, mp3file]
                        bestScore = score
        if entry in result:
            matchCount += 1
            if bestScore > 0.7:
                autoMovedCount += 1
                print "Automatic copy (" + str(bestScore) + "): " + outputDir + "/" + entry.getTargetFile() + " from " + result[entry][1].filename 
                paulo.copy(outputDir + "/" + entry.getTargetFile(), result[entry][1].filename)
            else:
                if interactiveThresold != None:
                    print "Score: " + str(bestScore) + "\n" + str(entry) + "\n" +  str(result[entry][1])
                    if paulo.prompt("Do you want to copy this file?"):
                        print "Manual copy: " + outputDir + "/" + entry.getTargetFile()
                        paulo.copy(outputDir + "/" + entry.getTargetFile(), result[entry][1].filename)
                        manualMovedCount += 1
                    else:               
                        negativeAnswers.addEntry(entry.getID(), result[entry][1].getID())
                        negativeAnswers.save(negativeAnswersFile)
                        print "Cancel copy"
                    

    print "Match number:", matchCount, "including: "
    print "\tAutomatic copies:", autoMovedCount
    print "\tManual copies:", manualMovedCount

if __name__ == "__main__":
    main(sys.argv[1:])
