'''
Created on Sep 22, 2011

@author: tufan
'''


import os
import sys
import urlparse
import tempfile
import shutil
import boto.s3.connection
import boto.s3.key

import kasa.error 
import kasa.log 
import kasa.util

_mlog = kasa.log.getLogger("kasa.storage")

"files that are automatically created in the local directories by the OS"

_OSFILES = [".ds_store","desktop.ini","thumbs.ini"]

class Storage(object):
    ''' Storage types base class
    '''
    
    def __init__(self):
        pass
    
    def getScheme(self):
        return None
    
    def getPath(self):
        return None

    def getURI(self):
        return None
    
    def store (self, absfname, subdir="", dryRun=None):
        return None
    
    def restore (self, absfname, subdir="", dryRun=None):
        return None
    
    def close(self):
        # cleanup mess
        pass

class StorageIterator (object):
    '''Storage iterator base class over the storage'''

    def __init__(self, storage):
        self._storage = storage

    def nextFile(self):
        '''returns the nextFile file in the Storage
        First parameter is the full path file name,
        Second parameter is the subdirectory of the file wrt Storage root 
        '''
        return ('', '')


class LocalStorage(Storage):
    ''' Stores / restores files to / from local file system
    '''
    
    __clog = kasa.log.getLogger("kasa.storage.LocalStorage")
    
    def __init__(self, path, config, fileHash):
        ''' Constructor. path is assumed to be a valid local absolute file system path
        '''
        Storage.__init__(self)
        self._path = path
        
        self.__clog.debug ("storage path is " + self._path)
        
        kasa.util.checkStorageValidity (self._path,os.W_OK)
        
        self._config = config
        self._fileHash = fileHash
        self.__clog.debug("LocalStorage initialized")
        

    def getScheme(self):
        return "file"
    
    def getPath(self):
        return self._path
    
    def getURI(self):
        return "file://"+self._path
    
    def store (self, absfname, subdir="", dryRun=False):
        ''' store given file into storage path
        infile is the file with absoulute path.
        subdir is the relative directory wrt storage path  
        '''        

        sys.stdout.flush()
        fhash = kasa.util.hashFile(absfname)           
        outfile = self._store(absfname, subdir,fhash, dryRun)
        if outfile:
            self._fileHash.update(absfname, fhash)
        return outfile
        
        
    def _store (self, absfname, subdir, fhash, dryRun=False):
        ''' store given file into storage path
        infile is the file with absoulute path.
        subdir is the relative directory wrt storage path  
        '''
        # Don't store auto generated OS files
        if os.path.basename(absfname).lower() in kasa.storage._OSFILES:
            return ''
        
        outfile = ''
        try:                        
            self.__clog.debug("HASH " + fhash + " " + absfname)
             
            print "Processing",absfname,",",             
            if self._fileHash.hasChanged(absfname, fhash):
                self.__clog.debug("=> encrypting and storing " + absfname )
                if dryRun:
                    updated = self._fileHash.lastUpdate(absfname)
                    if not updated:
                        print "(has not stored yet!)", 
                    else:
                        print "(has changed since", updated,")",
                else:
                                            
                    fname = os.path.basename(absfname)

                    outdir = kasa.util.mkdir(self._path, subdir) 
                    
                    outfile = outdir + fname + ".kasa"                                  
                    kasa.util.encryptFile(absfname, outfile, self._config.getCryptKey())                    
                    self.__clog.debug(absfname+" => "+outfile+" done!")
            else:
                print "(has not changed)",        
        except:
            self.__clog.error("Error during store! " + absfname)
            raise
        else:
            if outfile:
                print "stored!"
            else:
                print "skipped!"

            return outfile    
        
    def restore (self, absfname, subdir="", dryRun=False):
        ''' restore (decrypt and store) given file into storage path
        absname is the file with absoulute path that will be de-crypted.
        subdir is where decrypted file will be restored . it is a
        relative directory wrt storage path  
        '''
        
        outfile = ''
        try:
            fname = os.path.basename(absfname)                                    
            if fname.split('.')[-1] != "kasa":
                raise kasa.error.KasaStorageException("Wrong file type!")
            
            outdir = kasa.util.mkdir(self._path, subdir) 
            
            outfile = outdir + ".".join(fname.split('.')[:-1])
      
            print "Restoring to",outfile,                    
            sys.stdout.flush()
            
            kasa.util.decryptFile(absfname, outfile, self._config.getCryptKey())
            
            print "OK"
            
        except:
            self.__clog.error("Error during restore!")
            raise
        else:
            return outfile
        
        
    def close(self):
        # nothing to clean up
        pass
    
    
    
class LocalStorageIterator(StorageIterator):
    "iterates over local file system"
    
    def __init__(self, storage):
        StorageIterator.__init__(self, storage)
        
    def nextFile(self):
        for r,unused_dirs,files in os.walk(self._storage._path):
            for f in files:
                f_utf8 = f.decode('utf-8')
                r_utf8 = r.decode('utf-8')
                yield r_utf8+os.sep+f_utf8, r_utf8[len(self._storage._path):]

