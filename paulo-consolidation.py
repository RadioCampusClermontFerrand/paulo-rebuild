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
    print "Usage: paulo-consolidation.py [options]"
    print "Required ptions:"
    print "  -c, --csv  FILENAME         The input CSV file"
    print "  -i, --input-dir DIR         A directory with mp3 files"
    print "  -o, --output-dir DIR        A directory where the files will be stored"
    print "  -I, --interactive THRESHOLD The score threshold from when the user will be asked if the match is correct or not"
    print "  -n, --negative-answers      A file where are stored the previous negative answers of the interative mode (will not be asked again)"
    print ""
    print "Supplementary options:"
    print "  -h, --help           This message"
    print "  -s, --similarity     Use file names to detect similarities"
    
def main(argv):
    csvFile=""
    inputDir=""
    outputDir=""
    interactiveThresold=None
    negativeAnswersFile=""
    similarity=False

    try:                                
        opts, args = getopt.getopt(argv, "hc:i:o:I:n:s", ["help", "csv=", "input-dir=", "output-dir=", "interactive=", "negative-answers=", "similarity"])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)      
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit()  
        elif opt in ("-s", "--similarity"):
            similarity = True
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

    mp3files = paulo.loadMP3(inputDir, similarity)
    print " ", len(mp3files), "mp3"
    
    negativeAnswers = paulo.InvalidMatchings(negativeAnswersFile)
    print " ", negativeAnswers.getNbAnswers(), "existing negative answers"

    matchCount=0
    autoMovedCount=0
    manualMovedCount=0
    result = {}
    log = []
    nbEntry=0
    for entry in entries:
        print "Processing entry", nbEntry, "/", len(entries)
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
            if bestScore > 0.9:
                autoMovedCount += 1
                print "Automatic copy (" + str(bestScore) + "): " + outputDir + "/" + entry.getTargetFile() + " from " + result[entry][1].filename 
                paulo.copy(outputDir + "/" + entry.getTargetFile(), result[entry][1].filename)
                paulo.setTags(outputDir + "/" + entry.getTargetFile(), entry)
                log.append(entry.toCSVLine())
            else:
                if interactiveThresold != None:
                    print "Score: " + str(bestScore) + "\n" + str(entry) + "\n" +  str(result[entry][1])
                    if paulo.prompt("Do you want to copy this file?"):
                        print "Manual copy: " + outputDir + "/" + entry.getTargetFile()
                        paulo.copy(outputDir + "/" + entry.getTargetFile(), result[entry][1].filename)
                        paulo.setTags(outputDir + "/" + entry.getTargetFile(), entry)
                        log.append(entry.toCSVLine())
                        manualMovedCount += 1
                    else:               
                        negativeAnswers.addEntry(entry.getID(), result[entry][1].getID())
                        negativeAnswers.save(negativeAnswersFile)
                        print "Cancel copy"
                    
    paulo.add2CSVLog(log, outputDir)

    print "Match number:", matchCount, "including: "
    print "\tAutomatic copies:", autoMovedCount
    print "\tManual copies:", manualMovedCount

if __name__ == "__main__":
    main(sys.argv[1:])
