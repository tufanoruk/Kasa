'''
Created on Sep 16, 2011

@author: tufanoruk
'''

import os
import sqlite3
import datetime
from string import Template

import kasa.log

_mlog = kasa.log.getLogger("kasa.fhash")   

class FileHash (object):
    '''
    manages stored files hash values
    
    @todo: remove rows with invalid fname entries 
           by traversing from db to file system in another thread
    '''
    __clog = kasa.log.getLogger("kasa.fhash.FileHash")
    
    _dbname = "kasa.db"
    _tblname = "filehash"

    def __init__(self, resourceDir):
        '''
        Constructor
        '''   
         
        self.__db = sqlite3.Connection(resourceDir + os.sep + self._dbname, 
                                       detect_types = sqlite3.PARSE_COLNAMES | sqlite3.PARSE_DECLTYPES,
                                       isolation_level=None) 
        self.__cur = self.__db.cursor()
        try:
            createStr = Template ('''create table ${tblname} 
                                       (fname text not null unique, 
                                        fhash text not null,
                                        updated timestamp, 
                                        CONSTRAINT pk PRIMARY KEY (fname, fhash))''')
            
            self.__db.execute (createStr.substitute(tblname = self._tblname))
            self.__db.execute ("pragma case_sensitive_like=on;")
        except sqlite3.OperationalError:
            self.__clog.debug("Got operational error during file hash table creation")
        except sqlite3.DatabaseError:
            self.__clog.error("Got database error during file hash table creation ")
            raise           
        except:
            self.__clog.error("Got error during file hash table creation ")
            raise
        
    def close(self):
        try:
            self.__db.commit()
            self.__cur.close()
            self.__db.close()
            
            self._db = None
            self._cur = None
            
        except sqlite3.OperationalError:
            self.__clog.debug("Got operational error during close")
        except sqlite3.DatabaseError:
            self.__clog.error("Got database error during close")
            raise           
        except:
            self.__clog.error("Got error during close")
            raise
        
    def hasChanged (self, fname, fhash):
        ''' checks if given file has changed since last check by comparing its filehash
        '''
        try:                        
            selectStr = Template ("select * from ${tblname} where fname=? and fhash=?")
            self.__cur.execute (selectStr.substitute(tblname=self._tblname),(fname,fhash,))
            row = self.__cur.fetchone()
            return row == None
        
        except sqlite3.OperationalError:
            self.__clog.error("Got operational error during querying change")
            raise
        except sqlite3.DatabaseError:
            self.__clog.error("Got database error during querying change")
            raise
        except:
            self.__clog.error("Got error during querying change")
            raise      
    
    def update (self, fname, fhash):
        ''' insert / replace hash value of the file int filehash table
        '''
        try:
            now = datetime.datetime.utcnow()           
            ''' @@@bug: since hash is the primary key replacement occures only wrt hash value
            filename is not considered. This results storing different files with same hash 
            (lime duplicates and 0 sized files) over and over again
            ''' 
            replaceStr = Template ("replace into ${tblname} values (?,?,?)")
            self.__cur.execute (replaceStr.substitute(tblname=self._tblname), (fname, fhash, now,))
        except sqlite3.OperationalError:
            self.__clog.error("Got operational error during file hash update ")
            raise
        except sqlite3.DatabaseError:
            self.__clog.error("Got database error during file hash update")
            raise
        except:
            self.__clog.error("Got error during file hash pdate")
            raise
        
    def delete (self, fname):
        ''' deletes file name entry from file hash table
        '''
        try:
            deleteStr = Template ("delete from ${tblname} where fname like ?")
            self.__cur.execute (deleteStr.substitute(tblname=self._tblname), (fname+"%",))
        except sqlite3.OperationalError:
            self.__clog.error("Got operational error during row delete")
            raise
        except sqlite3.DatabaseError:
            self.__clog.error("Got database error during row delete")
            raise
        except:
            self.__clog.error("Got error during row delete")
            raise     
    
    def empty (self):
        self.delete("")
    
    def numEntries (self):
        try:
            countStr = Template ("select count(*) from ${tblname}")
            self.__cur.execute (countStr.substitute(tblname=self._tblname))
            return self.__cur.fetchone()[0]
        
        except sqlite3.OperationalError:
            self.__clog.error("Got operational error during querying entry count")
            raise
        except sqlite3.DatabaseError:
            self.__clog.error("Got database error during querying entry count")
            raise
        except:
            self.__clog.error("Got error during querying entry count")
            raise     
    
    def lastUpdate (self, ufile):
        try:
            udatedStr = Template ("select updated from ${tblname} where fname=?")
            self.__cur.execute (udatedStr.substitute(tblname=self._tblname),(ufile,))
            row = self.__cur.fetchone()
            if row:
                return row[0]
            else:
                return None
            
        except sqlite3.OperationalError:
            self.__clog.error("Got operational error during querying update time")
            raise
        except sqlite3.DatabaseError:
            self.__clog.error("Got database error during querying update time")
            raise
        except:
            self.__clog.error("Got error during querying update time")
            raise     
        
    
    def _dumpTable(self):
        dumpStr = Template("select fname, fhash, updated from ${tblname}")
        self.__cur.execute (dumpStr.substitute(tblname=self._tblname))
        for r in self.__cur.fetchall():
            print r
        print "-"*80    
    