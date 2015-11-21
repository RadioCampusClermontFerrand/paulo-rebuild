#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paulo
import getopt
import sys
import os.path


def usage():
    print "Missing parameters..."

def main(argv):
    csvFile=""
    inputDir=""
    outputDir=""
    interactiveThresold=None

    try:                                
        opts, args = getopt.getopt(argv, "hc:i:o:I:", ["help", "csv=", "input-dir=", "output-dir=", "interactive="])
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
            
    if csvFile == "":
        print "No csv file. Abort"
        return
    if inputDir == "":
        print "No input dir. Abort"
        return
    if outputDir == "":
        print "No output dir. Abort"
        return
    
    entries = paulo.charger_entries(csvFile, outputDir)
    print len(entries), "entrées chargées"

    mp3files = paulo.charger_mp3(inputDir)
    print len(mp3files), "mp3"

    matchCount=0
    autoMovedCount=0
    manualMovedCount=0
    result = {}
    for entry in entries:
        bestScore = interactiveThresold if interactiveThresold != None else 0.6
        for mp3file in mp3files:
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
                        print "Cancel copy"
                    

    print "Match number:", matchCount, "including: "
    print "\tAutomatic copies:", autoMovedCount
    print "\tManual copies:", manualMovedCount

if __name__ == "__main__":
    main(sys.argv[1:])
