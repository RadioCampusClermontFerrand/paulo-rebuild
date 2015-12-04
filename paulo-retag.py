#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paulo
import getopt
import sys
import os.path

# usage: 
# export PYTHONUNBUFFERED=1
# ./paulo-retag.py -c backup-titres.csv -o /mnt/paulo/home/sound/

def usage():
    print "Usage: paulo-retag.py [options]"
    print "Required ptions:"
    print "  -c, --csv  FILENAME         The input CSV file"
    print "  -o, --output-dir DIR        A directory where the files will be stored"
    print ""
    print "Supplementary options:"
    print "  -h, --help           This message"
    
def main(argv):
    csvFile=""
    outputDir=""

    try:                                
        opts, args = getopt.getopt(argv, "hc:o:", ["help", "csv=", "output-dir="])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)      
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit()  
        elif opt in ("-c", "--csv"): 
            csvFile = arg
        elif opt in ("-o", "--output-dir"): 
            outputDir = arg
            
    if csvFile == "":
        print "No csv file. Abort"
        return
    if outputDir == "":
        print "No output dir. Abort"
        return
    
    entries = paulo.loadEntries(csvFile, outputDir, True)
    print " ", len(entries), "loaded entries"

    print "Set tags"
    for entry in entries:
        if os.path.isfile(outputDir + "/" + entry.getTargetFile()):
            paulo.setTags(outputDir + "/" + entry.getTargetFile(), entry)
            

if __name__ == "__main__":
    main(sys.argv[1:])
