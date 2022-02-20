'''
Created on Sep 13, 2011

@author: tufanoruk
'''

import os
import unittest
import logging
import sqlite3
import datetime
from string import Template

from kasa import util
from kasa import fhash

class Test_FileHash(unittest.TestCase):

    def setUp(self):
        self._resDir = os.getcwd() 
        self._db = sqlite3.Connection(self._resDir + os.sep + fhash.FileHash._dbname,
                                      detect_types = sqlite3.PARSE_COLNAMES|sqlite3.PARSE_DECLTYPES,
                                      isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._db.text_factory = str
        
        self._cur = self._db.cursor()
    
        try:
            ''' this must be teh same as defined in FileHash
            '''
            createStr = Template ('''create table ${tblname} (fname text not null unique, 
                                                              fhash text primary key, 
                                                              updated timestamp)''')
            self._db.execute (createStr.substitute(tblname=fhash.FileHash._tblname))
            
            replaceStr = Template ("replace into ${tblname} values (?,?,?)")
            for d in os.walk("."):
                for f in d[2]:
                    fname = os.path.abspath(d[0])+os.sep+f                 
                    hash = util.hashFile(fname)
                    self._cur.execute (replaceStr.substitute(tblname=fhash.FileHash._tblname),
                                 (fname, hash, datetime.datetime.utcnow(),))
            
            countStr = Template ("select count(*) from ${tblname}")
            self._cur.execute(countStr.substitute(tblname=fhash.FileHash._tblname))

            self._db.commit()
            self._cur.close()
            self._db.close()
            
        except sqlite3.OperationalError:
            logging.error ("(setUp) Operational error")
        except:
            logging.error("(setUp) Error!")
        else:
            logging.debug("Test environment setup complete")


    def tearDown (self):
        try:
            self._db.close()
            os.unlink(self._resDir + os.sep + fhash.FileHash._dbname)
            self._db = None
            self._cur = None
        except sqlite3.OperationalError:
            logging.error("(tearDown) Operational error")
        except:
            logging.error ("(tearDown) Error!")
        else:
            logging.debug("Test environment cleanup complete")
       
       
    def test_update(self):        
        fname = self._createTestFile("fhash_testfile")                
        fh = fhash.FileHash(self._resDir)        
        fh.delete(fname) # if any
        
        before = fh.numEntries()
        fh.update(fname, util.hashFile(fname))
        self.assertEqual(fh.numEntries(), before+1)
        
        fh.close()
        os.unlink(fname) # cleanup your mess
                
    def test_delete(self):
        fname = self._createTestFile("fhash_testfile_noise_12345")                
        fh = fhash.FileHash(self._resDir)        
        fh.delete(fname) # if any            
        
        hash = util.hashFile(fname)
        
        before = fh.numEntries()
        fh.update(fname, hash)
        self.assertEqual(fh.numEntries(), before+1)

        fh.delete(fname)
        self.assertEqual(fh.numEntries(), before)
        
        fh.update(fname, hash)
        self.assertEqual(fh.numEntries(), before+1)
        
        fh.delete(fname[:-5])
        self.assertEqual(fh.numEntries(), before)
        
        fh.close()
        os.unlink(fname) # cleanup your mess
    
    def test_empty(self):
        fh = fhash.FileHash(self._resDir)
        count = fh.numEntries()
        self.assertGreater(count, 0)
        fh.empty()
        self.assertEqual(fh.numEntries(), 0)
        fh.close()
    
    def test_hasChanged(self):
        fname = self._createTestFile("fhash_testfile")                
        fh = fhash.FileHash(self._resDir)        
        fh.update(fname, util.hashFile(fname))
        
        self.assertFalse(fh.hasChanged(fname, util.hashFile(fname)))
        
        with open (fname,"wb") as fd:
            fd.write ("zest zest zest")
        
        self.assertTrue(fh.hasChanged(fname, util.hashFile(fname)))
        
        fh.close()
        os.unlink(fname) # cleanup your mess
    
    def test_lastUpdate(self):
        fh = fhash.FileHash(self._resDir)
        self.assertEquals(fh.lastUpdate("--bogus file name--"), None)
        fh.close()
    
    
    def _createTestFile(self, fname):
        fname = os.getcwd() + os.sep + fname
        with open (fname,"wb") as fd:
            fd.write ("test test test")
        return fname


#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()