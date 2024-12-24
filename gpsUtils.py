import serial
import pynmea2
import time

class gpsUtils():
    def __init__(self,
                 debug=False):

        self._debug           = debug
        
        self._ser = None
        self._nmeaList = []
        
    def getParsedSentence(self,sentenceType):
        parsedMsg = None

        for nmeaSentence in self._nmeaList:
            try:
                temp = pynmea2.parse(nmeaSentence)
                if(temp.sentence_type == sentenceType):
                    parsedMsg = temp
                    break
            except Exception as e:
                #print('Error: {}'.format(e))
                pass
            
        return nmeaSentence, parsedMsg
    
    def connect(self, 
                port,
                 baud):
        
        rtn = True
        try:
            self._ser = serial.Serial(port,
                                baud,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                timeout=0.1)
        except Exception as e:
            print('Error: {}'.format(e))
            rtn = False
        
        return rtn
    
    
    def readGPS(self):
        
        rtn = True
        self._nmeaList = []
        
        readBuf = self._ser.readline()
        # Clear out buffer
        while (readBuf == b''):
            readBuf = self._ser.readline()
            
        while (readBuf != b''):
            try:
                nmeaSentence = readBuf.decode("utf-8")
                self._nmeaList.append(nmeaSentence)
            except Exception as e:
                print('Error readGPS: {}'.format(e))
                
            readBuf = self._ser.readline()
        
        return rtn
    
    def convToDecimalDegree(self, ddss):
        DD = int(float(ddss)/100)
        SS = float(ddss) - DD * 100
        DEC = DD + SS / 60
        return DEC    