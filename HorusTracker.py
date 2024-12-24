import os
import time
import datetime
import configparser
import crcmod
import gpiozero
import HorusModem
import HorusUtils
import gpsUtils
import cw
import logger
import  packetDefs
from horusdemodlib.encoder import Encoder

versionInfo      = "Version 1.0"
debug            = False

config = configparser.ConfigParser()
config.read('config.ini')

spiChannel       = int(config.get('RFM9x', 'spiCS'))
dio0GpioN        = int(config.get('RFM9x', 'dio0GpioN'))
tx_power         = int(config.get('RFM9x', 'tx_power'))
fsk4Freq         = int(config.get('HorusModem', 'freq'))
fsk4Baud         = int(config.get('HorusModem', 'baud'))
txTimeOffset     = int(config.get('HorusModem', 'txTimeOffset'))
payloadID        =  int(config.get('payload', 'payloadID'))
callSign         = config.get('payload', 'callSign')
beconInterval    = int(config.get('payload', 'beconInterval'))
gpsPort          =  config.get('GPS', 'port')
gpsBaud          = int(config.get('GPS', 'baud'))

resetPin         = None

currDir          = os.path.abspath(os.getcwd())
logDir           = currDir+"/log"
flightDir        = logDir + "/" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
dataDir          = flightDir + "/data"
flightDataPath   = dataDir + "/flightData.txt"

def displayParameters():
    print("versionInfo      = " + str(versionInfo))
    print("spiChannel       = " + str(spiChannel))
    print("dio0GpioN        = " + str(dio0GpioN))
    print("fsk4Freq         = " + str(fsk4Freq))
    print("tx_power         = " + str(tx_power))
    print("fsk4Baud         = " + str(fsk4Baud))
    print("txTimeOffset     = " + str(txTimeOffset))
    print("resetPin         = " + str(resetPin))
    print("beconInterval    = " + str(beconInterval))
    print("gpsPort          = " + gpsPort)
    print("gpsBaud          = " + str(gpsBaud))
    print("callSign         = " + callSign)
    print("payloadID        = " + str(payloadID))
    print("flightDataPath   = " + flightDataPath)

def main():
    
    displayParameters()
    print(" ")
    
    if(os.path.exists(logDir) == False):
        os.mkdir(logDir,0o755)

    os.mkdir(flightDir,0o755)
    os.mkdir(dataDir,0o755)       
    
    loggerObj = logger.logger(flightDataPath, True)
    loggerStatus = loggerObj.initialize()
    if(loggerStatus):
        print("Datalogger initialized")
    else:
        print("Data logger could not be initialized")

    horusEncoder = Encoder("/usr/local/lib")
    horusPacketV2 = packetDefs.horusPacketV2Type()
    
    HorusModemObj = HorusModem.HorusModem(spiChannel,dio0GpioN,resetPin,tx_power,fsk4Freq,fsk4Baud,txTimeOffset,debug)
    HorusModemObj.dataLED.off()
    HorusModemObj.linkLED.off()    
    horusCounter = 0

    CPUTemperatureObj = gpiozero.CPUTemperature()
    
    gpsUtilsObj = gpsUtils.gpsUtils()
    runable = True
    gpsLocked = False

    beconIntervalTic = 0
    
    rtn = gpsUtilsObj.connect(gpsPort, gpsBaud)
    while (rtn == False):
        time.sleep(5)
        print("Trying to connect GPS to " +gpsPort)
    print("GPS connected to " +gpsPort)
    
    rtn = HorusModemObj.initialize()
    while(rtn != True):
        print("Modem initialization failed ...Retrying")
        rtn = HorusModemObj.initialize()
        time.sleep(1)
    print("Modem initialization complete")
    
    cwObj        = cw.cw(HorusModemObj.setModeTx,HorusModemObj.setModeRx)
    HorusModemObj.setCWFreq()
    cwObj.send(callSign)
    
    startNow = time.time()

    while(runable):
        gpsLocked = False
        rtn = gpsUtilsObj.readGPS()
        if(rtn):
            nmeaRMC, RMC = gpsUtilsObj.getParsedSentence("RMC")
            if(RMC != None):
                beconIntervalTic = beconIntervalTic + 1
                if(RMC.status == 'A' or RMC.lat != ''):                
                    nmeaGGA, GGA = gpsUtilsObj.getParsedSentence("GGA")
                    if(GGA != None):
                        if(GGA.lat != ''):
                            horusPacketV2.Altitude = int(GGA.altitude)
                            if(horusPacketV2.Altitude != 65535):
                                gpsLocked = True
           
            #Identify in morse code
            timeNow = time.time()
            elapedTime =  timeNow - startNow
            if(int(elapedTime) > 570):
                HorusModemObj.setCWFreq()
                cwObj.send(callSign)
                startNow = time.time()
                            
        if(gpsLocked):                   
            if(beconIntervalTic > beconInterval - 5):
                beconIntervalTic = 0
                
                hr =  GGA.timestamp.hour
                min =  GGA.timestamp.minute
                sec =  GGA.timestamp.second                    
                
                horusPacketV2.PayloadID = payloadID
                horusPacketV2.Counter = horusCounter
                horusPacketV2.Hours = hr
                horusPacketV2.Minutes = min 
                horusPacketV2.Seconds = sec
                
                lat = float(GGA.lat)
                if(GGA.lat_dir == 'S'):
                    lat = lat * -1
                lon = float(RMC.lon)
                if(RMC.lon_dir == 'W'):
                    lon = lon * -1                     
                horusPacketV2.Latitude = gpsUtilsObj.convToDecimalDegree(lat)
                horusPacketV2.Longitude = gpsUtilsObj.convToDecimalDegree(lon)
                
                horusPacketV2.Speed = int(RMC.spd_over_grnd)
                horusPacketV2.Sats = int(GGA.num_sats)
                
                cpuTemp = CPUTemperatureObj.temperature
                horusPacketV2.Temp = int(cpuTemp)
                
                batt = HorusUtils.endecodeBattVoltage(3.0)
                horusPacketV2.Batt = batt
                
                for i in range(packetDefs.CUSTOM_DATA_SIZE):
                    horusPacketV2.CustomData[i] = 0x0
                    
                horusPacketV2ByteArray = bytes(horusPacketV2)
                tempLen = len(horusPacketV2ByteArray)
                tempLen = tempLen - 2
                crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')
                horusPacketV2.Checksum =crc16(horusPacketV2ByteArray[:tempLen])
                horusPacketV2ByteArray = bytes(horusPacketV2)
                encoded, numBytes = horusEncoder.horus_l2_encode_packet(horusPacketV2ByteArray)
                FSK4PreamblePacketByteArray = bytes(packetDefs.FSK4PreamblePacket)
                sendByteArray = FSK4PreamblePacketByteArray +  encoded
                HorusModemObj.send4FSK(sendByteArray)
                
                loggerObj.LOG(nmeaGGA.rstrip("\r\n"))
                loggerObj.LOG(nmeaRMC.rstrip("\r\n"))
            
if __name__ == "__main__":
    main()