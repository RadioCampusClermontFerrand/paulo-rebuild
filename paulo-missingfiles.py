#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paulo
import getopt
import sys
import os.path

def usage():
    print "Example: "
    print "./paulo-missingfiles.py -c backup-titres.csv -d /mnt/paulo/home/sound/ -u \"pgms,interview,interview 2,interview 3\""

def main(argv):
    csvFile=""
    dir=""
    unwantedList = []

    try:                                
        opts, args = getopt.getopt(argv, "hc:d:u:", ["help", "csv=", "dir=", "unwanted-list="])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)      
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit()                  
        elif opt in ("-c", "--csv"): 
            csvFile = arg
        elif opt in ("-d", "--dir"): 
            dir = arg
        elif opt in ("-u", "--unwanted-list"):
            unwantedList = arg.split(",")

            
    if csvFile == "":
        print "No csv file. Abort"
        return
    if dir == "":
        print "No input dir. Abort"
        return
    
    
    entries = paulo.loadEntries(csvFile, dir, False)
    
    filteredEntries = []
    for entry in entries:
        if not entry.bande in unwantedList:
            filteredEntries.append(entry)
            
    
    for entry in filteredEntries:
        print entry.toCSVLine()


if __name__ == "__main__":
    main(sys.argv[1:])