class S3BucketStorage(Storage):
    ''' Stores / restores files to / from AWS S3 account
    '''
    __clog = kasa.log.getLogger("kasa.storage.S3BucketStorage")

    def __init__(self, urituple, config, fileHash):
        ''' urituple must be in the form of
        s3:///bucket-name/prefix/path 
        '''
        Storage.__init__(self)
        pathlist = urituple.path.strip(os.sep).split(os.sep)
        
        if urituple.netloc or not pathlist[0]:
            raise kasa.error.KasaStorageException("Format error. S3 path must be like s3:///bucket-name/prefix/path")
        
        self._bucketName = pathlist[0].lower() # bucket names must be lower case
        self._keyPrefix = os.sep.join(pathlist[1:])
        self._config = config
        self._fileHash = fileHash
        
        self._tmpStorage = LocalStorage(tempfile.mkdtemp(), self._config, self._fileHash)
        
        self._s3conn = boto.s3.connection.S3Connection(self._config.getS3Code(),self._config.getS3Key())
        
        self.__clog.debug("S3BucketStorage initialized")
       
    def getScheme(self):
        return "s3"

    def getPath(self):
        return os.sep+self._bucketName+os.sep+self._keyPrefix

    def getURI(self):
        return "s3://"+self.getPath()
    
    def getS3Bucket(self):
        "S3 Storage specific function. Returns the bucket object"
        return self._s3conn.get_bucket(self._bucketName)

    def store (self, absfname, subdir="", dryRun=False):
        ''' store given file into storage path
        infile is the file with absoulute path.
        subdir is the relative directory wrt storage path  
        '''
        outfile = ''
        try: 
            fhash = kasa.util.hashFile(absfname)           
            outfile = self._tmpStorage._store(absfname, subdir, fhash, dryRun)
            
            if outfile:
                bucket = self._s3conn.get_bucket(self._bucketName)
                k = boto.s3.key.Key (bucket)
                k.key = self._keyPrefix+os.sep
                if subdir:
                    k.key += subdir.strip(os.sep)+os.sep
                k.key += os.path.basename(absfname)+".kasa"

                self.__clog.debug(outfile+" => " + self._bucketName + ", " + k.key)
                
                # transfer to s3            
                k.set_contents_from_filename(outfile, cb=self._uploadProgress)

                self._fileHash.update(absfname, fhash)       
                         
                os.unlink(outfile)                                       
        except:
            self.__clog.error("")
            raise
        
        return outfile
                
    def restore(self, absfname, subdir="", dryRun=False):   
        raise kasa.error.KasaStorageException("Cannot restore to Amazon S3 bucket!")
        

    def close(self):
        shutil.rmtree(self._tmpStorage.getPath())
        pass
    
    def _uploadProgress(self, transmitted, total):
        print transmitted,"Bytes of",total,"Bytes"



class S3BucketStorageIterator(StorageIterator):
    "iterates over local file system"
    
    def __init__(self, storage):
        StorageIterator.__init__(self, storage)
    
    def nextFile(self):
        s = self._storage
        b = s.getS3Bucket()
        rs = b.list(os.sep.join(s.getPath().strip(os.sep).split(os.sep)[1:]))
        
        for k in rs:
            # get it into local temp dir
            subdir = os.sep.join(k.name.strip(os.sep).split(os.sep)[:-1])
            kasa.util.mkdir(s._tmpStorage.getPath(), subdir)            
            fname = s._tmpStorage.getPath()+os.sep+k.name
            k.get_contents_to_filename(fname)                
            yield fname.decode('utf-8'), subdir.decode('utf-8')
        

class StorageFactory(object):
    ''' returns LocalStorage or S3Storage object depending on the provided destination URI
    '''
    
    __clog = kasa.log.getLogger("kasa.storage.StorageFactory")

    def __init__(self, config, fileHash):
        ''' Constructor 
        Factory needs to pass configuration parameters hold in Configuration to Storage objects 
        '''
        self._config = config
        self._fileHash = fileHash

    def getStorage(self, uri):
        
            urituple = urlparse.urlsplit(uri)
                              
            if urituple.scheme == "" or urituple.scheme == "file":
                            
                path = os.path.abspath (os.path.expanduser(urituple.path))    

                if self._isLocalPathValid(path):
                    s = LocalStorage(path, self._config, self._fileHash)
                    return s, LocalStorageIterator(s)
                else:
                    raise kasa.error.KasaStorageException("Invalid Path! Cannot create Storage")
            elif urituple.scheme == "s3":
                
                s = S3BucketStorage (urituple, self._config, self._fileHash)
                return s, S3BucketStorageIterator(s)
            
            else:
                raise kasa.error.KasaStorageException("Unsupported scheme '"+uri+"'")


    def _isLocalPathValid (self, directory, perm=os.W_OK):
        if not os.path.exists(directory) :
            self.__clog.error(directory + " path does not exists")
            return False
        if not os.access(directory, perm):
            self.__clog.error(directory + " path is not accessible")
            return False                
        if not os.path.isdir(directory) :
            self.__clog.error(directory + " path must be a directory")
            return False
        return True



    
    


