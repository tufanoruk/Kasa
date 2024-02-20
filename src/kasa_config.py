#!/usr/bin/env python2.7

'''
Created on Aug 24, 2011

@author: tufan
'''

__version__ = "$Revision: 00f8e3bb1197 $"
# $Source$

import sys
import os

import kasa.error
import kasa.param
import kasa.util
import kasa.log
import kasa.cfile

# top level program log
plog = kasa.log.getDefaultLogger()

params = kasa.param.ConfigParameters()

try:
    params.parseArgs()
    
    plog.debug("Use configuration from " + params.getArgs().confFile[0])

    # open / create config file
    config = kasa.cfile.Configuration(params.getArgs().confFile[0])    
    config.open()
    plog.setLevel(config.getDebug()) # get / set default debug level from configuration
    
    # if debug level is provided as parameter override it
    if params.getVerbosity():
        plog.setLevel(params.getVerbosity())
    
    # --- key
    validFile = False
    fhash = config.getCryptKey()
    changeKey = "N"
    if (fhash != None and len(fhash) > 0):
        print '''
    WARNING: There is already a crypt key defined!
             Changing the key will result failure to decrypt 
             the files encrypted with the existing key.
             '''
        changeKey = raw_input("Are you sure to change the encryption key [y:N]: ")
    else:
        changeKey = "Y"
    
    while ((not validFile) and (changeKey.upper() == "Y")):
        print '''
To have a strong encryption, key is calculated from a non-empty file.
User will not need to enter the key to encrypt / decrpyt the files while using kasa utilities.
'''
        keyF = os.path.abspath(os.path.expanduser(raw_input("Enter a file path to create a key: ")))
        if (os.access(keyF, os.R_OK) and os.path.getsize(keyF) > 1024):
            fhash = kasa.util.hashFile(keyF)
            config.setCryptKey(fhash)            
            validFile = True
        else:
            print "'", keyF, "' is not a valid file. Either non exist or readable, or file size is too small!"
            
    plog.debug ("Key that will be used for encryption : " + 
                str([hex(ord(c)) for c in list(config.getCryptKey())]))
    
    # --- S3 code  
    validS3code = False
    S3code = config.getS3Code()
    while(not validS3code):
        try:        
            S3code = raw_input("Enter your AmazonS3 Code: ")
            config.setS3Code(S3code)
            validS3code = True
        except kasa.error.KasaS3CodeException:
            print "Invalid S3 Code. S3 code must be at least 20 characters long"
            continue
        
    plog.debug ("Amazon S3 code : " + config.getS3Code())       
    
    # --- S3 key    
    validS3Key = False
    S3key = config.getS3Key()
    while(not validS3Key):
        try:
            S3key = raw_input("Enter your Amazon S3 Key: ")
            config.setS3Key(S3key)
            validS3Key = True
        except kasa.error.KasaS3KeyException:
            print "Invalid S3 Key. S3 key must be at least 20 characters long"
            continue
            
    plog.debug("Amazon S3 key : " + config.getS3Key())
    
    # feedback parameters and ask for approval
    
    print "Configuration parameters that will be set are below"
    print "---------------------------------------------------"
    print "Encryption key : ", " ".join([hex(ord(c)) for c in list(config.getCryptKey())])
    print "Amazon S3 Code : ", config.getS3Code()
    print "Amazon S3 Key  : ", config.getS3Key() 

    cmd = raw_input ("If these values are correct then type 's' to save : ")
    if (cmd.upper() == "S"):
        try:
            config.save()
            print "Configuration parameters are saved."
        except kasa.error.KasaFileException:
            print "Cannot save configuration!"
            plog.error("Parameters cannot be saved to configuration file " + config.getName())           
    else:
        print "\n\nConfiguration parameters are NOT saved." 
        print "Exiting without changing the existing configuration."
        
    # if approved save config file
    
except kasa.error.KasaException as e:
    plog.error ("ERROR. Terminating!" + e.getMessage())    
except SystemExit:
    pass
except:
    instance = sys.exc_info()
    plog.error ("ERROR. Terminating!" + str(instance))
         
plog.debug("done")
print "Done!"
