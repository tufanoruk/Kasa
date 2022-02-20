'''
Created on Sep 13, 2011

@author: tufanoruk
'''
import unittest
from kasa import error
from kasa import cfile

_testCFile = "./kasaTestFile.dat"

class Test_Configuration(unittest.TestCase):

    def test_open(self):
        cf = cfile.Configuration(_testCFile)
        # open / create non existing config file
        self.assertRaises(error.KasaFileException, cf.open())
        # open existing config file
        pass
        # open existing wrong permission config file
        
    
    def test_close(self):
        pass
    
    def test_save(self):
        pass
    
    def test_sgetCryptKey(self):
        pass
    
    def test_sgetS3Code(self):
        pass
    
    def test_sgetS3Key(self):
        pass

    def test_sgetDebug(self):
        pass

#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()