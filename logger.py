import os
import queue
import threading
import time
from datetime import datetime


class logger():
    
    def __init__(self,
                 logFilePath,
                 debug=False):
        
        self._logFilePath = logFilePath
        self._debug       = debug
        self._fileId      = None
        
    def logBanner(self,txt=""):
        bannerStr = " **********************************************************************************************"
        self.LOG(bannerStr)
        self.LOG(txt)
        self.LOG(bannerStr)      
        
    def initialize(self):
        
        rtn = True

        try:       
            self._fileId = open(self._logFilePath,"w")
            self._fileId.close()
        except Exception as e:
            print('Error: {}'.format(e))
            rtn = False

        return rtn 

    def LOG(self, data):
        rtn = True
        if(self._fileId != None):
            try:
                now = datetime.now()
                t = now.strftime("%Y:%m:%d %H:%M:%S")
                temp = t + " " + data
                if(self._fileId != None):
                    self._fileId = open(self._logFilePath,"a")
                    self._fileId.write(temp+"\n")
                    self._fileId.close()
                    if(self._debug):
                        print(temp)
            except Exception as e:
                print('Error: {}'.format(e))
            
        return rtn

