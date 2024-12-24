def endecodeBattVoltage(volts):
    div = 255 / 5
    rtn = int(volts*div)
    return rtn

