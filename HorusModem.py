import time
import RFM9x
import packetDefs
import constants

class HorusModem(RFM9x.RFM9x):
    def __init__(self,spiChannel,dio0GpioN,resetPin,txPower,fsk4Freq,fsk4BaudRate,txTimeOffset, debug=False):
        super().__init__(spiChannel,dio0GpioN,resetPin,debug)
        
        self._txPower = txPower
        self._fsk4Freq = fsk4Freq
        self._fsk4BaudRate = fsk4BaudRate
        self._txTimeOffset = txTimeOffset
        self._debug        = debug
         
        self._fsk4Shift = 270
        self._fsk4BaudRate = self._fsk4BaudRate
        self._tones = [0, 0, 0, 0]
        self._corr = [110,110, 110, 111]
        self._symDuration = int(1000000000 / self._fsk4BaudRate)
        self._guardTime = round(self._symDuration / 2000000000, 4)
        self._txTime = round(self._symDuration/1000000000 - self._guardTime, 4)

        self._baseFreq = int(self._fsk4Freq / constants.FSTEP)        

    def initialize(self):
        status = True
        
        rtn = self.setMaxCurrent(0x1b)
        if(rtn != True):
            status = False
            print("Could not set Max Current")
            
        rtn = self.setOOK()
        if(rtn != 0):
            status = False
            print("Could not set OOKK mode")
                
        if(status):
            rtn = self.setGaussian(bt=1)
            if(rtn != True):
                status = False
                print("Could not set Gaussian")
                
        if(status):
            rtn = self.setPacketConfig(0x08,0x40)
            if(rtn != True):
                status = False
                print("Could not set packet config")
                
        if(status):
            rtn = self.setFrequency(self._fsk4Freq)
            if(rtn != True):
                status = False
                print("Could not set frequency")
                
        if(status):
            rtn = self.setTxPower(self._txPower)
            if(rtn != True):
                status = False
                print("Could not set Tx power")
                        
        if(status):
            rtn = self.clearIRQFlags()
            if(rtn != True):
                status = False
                print("Could not cFSLlear IRQ flags")
                
        if(status):
            #Write resultant tones into arrays for quick lookup when modulating.
            shiftFreq = self.getRawShift(self._fsk4Shift)
            for i in range(4):
                self._tones[i] = shiftFreq*i
                
        rtn = self.setEncoding(constants.ENCODING_NRZ)
        if(rtn == False):
            status = False
            print("Could not set ENCODING_NRZ")
                
        if(status):
            rtn = self.setDataShaping(constants.SHAPING_NONE)
            if(rtn == False):
                status = False
                print("Could not set SHAPING_NONE")
                    
        if(status):
            rtn = self.setDeviationFSK(.4)
            if(rtn == False):
                status = False
                print("Could not set setDeviationFSK")                   
                               
        return status
    
    def tone(self, i):
        rtn = True

        frf =  int(self._baseFreq + self._tones[i])
        frf = frf + self._corr[i]

        nsTime = time.time_ns() 
        self.transmitDirect(int(frf))
        
        time.sleep(self._txTime)
        self.timingTest.off()
        self.setStandbye()
        while( (nsTime + 10000000 - self._txTimeOffset) > time.time_ns()):
            pass
        
        return rtn

    def writeBytes(self, buf):
        rtn = True
        for b in buf:
            self.writeByte(b)

        return rtn

    def writeByte(self, b):
        rtn = True
        bTemp = b
        count = 1
        while count in range(5):
            symbol = (bTemp & 0XC0) >> 6
            self.tone(symbol)
            bTemp = bTemp << 2
            count += 1

        return rtn


    def getRawShift(self, shift):
        #calculate module carrier frequency resolution
        freqStep = round(constants.FSTEP)
        if(shift % freqStep < (freqStep / 2)):
            val = shift / freqStep
        else:
            val = (shift / freqStep) + 1

        return int(val)

    def transmitDirect(self, frf):
        rtn = True

        rtn = self.setFrequencyfrf(frf)
        self.setModeFSTX()
        self.setModeTx()
        self.timingTest.on()

        return rtn
    
    def setCWFreq(self):  
        frf =  int(self._baseFreq + self._tones[1])
        frf = frf + self._corr[0]
        rtn = self.setFrequencyfrf(frf)
        
        return rtn
    
    def transmitLET(self):
        rtn = True
        
        frf =  int(self._baseFreq + self._tones[0])
        frf = frf + self._corr[0]

        self.transmitDirect(int(frf))
        time.sleep(1)
        self.setStandbye()
        self.timingTest.off()        
      
        return rtn        

    def send4FSK(self, payload):
        rtn = True
        
        self.dataLED.on()
        self.transmitLET()
        self.writeBytes(payload)
        self.dataLED.off()

        return rtn    