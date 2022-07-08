from resultater import Resultater
from lag import Lag

class Klubb:
    
    def __init__(self,kjonn,klubbnavn):
        self._lag = []
        self._klubbdivs = []
        self._statistikk = [] # brukes ikke per na
        self._resultater = Resultater()
        
        self._kjonn = kjonn
        self._klubbnavn = klubbnavn
        self._ID = None
        self._krets = None
        
    def __str__(self):
        return self._klubbnavn+" ("+self._kjonn+")"
        
    def settKrets(self,krets):
        self._krets = krets
        
    def harID(self):
        return self._ID != None

    def harResultater(self):
        return len(self._resultater)>0

    def settID(self,ID):
        self._ID = ID
        
    def leggTilDiv(self,div):        
        self._klubbdivs = sorted(self._klubbdivs + [div])
    
    def leggTilRes(self,res):
        self._resultater.append(res)
        
    def fjernRes(self,res):
        self._resultater.remove(res)
        
    def hentDiv(self,lag_nr):
        if len(self._klubbdivs)>=lag_nr:
            return self._klubbdivs[lag_nr-1]
        else:
            return 3
        
    def hentAlleLag(self):
        return self._lag
        
    def hentLag(self,lag_nr):
        while len(self._lag)<lag_nr:   
            nyttLagNr = len(self._lag)+1
            nyttLag = Lag(self,nyttLagNr,self._klubbnavn)

            self._lag.append(nyttLag)
        return self._lag[lag_nr-1]
        
    def hentKjonn(self):
        return self._kjonn
        
    def hentID(self):
        return self._ID
    
    def hentResultater(self):
        return self._resultater
        
    def hentKlubbnavn(self):
        return self._klubbnavn

    def hentKrets(self):
        return self._krets
        