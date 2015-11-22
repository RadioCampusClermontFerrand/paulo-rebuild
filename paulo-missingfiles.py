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
    dir=""

    try:                                
        opts, args = getopt.getopt(argv, "hc:d:", ["help", "csv=", "dir="])
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
            
    if csvFile == "":
        print "No csv file. Abort"
        return
    if dir == "":
        print "No input dir. Abort"
        return
    
    entries = paulo.loadEntries(csvFile, dir, False)
    
    for entry in entries:
        print entry.toCSVLine()


if __name__ == "__main__":
    main(sys.argv[1:])
