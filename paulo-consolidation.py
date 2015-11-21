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
    try:                                
        opts, args = getopt.getopt(argv, "hc:i:o:", ["help", "csv=", "input-dir=", "output-dir="])
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

    nbgood=0
    moved=0
    movedManual=0
    result = {}
    for entry in entries:
        bestScore = 0
        for mp3file in mp3files:
            e_meta = entry.getMetaData()
            es_mp3file = mp3file.getMetaDatas()
            for e_mp3file in es_mp3file:
                score = e_meta.similarity(e_mp3file)
                if score > bestScore:
                    result[entry] = [score, mp3file]
                    bestScore = score
        if entry in result:
            nbgood += 1
            if bestScore > 0.7:
                moved += 1
                print "Automatic copy (" + str(bestScore) + "): " + outputDir + "/" + entry.getTargetFile() + " from " + result[entry][1].filename 
                paulo.copy(outputDir + "/" + entry.getTargetFile(), result[entry][1].filename)
            else:
                print "Score: " + str(bestScore) + "\n" + str(entry) + "\n" +  str(result[entry][1])
                #if paulo.prompt("Do you want to copy this file?"):
                    #print "Manual copy: " + outputDir + "/" + entry.getTargetFile()
                    #paulo.copy(outputDir + "/" + entry.getTargetFile(), result[entry][1].filename)
                    #movedManual += 1
                #else:
                    #print "Cancel copy"
                    

    print "Match number:", nbgood, "including: "
    print "\tAutomatic copies:", moved
    print "\tManual copies:", movedManual

if __name__ == "__main__":
    main(sys.argv[1:])
