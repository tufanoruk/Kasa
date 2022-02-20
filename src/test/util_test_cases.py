'''
Created on Sep 13, 2011

@author: tufanoruk
'''
import os
import stat
import unittest
from Crypto.Hash import MD5

from kasa import util

_testFileName = "./kasaTestFile.dat"
_permUserOnlyRW = stat.S_IRUSR | stat.S_IWUSR
_permUserGroupRW = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP

class Test_util(unittest.TestCase):


    def test_hashFile(self):
        msg2Digest = "This is an md5 test file"
        with open (_testFileName,"wb") as fd: # create file
            fd.write(msg2Digest)
        md5 = MD5.new ()
        md5.update(msg2Digest)
        self.assertEqual(md5.hexdigest(), util.hashFile(_testFileName))
        os.unlink(_testFileName)
    
    def test_toHex(self):
        pass
    
    def test_toStr(self):
        pass
    
    def test_makeOwnerOnly(self):
        with open (_testFileName,"wb"): # create file
            pass
        util.makeOwnerOnly(_testFileName)
        self.assertTrue(util.isOwnerOnly(_testFileName))
        os.unlink(_testFileName)
    
    def test_isOwnerOnly(self):
        with open (_testFileName,"wb"): # create file
            pass
        os.chmod(_testFileName,  _permUserOnlyRW)
        self.assertTrue(util.isOwnerOnly(_testFileName))
        os.chmod(_testFileName,  _permUserGroupRW)                    
        self.assertFalse(util.isOwnerOnly(_testFileName))
        os.unlink(_testFileName)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()