'''
Created on Aug 25, 2011

@author: tufan
'''

class KasaException(Exception):
    '''
        Base exeption class
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def getMessage(self):
        return "Base Kasa Exception"
    
    
class KasaKeyException(KasaException):
    '''
        Thrown when key is not stong enough
    '''
    def __init__(self):
        pass

    def getMessage(self):
        return "Kasa Key Exception"

    
class KasaS3KeyException(KasaException):
    '''
        Thrown when S3 key is not valid
    '''
    def __init__(self):
        pass
    
    def getMessage(self):
        return "Kasa S3 Key Exception"
   
    
class KasaS3CodeException(KasaException):
    '''
        Thrown when S3 code is not valid
    '''
    def __init__(self):
        pass
    
    def getMessage(self):
        return "Kasa S3 Code Exception"
   
    

class KasaFileException(KasaException):
    
    def __init__(self):
        pass
    
    def setMessage(self,msg):
        self._message = msg
    
    def getMessage(self):
        return "Kasa File Exception: " + self._message
    
    
class KasaStorageException(KasaException):

    def __init__(self, msg):
        self._message = msg

    def getMessage(self):
        return "Kasa File Exception: " + self._message
        
        
