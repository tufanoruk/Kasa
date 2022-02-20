'''
Created on Aug 19, 2011

@author: tufanoruk
'''

import os
import argparse

import kasa.log
import kasa.util

COMMENT_CHAR = "#"

''' module level logger
'''
_mlog = kasa.log.getLogger("kasa.config")    


class Parameters():
    '''
    Provides common parameters
    '''
    #-- private
    __MAJOR_VERSION = 0
    __MINOR_VERSION = 4
    __MICRO_VERSION = 1

    __version = str(__MAJOR_VERSION) + "." + str(__MINOR_VERSION) + "." + str(__MICRO_VERSION)
    
    __clog = kasa.log.getLogger("kasa.config.Parameters")
            
    #-- protected
    _resDir = os.path.join(os.getenv("HOME"), ".kasa")  # first assume POSIX

    ''' _args is a map with following keys
             verbosity: level of logging
             confFile : configuration file path/name 
             srcURI   : source URI
             dstURI   : destination storage URI
    '''
    _args = None
    

    def __init__(self):

        #@todo: preferred_encoding = locale.getpreferredencoding() or "UTF-8"
        
        if (os.name == "nt"):
            self._resDir = os.path.join(os.getenv("USERPROFILE").decode('mbcs'), "Application Data", "Kasa")            
  
        if (os.access(self._resDir,os.R_OK)):
            pass
        else:
            try:
                os.mkdir(self._resDir,0700)
                kasa.util.makeOwnerOnly (self._resDir)
            except:
                self.__clog.error("ERROR during resource directory creation")
                raise
        
        self.__clog.debug("Parameters initiated!")
        
    def getVersion(self):
        return self.__version
                        
    def getVerbosity(self):
        try:
            self._args.verbosity
        except AttributeError:
            return kasa.log.ERROR;
        else: 
            return self._args.verbosity
    
    def getArgs (self):
        return self._args
    
    def getResDir(self):
        return self._resDir

    def dumpArgs(self):
        print self._args

    # --protected part

    def _addArgs (self, parser):
        parser.add_argument("--version", 
                            action='version', 
                            version=self.getVersion(),
                            help="Show program version and exit.")

        parser.add_argument("-v", "--verbose", 
                            dest="verbosityArg", 
                            action="store",
                            nargs=1, 
                            default=['ERROR'], 
                            choices=['DEBUG','INFO','WARNING', 'ERROR','CRITICAL'],
                            help="Enable verbose output.")
        
        self.__clog.debug("common arguments added!")
        
    def _parseArgs (self, parser):
        self._args = parser.parse_args()
        if self._args.verbosityArg:
            self._args.verbosity = kasa.log._verbosityMap[self._args.verbosityArg[0]] 
            # set debug level
            self.__clog.setLevel(self.getVerbosity())
        #self.__clog.debug("DEBUG logs shall be collected")
        #self.__clog.error("ERROR logs shall be collected")
        #self.__clog.warning("WARNING logs shall be collected")
        #self.__clog.critical("CRITICAL logs shall be collected")      
            
           
class ConfigParameters (Parameters):
    '''
    Configuration tool specific parameters
    '''
    __clog = kasa.log.getLogger("kasa.config.ConfigParameters")

    def __init__(self):
        Parameters.__init__(self)
        self.__clog.debug("ConfigParameters initilized")
        
    def parseArgs(self):        
        parser = argparse.ArgumentParser(prog="kasa-config",
                                         description='Kasa configuration utility.')
        Parameters._addArgs(self, parser)
        
        parser.add_argument("-o", "--out-file",
                            dest="confFile",
                            action="store",
                            nargs=1,
                            default=[self._resDir+"/config"])
        try:
            Parameters._parseArgs(self, parser)           
        except (argparse.ArgumentError, argparse.ArgumentTypeError):
            self.__clog.warning("ERROR parsing arguments")
            raise        
        self.__clog.debug("ConfigParameter arguments parsed")


class StoreParameters (Parameters):
    '''
    Store tool specific parameters
    '''
    __clog = kasa.log.getLogger("kasa.config.StoreParameters")
     
    def __init__(self):
        Parameters.__init__(self)
        
    def parseArgs(self):
        parser = argparse.ArgumentParser(prog="kasa-store",
                                         description='''Kasa storage utility stores the modified content of 
                                         the given directory structure recursively using client side encryption   
                                         to the local file system or AmazonS3 service. 
                                         It can also restore files it has stored''')
                                         
        Parameters._addArgs(self, parser)
        
        parser.add_argument("-c", "--config-file",
                            dest="confFile",
                            action="store",
                            nargs=1,
                            default=[self._resDir+"/config"],
                            help="configuration file (default is " + self._resDir + "/config)")
        parser.add_argument("-s", "--source-URI",
                            dest="srcURI",
                            action="store",
                            nargs=1,
                            required=True,
                            help="the directory URI which is to be stored securely to the destination")
        parser.add_argument("-d", "--destination-URI",
                            dest="dstURI",
                            action="store",
                            nargs=1,
                            required=True,
                            help="the destination URI where the files will be stored securely."+ 
                            "Can be local file system or Amazon S3 service.")
        parser.add_argument("-l", "--list",
                            dest="list",
                            action="store_true",
                            required=False,
                            help="lists files that will be stored. No store operation is performed.")    
        parser.add_argument("--reset",
                            dest="reset",
                            action="store_true",
                            required=False,
                            help="forcefully stores all files under src directory.")
        parser.add_argument("-r", "--restore",
                            dest="restore",
                            action="store_true",
                            required=False,
                            help="restores all files under source-URI tree into the destination-URI."+
                            "Currently only local file system is supported as destination-URI")
        
        try:
            Parameters._parseArgs(self, parser)
        except:
            self.__clog.warning("ERROR parsing arguments")
            raise 
        #@todo: store tool related parameter parsing
    


