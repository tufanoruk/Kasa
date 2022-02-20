'''
Created on Sep 13, 2011

@author: tufanoruk
'''

import errno
import ConfigParser

import kasa.error
import kasa.log
import kasa.util

_mlog = kasa.log.getLogger("kasa.cfile")   

class Configuration():
    ''' Configuration file accessor. MSWin style INI file is utilized through ConfigFile module
        Supported sections and fields are as follows
        
        [kasa]
        debug=ERROR
        
        [key]
        cryptKey = < 16B string >
        s3Code = < >=20B string >
        s3Key =  < >=20B string >
        
        [path]
        hiddenDirs = False
        hiddenFiles = False
        exludeExpr = < regular expression >
    '''

    _config = ConfigParser.RawConfigParser()
    
    __clog = kasa.log.getLogger("kasa.cfile.Configuration")
         
    def __init__(self, cfname):
        self._cfname = cfname
        
    def open (self):
        try:
            self._config.optionxform = str # make options case sensitive
            
            configfile = self.__open("rb")
            self.__clog.debug("config file opened!")
            with configfile:
                self._config.readfp (configfile)
            if not self._config.has_section('kasa'):
                self._config.add_section('kasa')                
            if not self._config.has_section('key'):
                self._config.add_section('key')
            if not self._config.has_section('path'):
                self._config.add_section('path')            
        except:
            raise           
                
    def close (self):
        self.save()
        #@todo: should do more then save!
    
    def save(self):
        try:
            configfile = self.__open("wb")
            with configfile:
                self._config.write(configfile)

            self.__clog.debug("config file written!")
        except:
            self.__clog.error("Configuration cannot be saved!")
    
    def setCryptKey(self, key):
        #@todo: check validity more throughly!
        if len(key) < 16:
            raise kasa.error.KasaKeyException()
        self._config.set('key', 'cryptKey', key)
        
    
    def getCryptKey(self):
        if self._config.has_option('key', 'cryptKey'):
            return self._config.get('key', 'cryptKey')
        else:
            return None
    
    def setS3Code (self, code):
        #@todo: check validity more throughly! 
        if len(code) < 20:
            raise kasa.error.KasaS3CodeException()    
        self._config.set('key', 's3Code', code)

    def getS3Code(self):
        if self._config.has_option('key', 's3Code'):
            return self._config.get('key', 's3Code')
        else:
            return None
        
    def setS3Key(self, s3key):
        #@todo: check validity more throughly! 
        if len(s3key) < 40:
            raise kasa.error.KasaS3KeyException()
        self._config.set('key','s3Key', s3key)
        
    def getS3Key(self):
        if self._config.has_option('key', 's3Key'):
            return self._config.get('key', 's3Key')
        else:
            return None

    def setDebug(self, debugLevel):
        self._config.set('kasa','debug', debugLevel)
        
    def getDebug(self):
        if self._config.has_option('kasa', 'debug'):
            return kasa.log._verbosityMap[self._config.get('kasa', 'debug')]
        else:
            return kasa.log.ERROR
        
# --- private part
        
    def __open (self, mode):
        fp = None
        try:
            # if access rights are wrong warn and do not continue
            if not kasa.util.isOwnerOnly(self._cfname):
                e = kasa.error.KasaFileException()
                e.setMessage('''
   Configuration file permissions are wrong. It may have been compromised. Please check your system!
''')
                raise e
            self.__clog.debug("open config file " + self._cfname)
            fp = open(self._cfname, mode)
        except (IOError, OSError) as e:
            self.__clog.debug("error opening config file " + self._cfname)
            if e.errno == errno.ENOENT:
                self.__clog.debug("Config file does not exist creating one!")
                fp = open(self._cfname,'wb')
                fp.close()
                # file must have been created
                kasa.util.makeOwnerOnly(self._cfname)
                fp = open(self._cfname, mode)
            else:  # Not a file not exist error!
                e = kasa.error.KasaFileException()
                e.setMessage(e.strerror)
                raise e
            
        return fp # no matter what           
        
    