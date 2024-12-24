import time
class cw():
    def __init__(self,
                 keyDown,
                 keyUp):
        self._keyDown   = keyDown
        self._keyUp     = keyUp
        
        self._dotLength  = .06
        self._dashLength = self._dotLength * 3
        self._pauseWords = self._dotLength * 6
        
    def _space(self):
        time.sleep(self._spaceDelay)

    def _characterSpace(self):
        time.sleep(self._pauseWords)

    def _dit(self):
        self._keyDown()
        time.sleep(self._dotLength)
        self._keyUp()
        time.sleep(.05)

    def _dash(self):
        self._keyDown()
        time.sleep(self._dashLength)
        self._keyUp()
        time.sleep(.05)

    def sendCharacter(self, c):
        uch = c.upper()
        if uch == 'A':
            self._dit()
            self._dash()
        elif uch == 'B':
            self._dash()
            self._dit()
            self._dit()
            self._dit()
        elif uch == 'C':
            self._dash()
            self._dit()
            self._dash()
            self._dit()                   
        elif uch == 'D':
            self._dash()
            self._dit()
            self._dit()
        elif uch == 'E':
            self._dit()  
        elif uch == 'F':
            self._dit()
            self._dit()
            self._dash()
            self._dit()            
        elif uch == 'G':
            self._dash()
            self._dash()
            self._dit()            
        elif uch == 'H':
            self._dit()
            self._dit()
            self._dit()
            self._dit()             
        elif uch == 'I':
            self._dit()
            self._dit()            
        elif uch == 'J':
            self._dit()
            self._dash()
            self._dash()
            self._dash()  
        elif uch == 'K':
            self._dash()
            self._dit()
            self._dash()           
        elif uch == 'L':
            self._dit()
            self._dash()
            self._dit()
            self._dit()
        elif uch == 'M':
            self._dash()
            self._dash()          
        elif uch == 'N':
            self._dash()
            self._dit()           
        elif uch == 'O':
            self._dash()
            self._dash()
            self._dash() 
        elif uch == 'P':
            self._dit()
            self._dash()
            self._dash()
            self._dit()            
        elif uch == 'Q':
            self._dash()
            self._dash()
            self._dit()
            self._dash()
        elif uch == 'R':
            self._dit()
            self._dash()
            self._dit()            
        elif uch == 'S':
            self._dit()
            self._dit()
            self._dit()
        elif uch == 'T':
            self._dash()           
        elif uch == 'U':
            self._dit()
            self._dit()
            self._dash()
        elif uch == 'V':
            self._dit()
            self._dit()
            self._dit() 
            self._dash()
        elif uch == 'W':
            self._dit()
            self._dash()
            self._dash()          
        elif uch == 'X':
            self._dash()
            self._dit()
            self._dit()
            self._dash()
        elif uch == 'Y':
            self._dash()
            self._dit()
            self._dash()
            self._dash()           
        elif uch == 'Z':
            self._dash()
            self._dash()
            self._dit()
            self._dit()
        elif uch == '1':
            self._dit()
            self._dash()
            self._dash()
            self._dash()
            self._dash()             
        elif uch == '2':
            self._dit()
            self._dit()
            self._dash()
            self._dash()
            self._dash()
        elif uch == '3':
            self._dit()
            self._dit()
            self._dit() 
            self._dash()
            self._dash()           
        elif uch == '4':
            self._dit()
            self._dit()
            self._dit()
            self._dit()            
            self._dash()
        elif uch == '5':
            self._dit()
            self._dit()
            self._dit()
            self._dit()
            self._dit()             
        elif uch == '6':
            self._dash()
            self._dit()
            self._dit()
            self._dit()
            self._dit()            
        elif uch == '7':
            self._dash()
            self._dash()
            self._dit()
            self._dit()
            self._dit()
        elif uch == '8':
            self._dash()
            self._dash()
            self._dash()
            self._dit()
            self._dit()
        elif uch == '9':
            self._dash()
            self._dash()
            self._dash()
            self._dash()            
            self._dit()            
        elif uch == '0':
            self._dash()
            self._dash()
            self._dash()
            self._dash()
            self._dash()  
                                                                                                                        
    def send(self, text):
        time.sleep(1)
        print("CW ID " + text)
        for c in text:
            self.sendCharacter(c)
            self._characterSpace()
        time.sleep(.5)
        self._keyUp()

        



