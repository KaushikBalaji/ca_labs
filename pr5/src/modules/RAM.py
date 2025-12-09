from modules import readMemory
from modules import writeMemory

class simulatedRAM:

    def __init__(self):
        self.memory = {}
        
    def readRAM(self, addr):
        return readMemory.read(self, addr)
    
    def writeRAM(self, addr, value):
        return writeMemory.write(self, addr, value)
    
    

    
