#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paulo
import getopt
import sys
import os.path

def usage():
    print "Example: "
    print "./paulo-updatedb.py -c backup-titres.csv -d /mnt/paulo/home/sound/"

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
    
    
    entries = paulo.loadEntries(csvFile, dir, True, False)

    for entry in entries:
        if os.path.isfile(dir + "/" + entry.getTargetFile()):
            print "UPDATE t_titre SET tit_file = \"" + entry.mp3file.replace('"', '\\"') + "\" WHERE tit_code = " + str(entry.idFile) + ";";
        else:
            print "UPDATE t_titre SET tit_file = \"\" WHERE tit_code = " + str(entry.idFile) + ";";


if __name__ == "__main__":
    main(sys.argv[1:])
