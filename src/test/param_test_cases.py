'''
Created on Aug 19, 2011

@author: tufanoruk
'''

import sys
import unittest
import logging

from kasa import param

    
def _addArgs (commandLine):
    argv = commandLine.split()
    for a in argv:
        sys.argv.append(a)

def _setArgs (commandLine):
    del sys.argv[1:]
    _addArgs (commandLine)
        
class Test_Parameters (unittest.TestCase):
    
    def test_init(self):
        params = param.Parameters()
        self.assertEqual(params.getVersion(), "0.4.1")
        self.assertEqual(params.getArgs(), None)
        self.assertEqual(params.getVerbosity(), logging.ERROR)
        
    def test_getVersion (self):
        params = param.Parameters()
        self.assertEqual(params.getVersion(), "0.4.1")
    
    def test_getVerbosity(self):
        params = param.Parameters()
        self.assertEqual(params.getVerbosity(), logging.ERROR)
    
    def test_getArgs(self):
        params = param.Parameters()
        self.assertEqual(params.getArgs(), None)
              
class Test_ConfigParameters(unittest.TestCase):
    
    def test_init(self):
        params = param.ConfigParameters()
        self.assertEqual(params.getVersion(), "0.4.1")
        self.assertEqual(params.getArgs(), None)
        self.assertEqual(params.getVerbosity(), logging.ERROR)
        
    def test_getVersion (self):
        params = param.ConfigParameters()
        self.assertEqual(params.getVersion(), "0.4.1")
    
    def test_getVerbosity(self):
        params = param.ConfigParameters()
        # default verbosity is ERROR
        self.assertEqual(params.getVerbosity(), logging.ERROR)
        _setArgs("-v DEBUG")
        params.parseArgs()
        self.assertEqual(params.getVerbosity(), logging.DEBUG)
        _setArgs("-v WARNING")
        params.parseArgs()
        self.assertEqual(params.getVerbosity(), logging.WARNING)
        _setArgs("-v CRITICAL")
        params.parseArgs()
        self.assertEqual(params.getVerbosity(), logging.CRITICAL)
        _setArgs("-v DEBUG")
        params.parseArgs()
        self.assertEqual(params.getVerbosity(), logging.DEBUG)
    
    def test_getArgs(self):
        params = param.ConfigParameters()
        self.assertEqual(params.getArgs(), None)
        
    def test_parseArgs(self):
        params = param.ConfigParameters()
        _setArgs("-v ERROR")
        params.parseArgs()
        self.assertEqual(params.getVerbosity(), logging.ERROR)
        self.assertEqual(params.getArgs().confFile[0], params._resDir+"/config")
        _setArgs("-o outfile")
        params.parseArgs()
        self.assertEqual(params.getArgs().confFile[0], "outfile")
        _setArgs("--out-file another-outfile")
        params.parseArgs()
        self.assertEqual(params.getArgs().confFile[0], "another-outfile")
           
    
class Test_StoreParameters(unittest.TestCase):
    
    def setUp(self):
        _setArgs("-s sourceuri -d destinationuri")
    
    def test_init(self):
        params = param.StoreParameters()
        self.assertEqual(params.getVersion(), "0.4.1")
        self.assertEqual(params.getArgs(), None)
        self.assertEqual(params.getVerbosity(), logging.ERROR)
        
    def test_getVersion (self):
        params = param.StoreParameters()
        self.assertEqual(params.getVersion(), "0.4.1")
    
    def test_getVerbosity(self):
        params = param.StoreParameters()
        self.assertEqual(params.getVerbosity(), logging.ERROR)
        _addArgs("-v DEBUG")
        params.parseArgs()
        self.assertEqual(params.getVerbosity(), logging.DEBUG)
        _addArgs("-v WARNING")
        params.parseArgs()
        self.assertEqual(params.getVerbosity(), logging.WARNING)
        _addArgs("-v CRITICAL")
        params.parseArgs()
        self.assertEqual(params.getVerbosity(), logging.CRITICAL)
        _addArgs("-v DEBUG")
        params.parseArgs()
        self.assertEqual(params.getVerbosity(), logging.DEBUG)
    
    def test_getArgs(self):
        params = param.StoreParameters()
        self.assertEqual(params.getArgs(), None)
        
    def test_parseArgs(self):
        params = param.StoreParameters()
        
        _addArgs("-v ERROR")
        params.parseArgs()
        self.assertEqual(params.getVerbosity(), logging.ERROR)
        self.assertEqual(params.getArgs().confFile[0], params._resDir+"/config")
        _addArgs("-s sourcepath")
        params.parseArgs()
        self.assertEqual(params.getArgs().srcURI[0], "sourcepath")
        _addArgs("--source-URI file:///longsourceuri")
        params.parseArgs()
        self.assertEqual(params.getArgs().srcURI[0], "file:///longsourceuri")

        _addArgs("-d destinationURI")
        params.parseArgs()
        self.assertEqual(params.getArgs().dstURI[0], "destinationURI")
        _addArgs("--destination-URI longdestinationURI")
        params.parseArgs()
        self.assertEqual(params.getArgs().dstURI[0], "longdestinationURI")

        _addArgs("-l")
        params.parseArgs()
        self.assertTrue(params.getArgs().list)
        
        _addArgs("--reset")
        params.parseArgs()
        self.assertTrue(params.getArgs().reset)

