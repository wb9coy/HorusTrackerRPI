import time
import threading
import spidev
import gpiozero
import constants

class RFM9x(object):
    def __init__(self,spiChannel,dio0GpioN,resetPin,debug):

        self._hw_lock = threading.RLock() # lock for multithreaded access

        self._resetPin = resetPin
        self._debug    = debug
        
        self.fifoSize  = 64
        
        self.spi = spidev.SpiDev()
        self.spi.open(0, spiChannel)
        self.spi.max_speed_hz = 5000000
        
        self._mode = None
        self._dio0GpioN  = gpiozero.DigitalInputDevice(dio0GpioN)
        self._dio0GpioN.when_activated = self._handle_interrupt
        
        self.dataLED  = gpiozero.DigitalOutputDevice(13)
        self.dataLED.on()
        time.sleep(1)
        
        self.linkLED  = gpiozero.DigitalOutputDevice(6)
        self.linkLED.on()
        time.sleep(1)
        
        self.timingTest  = gpiozero.LED(26)
        self.timingTest.off()         
           
    def _spiRead(self, register, length=1):
        if length == 1:
            d = self.spi.xfer([register] + [0] * length)[1]            
            return d
        else:
            d = self.spi.xfer([register] + [0] * length)[1:]
            return d
        
    def _spiWrite(self, register, payload):
        if type(payload) == int:
            payload = [payload]
        elif type(payload) == bytes:
            payload = [p for p in payload]
        elif type(payload) == str:
            payload = [ord(s) for s in payload]
        self.spi.xfer([register | 0x80] + payload)
            
    def _handle_interrupt(self):
        
        with self._hw_lock:
            irq_flags = self._spiRead(constants.REG_3E_IRQ_FLAGS1)
            if self._mode == constants.MODE_RXCONTINUOUS and (irq_flags & constants.RX_DONE):

                self._spiWrite(constants.REG_0D_FIFO_ADDR_PTR, self._spiRead(constants.REG_10_FIFO_RX_CURRENT_ADDR))
                packet = self._spiRead(constants.REG_00_FIFO, self.fifoSize)
                self.rxDataQueue.put(packet)
                rssi = -137 + self._spiRead(constants.REG_11_RSSI_VALUE_FSK)

    def setGaussian(self,bt):
        rtn = True
        if(bt == 1):
            self.setStandbye()
            self._spiWrite(constants.REG_0A_Reg_PA_RAMP,0x29)
        else:
            rtn = False
            
        return rtn
    
    def setDeviationFSK(self,freqDev):
        rtn = True
        
        self.setStandbye()
        freqDevCalVal = freqDev * (1 << 19) / 32000
        self._spiWrite(constants.REG_04_FDEV_MSB,int(freqDevCalVal) >>8)
        self._spiWrite(constants.REG_05_FDEV_LSB,int(freqDevCalVal))
            
        return rtn
        
    def resetChip(self,resetPin):
        pass
    
    def setMaxCurrent(self,rate):
        rtn = True
        
        if(rate >  0x1B):
            print("Maximum rate value = 0x1B, because maximum current supply = 240 mA")
            rtn = False
        else:
            setRate = rate | 0x20;
            self.setStandbye()
            self._spiWrite(constants.REG_0B_OCP,setRate)
            st0 = self._spiRead(constants.REG_01_OP_MODE)
            if(st0 != constants.MODE_STDBY):
                rtn = False
                
        return rtn
    
    def setBitrate(self,bps):
        rtn = True
        
        if( (bps <1200) or (bps > 300000) ):
            print("Invalid bit rate")
            rtn = False
        else:
            #set bit rate
            self.setStandbye()
            bitRate = (constants.FXOSC * 1.0)/bps
            bitRate = int(bitRate)
            #print((bitRate & 0xFF00) >> 8)
            self._spiWrite(constants.REG_02_BITRATEMSB,0x0D)
            #print(bitRate & 0x00FF)
            self._spiWrite(constants.REG_03_BITRATELSB,0x05)
            
        return rtn
               
       
    def setAFCBandwidth(self,afcbw):
        rtn      = True
        rxbwexp  = 1
        rxBWMant = 2
        tmpAFCbw = 0
        
        if( (afcbw <2600) or (afcbw > 250000) ):
            print("Invalid AFC Bandwidth")
            rtn = False
        else:
            tmpAFCbw = constants.FXOSC/afcbw/8
            while(tmpAFCbw > 31):
                rxbwexp = rxbwexp + 1
                tmpAFCbw = tmpAFCbw/2.0
                
            if(tmpAFCbw <17):
                rxBWMant = 0
            elif(tmpAFCbw <21):
                rxBWMant = 1
                
            self.setStandbye()
            self._spiWrite(constants.REG_13_AFC_BW,rxBWMant | (rxbwexp<<3))
                
        return rtn
    
    def setRxBandwidth(self,rxbw):
        rtn      = True
        rxbwexp  = 1
        rxBWMant = 2
        tmpRxbw  = 0
        
        if( (rxbw <2600) or (rxbw > 250000) ):
            print("Invalid Rx Bandwidth")
            rtn = False
        else:
            tmpRxbw = constants.FXOSC/rxbw/8
            while(tmpRxbw > 31):
                rxbwexp = rxbwexp + 1
                tmpRxbw = tmpRxbw/2.0
                
            if(tmpRxbw <17):
                rxBWMant = 0
            elif(tmpRxbw <21):
                rxBWMant = 1
                
            self.setStandbye()
            self._spiWrite(constants.REG_12_RX_BW,rxBWMant | (rxbwexp<<3))
                
        return rtn

   
    def setRxConf(self,conf):
        rtn      = True
        
        self.setStandbye()
        self._spiWrite(constants.REG_0D_RX_CONFG,conf)
        
        return rtn
    
    def setSyncConf(self,conf,syncBytes):
        rtn          = True
        lenSyncBytes = len(syncBytes)
        syncIndex    = 0
        
        if(lenSyncBytes > 8):
            rtn = False
            print("Invalid sync pattern size")
        else:
            self._spiWrite(constants.REG_27_SYNC_CONFIG,conf)
            for syncByte in syncBytes:
                self._spiWrite(constants.REG_28_SYNC_VALUE1+syncIndex,syncBytes[syncIndex])
                syncIndex = syncIndex + 1
                
        return rtn
    
    def setPreambleLength(self,preLen):
        rtn      = True
        
        self._spiWrite(constants.REG_25_PREAMBLE_MSB_FSK, preLen >>8)
        self._spiWrite(constants.REG_26_PREAMBLE_LSB_FSK, preLen&0xff)
        
        return rtn
    
    def setPreambleDetect(self,conf):
        rtn      = True
        
        self._spiWrite(constants.REG_1F_PREAMBLE_DETECT,conf)
        
        return rtn
    
    def setPacketConfig(self,conf1,conf2):
        rtn      = True
        
        self.setStandbye()
        self._spiWrite(constants.REG_30_PACKET_CONFIG1,conf1)
        self._spiWrite(constants.REG_31_PACKET_CONFIG2,conf2)
        
        return rtn
    
    def setStandbye(self):
        rtn      = True
        
        self._spiWrite(constants.REG_01_OP_MODE,constants.MODE_STDBY)
        self._mode = constants.MODE_STDBY
        
        return rtn
    
    def setFrequency(self,freq):
        frf = int(freq / constants.FSTEP)    
        rtn = self.setFrequencyfrf(frf)
        return rtn
    
    def setFrequencyfrf(self,frf):
        rtn   = True
        self.setStandbye()
        self._spiWrite(constants.REG_06_FRF_MSB, (frf >> 16) & 0xff)
        self._spiWrite(constants.REG_07_FRF_MID, (frf >> 8) & 0xff)
        self._spiWrite(constants.REG_08_FRF_LSB, frf & 0xff)
        time.sleep(.001)
        
        return rtn
    
    def setTxPower(self,txPower):
        rtn        = True
        pwrSetting = txPower
        
        if pwrSetting < 5:
            pwrSetting = 5
        if pwrSetting > 23:
            pwrSetting = 23

        self.setStandbye()
        if pwrSetting > 20:
            self._spiWrite(constants.REG_4D_PA_DAC, constants.PA_DAC_ENABLE)
            pwrSetting -= 3
        else:
            self._spiWrite(constants.REG_4D_PA_DAC, constants.PA_DAC_DISABLE)

        self._spiWrite(constants.REG_09_PA_CONFIG, constants.PA_SELECT | (pwrSetting - 5))
        
        return rtn
    
    def clearIRQFlags(self):
        rtn   = True
        
        self._spiWrite(constants.REG_3E_IRQ_FLAGS1, 0xff)
        self._spiWrite(constants.REG_3F_IRQ_FLAGS2, 0xff)

        return rtn
    
    def setPayloadLength(self, payloadLen):
        rtn   = True
        
        self.setStandbye()
        self._spiWrite(constants.REG_32_PAYLOAD_LEN, payloadLen)
                
        return rtn
    
    def setModeRx(self):
        rtn   = True
        
        if self._mode != constants.MODE_RXCONTINUOUS:
            self._spiWrite(constants.REG_01_OP_MODE, constants.MODE_RXCONTINUOUS)
            self._spiWrite(constants.REG_40_DIO_MAPPING1, 0x00)  # Interrupt on RxDone
            self._mode = constants.MODE_RXCONTINUOUS
                
        return rtn
    
    def setModeSleep(self):
        rtn   = True
        
        self._spiWrite(constants.REG_01_OP_MODE,constants.MODE_SLEEP)
                
        return rtn      
    
    def setModeTx(self):
        rtn   = True
        
        if self._mode != constants.MODE_TX:
            self._spiWrite(constants.REG_01_OP_MODE, constants.MODE_TX)
            self._spiWrite(constants.REG_40_DIO_MAPPING1, 0x00)  # Interrupt on TxDone
            self._mode = constants.MODE_TX
                
        return rtn
    
    def setFSK(self):
        st0   = None
        state = 1
        
        self._spiWrite(constants.REG_01_OP_MODE,constants.MODE_SLEEP)
        self._spiWrite(constants.REG_01_OP_MODE,constants.MODE_SLEEP)
        self.setStandbye()
        
        time.sleep(1)
        
        st0 = self._spiRead(constants.REG_01_OP_MODE)
        if(st0 == constants.MODE_STDBY):
            state = 0
        
        return state

    def setModeFSTX(self):
        rtn = str
        
        self._spiWrite(constants.REG_01_OP_MODE,constants.MODE_FSTX)
        
        return rtn
    
    def setDirectMode(self):
        
        rtn = True
        self.setStandbye()
        
        self._spiWrite(constants.REG_40_DIO_MAPPING1, constants.DIO1_CONT_DCLK | constants.DIO2_CONT_DATA)
        self.setContinuousMode()
        
        return rtn
    
    def setContinuousMode(self):
        
        rtn = True
        self.setStandbye()
        
        self._spiWrite(constants.REG_31_PACKET_CONFIG2, constants.DATA_MODE_CONTINUOUS)
        
        return rtn    
    
    def setOOK(self):
        st0   = None
        state = 1
        
        self._spiWrite(constants.REG_01_OP_MODE,constants.MODE_SLEEP)
        self._spiWrite(constants.REG_01_OP_MODE,constants.MODE_OOK)
        self.setStandbye()
        
        time.sleep(1)
        
        st0 = self._spiRead(constants.REG_01_OP_MODE)
        if(st0 == constants.MODE_STDBY):
            state = 0
        
        return state
    
    def setEncoding(self, encoding):
        rtn   = True
        
        self.setStandbye()
        if(encoding == constants.ENCODING_NRZ):
            self._spiWrite(constants.REG_30_PACKET_CONFIG1, constants.DC_FREE_NONE)
        elif(encoding == constants.ENCODING_MANCHESTER):
            self._spiWrite(constants.REG_30_PACKET_CONFIG1, constants.DC_FREE_MANCHESTER)
        elif(encoding == constants.ENCODING_WHITENING):
            self._spiWrite(constants.REG_30_PACKET_CONFIG1, constants.DC_FREE_WHITENING)
        else:
            rtn = False

        return rtn

    def setDataShaping(self, sh):
        rtn = True

        self.setStandbye()

        if(sh == constants.SHAPING_NONE):
            self._spiWrite(constants.REG_01_OP_MODE,constants.NO_SHAPING)
        elif(sh == constants.SHAPING_0_3):
            self._spiWrite(constants.REG_01_OP_MODE,constants.GAUSSIAN_0_3)
        elif(sh == constants.SHAPING_0_5):
            self._spiWrite(constants.REG_01_OP_MODE,constants.GAUSSIAN_0_5)
        elif(sh == constants.SHAPING_1_0):
            self._spiWrite(constants.REG_01_OP_MODE,constants.GAUSSIAN_1_0)            

        return rtn
