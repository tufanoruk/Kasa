#!/usr/bin/env python

'''
Created on Sep 14, 2011

@author: tufan
'''
__version__ = "$Revision: 00f8e3bb1197 $"

import sys
import codecs

import kasa.error
import kasa.param
import kasa.util
import kasa.log
import kasa.cfile
import kasa.fhash
import kasa.storage

# set stdout and stderr to utf-8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

# top level program log
plog = kasa.log.getDefaultLogger()

params = kasa.param.StoreParameters()

fileCount = 0
srcStorage = None
dstStorage = None

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
        
    fileHash = kasa.fhash.FileHash(params.getResDir())
    
    storageFactory = kasa.storage.StorageFactory(config, fileHash)

    dstStorage, dstStorageIterator = storageFactory.getStorage(params.getArgs().dstURI[0])
    srcStorage, srcStorageIterator = storageFactory.getStorage(params.getArgs().srcURI[0]) 
 
    kasa.util.checkStorageValidity (srcStorage.getURI()) 
    kasa.util.checkStorageValidity (dstStorage.getURI()) 
    
    if dstStorage.getURI().find(srcStorage.getURI()) == 0:
        print "Destination directory cannot be the same or within the source directory"
        raise SystemExit
        
    # to forcefully storage files under fromDir, clear their hash from the file hash bookkeeper 
    if params.getArgs().reset:
        fileHash.delete(srcStorage.getPath())
    
    dryRun = params.getArgs().list
    
    for theFile, intoSubdir in srcStorageIterator.nextFile():
        if params.getArgs().restore:
            if dstStorage.restore(theFile, intoSubdir,dryRun):
                fileCount += 1
        else:
            if dstStorage.store(theFile, intoSubdir,dryRun):
                fileCount += 1
        
    if params.getArgs().list:
        print fileCount,"files will be (re)stored!"
    else:
        print fileCount,"files has (re)stored!"
         
except kasa.error.KasaException as e:
    plog.error ("ERROR. Terminating!" + e.getMessage())    
except SystemExit:
    pass 
except:
    instance = sys.exc_info()
    plog.error ("ERROR. Terminating!" + str(instance))

if srcStorage:
    srcStorage.close()
    
if dstStorage:    
    dstStorage.close()

plog.debug("done")




