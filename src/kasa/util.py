'''
Created on Sep 9, 2011

@author: tufanoruk
'''

import sys
import os.path
import stat
import zlib
import tempfile
import exceptions
import urlparse
import errno

from Crypto.Hash import MD5
from Crypto.Cipher import AES

import kasa.log

_CHUNK_SIZE = 8192

_mlog = kasa.log.getLogger("kasa.util")   


#convert string to hex (from ActiveState Code Recipes)
def toHex(s):
    ''' calculates the hex value of the given string
        by using ordinal values of the chars that makes the string
    '''
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    
    return reduce(lambda x,y:x+y, lst)

#convert hex repr to string (from ActiveState Code Recipes)
def toStr(s):
    return s and chr(int(s[:2], base=16)) + toStr(s[2:]) or ''

def hashFile (ifile):
    ''' Calculates MD5 hash of the given file effectively!
    '''
    md5 = MD5.new()
    with open(ifile,'rb') as f: 
        for chunk in iter(lambda: f.read(128*md5.block_size), ''): 
            md5.update(chunk)             
    return md5.hexdigest() # is a 16B string!


def encryptFile(infname, ofname, key):
    ''' compress and encrypt ifname to ofname with given key
    '''
    # @todo: mode of the enrypted file should be the same as the cleartext file

    with tempfile.TemporaryFile() as zf: 
        
        __compressFile (infname, zf)
        zf.seek(0) # reset file cursor
        
        aes = AES.new(key, AES.MODE_ECB)
        
        with open(ofname, 'wb') as out_file:
            chunk = zf.read(_CHUNK_SIZE)            
            while chunk:
                if len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)                                
                out_file.write(aes.encrypt(chunk))
                chunk = zf.read(_CHUNK_SIZE)


def decryptFile(infname, ofname, key):
    ''' decrypt and decompress infname to ofname
    '''
    aes = AES.new(key, AES.MODE_ECB)

    with open(infname, 'rb') as inf:
        with tempfile.TemporaryFile() as zf: 
            chunk = inf.read(_CHUNK_SIZE)            
            while chunk:
                zf.write(aes.decrypt(chunk))
                chunk = inf.read(_CHUNK_SIZE)
                
            zf.seek(0) # reset file cursor
            __decompressFile (zf, ofname)


def  makeOwnerOnly (path):         
    if (os.name == "nt"):
        __applyWin32OwnerOnly(path)
    elif (os.name == "posix"):
        __applyPosixOwnerOnly (path)
    else:
        _mlog.error("ERROR: Unsupported Operating System " + sys.platform + " " + os.name)
        # @todo: raise exception!
             
def isOwnerOnly (path):
    if (os.name == "nt"):
        return __isOwnerOnly_Win32(path)
    elif (os.name == "posix"):
        return __isOwnerOnly_Posix (path)
    else:
        _mlog.error("ERROR: Unsupported Operating System " + sys.platform + " " + os.name)
        return False
        # @todo: raise exception!
        

# @ todo: also check s3 uri validiy 
def checkStorageValidity (uri, perm=os.R_OK):
    s = urlparse.urlsplit(uri)
    if s[0] == "" or s[0] == "file":
        if not os.path.exists(s[2]) :
            print dir,"path does not exists"
            raise exceptions.IOError
        if not os.access(s[2], perm):
            print dir,"path is not accessible"
            raise exceptions.IOError                
        if not os.path.isdir(s[2]) :
            print dir,"path must be a directory"
            raise exceptions.IOError
        else:
            pass
        

        
def mkdir (path, subdir):
    outdir = path + os.sep
    if subdir:
        outdir += subdir.strip(os.sep)+os.sep
    try:
        os.makedirs(outdir)
        # @todo: mode should match with source directory!
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e        
        
    return outdir
        
# -- module private part

def __applyPosixOwnerOnly (path):
    if (os.path.isdir(path)):
        os.chmod(path, 0700)
    else:
        os.chmod(path, 0600)
     
def __isOwnerOnly_Posix(path):
    if (os.path.isdir(path)):
        return (stat.S_IMODE(os.stat(path).st_mode)==0700)
    else:
        return (stat.S_IMODE(os.stat(path).st_mode)==0600)
    
                        
def __applyWin32OwnerOnly (path):
    #@todo: win32 owner only security settings here
    _mlog.error("Not implemented!")
    pass

def __isOwnerOnly_Win32(path):
    _mlog.error("Not implemented!")
    pass


def __compressFile (infname, of):    
    encoder = zlib.compressobj()
    with open (infname, "rb") as inf:
        block = inf.read(_CHUNK_SIZE)
        while block:                
            of.write (encoder.compress(block))
            block = inf.read(_CHUNK_SIZE)
        of.write (encoder.flush())

            
            
def __decompressFile (inf, ofname):
    decoder = zlib.decompressobj()
    with open (ofname, "wb") as of:
        block = inf.read(_CHUNK_SIZE)
        while block:
            of.write (decoder.decompress(block))
            block = inf.read(_CHUNK_SIZE)
        of.write (decoder.flush())



