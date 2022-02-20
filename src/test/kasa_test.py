#!/usr/bin/env python

'''
Created on Aug 25, 2011

@author: tufan
'''

import unittest

from param_test_cases import Test_Parameters, Test_ConfigParameters, Test_StoreParameters   
from util_test_cases import Test_util
from cfile_test_cases import Test_Configuration
from fhash_test_cases import Test_FileHash 
from storage_test_cases import Test_StorageFactory

#@todo: add other module test case modules here

tests = []
tests.append(unittest.TestLoader().loadTestsFromTestCase(Test_Parameters))
tests.append(unittest.TestLoader().loadTestsFromTestCase(Test_ConfigParameters))
tests.append(unittest.TestLoader().loadTestsFromTestCase(Test_StoreParameters))
tests.append(unittest.TestLoader().loadTestsFromTestCase(Test_util))
tests.append(unittest.TestLoader().loadTestsFromTestCase(Test_Configuration))
tests.append(unittest.TestLoader().loadTestsFromTestCase(Test_FileHash))
tests.append(unittest.TestLoader().loadTestsFromTestCase(Test_StorageFactory))
#@todo: load more tests cases here

suite = unittest.TestSuite(tests)
runner = unittest.TextTestRunner(verbosity=0)

runner.run(suite)
    