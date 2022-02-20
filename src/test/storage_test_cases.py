'''
Created on Sep 13, 2011

@author: tufanoruk
'''

import sys
import os
import unittest

from kasa import cfile
from kasa import param
from kasa import fhash
from kasa import storage


_testCFile = "./kasaTestFile.dat"

class Test_StorageFactory(unittest.TestCase):

    def test_getStorage(self):
                
        fileuri = "file://"+os.getcwd()
        s3uri = "s3:///bucket/to/file"

        argv = " -s " + fileuri + " -d " + s3uri
        del sys.argv[1:]
        for a in argv.split():
            sys.argv.append(a)
        
        params = param.StoreParameters()        
        params.parseArgs()
        config = cfile.Configuration(params.getArgs().confFile[0])
        fileHash = fhash.FileHash(params.getResDir()) 
        
        storageFactory = storage.StorageFactory(config, fileHash) 
        
        store, unused_iterator = storageFactory.getStorage(fileuri)        
        self.assertTrue(store.getScheme() == "file")
        
        store, unused_iterator = storageFactory.getStorage(s3uri)
        self.assertTrue(store.getScheme() == "s3")


#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()