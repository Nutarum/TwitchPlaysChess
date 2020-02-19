class Utils:
    
    def loadConfig():
        f= open("config.txt")      
        f.readline()
        dragMouseDelay = f.readline()        
        f.readline()
        firefoxFolder = f.readline()
        return [dragMouseDelay,firefoxFolder]