import ctypes

START_IMAGE	= 0xff
IMAGE_DATA	= 0xee
END_IMAGE	= 0xdd
GPS_GGA		= 0xc1
GPS_GGA_1	= 0xc2
GPS_GGA_2	= 0xc3
GPS_RMC		= 0xb1
GPS_RMC_1	= 0xb2
GPS_RMC_2	= 0xb3
INT_TEMP	= 0xaa
EXT_TEMP	= 0x99
BATT_INFO       = 0x88
PRESS_INFO      = 0x77
HUM_INFO        = 0x66
INFO_DATA       = 0x55
CW_ID           = 0x44 

RSSI_INFO       = 0x13
PING	        = 0x14

NPAR               = 16
CRC16_LEN = 2
MAX_IMG_BUF_LEN    = 42
MAX_INFO_DATA_SIZE = 20
MAX_CALL_SIGN_SIZE = 12
MAX_GPS_DATA       = 45
CUSTOM_DATA_SIZE = 9

MTU = 64

c_uint32 = ctypes.c_uint32
c_uint16 = ctypes.c_uint16
c_uint8 = ctypes.c_uint8
c_float = ctypes.c_float

class HABPacketImageStartType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("packetType",    c_uint16),
        ("imageFileID",   c_uint8),
        ("fileSize",      c_uint32),
        ("crc16",         c_uint16),
        ("parity",        c_uint8*NPAR)
        ]

class HABPacketImageDataType(ctypes.LittleEndianStructure):
    name     = "HABPacketImageDataType"
    _pack_   = 1
    _fields_ = [
        ("packetType",    c_uint16),
        ("imageFileID",   c_uint8),
        ("imageSeqnum",   c_uint16),
        ("imageDataLen",  c_uint8),
        ("imageData",     c_uint8*MAX_IMG_BUF_LEN),
        ("parity",        c_uint8*NPAR)
        ]
    
class HABPacketImageEndType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("packetType",    c_uint16),
        ("imageFileID",   c_uint8),
        ("crc16",         c_uint16),
        ("parity",        c_uint8*NPAR)
        ]
    
class HABPacketInfoDataType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("packetType",    c_uint16),
        ("infoDataLen",   c_uint8),
        ("infoData",      c_uint8*MAX_INFO_DATA_SIZE),
        ("crc16",         c_uint16),
        ("parity",        c_uint8*NPAR)
        ]
    
class HABPacketGPSDataType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("packetType",    c_uint16),
        ("gpsDataLen",    c_uint8),
        ("gpsData",       c_uint8*MAX_GPS_DATA), 
        ("parity",        c_uint8*NPAR)
        ]       
    
class HABPacketCallSignDataType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("packetType",      c_uint16),
        ("callSignDataLen", c_uint8),
        ("callSignData",    c_uint8*MAX_CALL_SIGN_SIZE),
        ("crc16",           c_uint16),
        ("parity",          c_uint8*NPAR)
        ] 
    
class HABPacketBattInfoDataType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("packetType",    c_uint16),
        ("battInfoData",  c_float),
        ("crc16",         c_uint16),
        ("parity",        c_uint8*NPAR)
        ]
  
class HABPacketIntTempInfoDataType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("packetType",      c_uint16),
        ("intTempInfoData", c_float),
        ("crc16",           c_uint16),
        ("parity",          c_uint8*NPAR)      
        ]

class HABPacketExtTempInfoDataType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("packetType",      c_uint16),
        ("extTempInfoData", c_float),
        ("crc16",           c_uint16),
        ("parity",          c_uint8*NPAR)      
        ]

class HABPacketHumidityInfoDataType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("packetType",       c_uint16),
        ("humidityInfoData", c_float),
        ("crc16",            c_uint16),
        ("parity",           c_uint8*NPAR)
        ]

class HABPacketPressureInfoDataType(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("packetType",       c_uint16),
        ("pressureInfoData", c_float),
        ("crc16",            c_uint16),
        ("parity",           c_uint8*NPAR)    
        ]
    
class horusPacketV2Type(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [
        ("PayloadID", c_uint16),
        ("Counter", c_uint16),
        ("Hours",    c_uint8),
        ("Minutes", c_uint8),
        ("Seconds", c_uint8),
        ("Latitude",  c_float),
        ("Longitude", c_float),
        ("Altitude", c_uint16),
        ("Speed",  c_uint8),
        ("Sats",  c_uint8),
        ("Temp",  c_uint8),
        ("Batt",  c_uint8),
        ("CustomData",  c_uint8*CUSTOM_DATA_SIZE),
        ("Checksum", c_uint16)
        ]
    
FSK4PreamblePacket = [0xE4, 0xE4, 0xE4, 0xE4, 0xE4, 0xE4, 0xE4, 0xE4,
                      0xE4, 0xE4, 0xE4, 0xE4, 0xE4, 0xE4, 0xE4, 0xE4,
                      0xE4, 0xE4, 0xE4, 0xE4, 0xE4, 0xE4, 0xE4, 0xE4
                     ]   