'''
Created on Sep 9, 2011

@author: tufanoruk
'''

''' top level logger definition
'''

import logging

DEBUG   = logging.DEBUG
INFO    = logging.INFO
WARNING = logging.WARNING 
ERROR   = logging.ERROR
CRITICAL= logging.CRITICAL
    
_verbosityMap = {'DEBUG':DEBUG, 'INFO':INFO, 'WARNING':WARNING, 
                 'ERROR':ERROR, 'CRITICAL':CRITICAL}
_log= None
_initialized = False

def _init():
    global _initialized
    global _log
    if ((_initialized == None) or (not _initialized)):
        __lh = logging.StreamHandler()
        __lf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        __lh.setFormatter(__lf)

        _log = logging.getLogger("kasa")
        _log.setLevel(logging.ERROR)
        _log.addHandler(__lh)
        _initialized = True
    else:
        pass

def getDefaultLogger():
    _init()
    return _log

def getLogger (name):
    _init()
    return logging.getLogger(name)

