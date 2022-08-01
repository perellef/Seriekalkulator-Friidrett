from _resultater import Resultater

class Utover:

    def __init__(self,kjonn,navn,fodselsaar):

        self._kjonn = kjonn
        self._navn = navn
        self._fodselsaar = fodselsaar
        self._resultater = Resultater()
        
    def __eq__(self,utover2):
        return self.hentNavn()==utover2.hentNavn() and self.hentFAar()==utover2.hentFAar()
    
    def __str__(self):
        if self.erNull():
            return "nullutøver"
        return self._navn + " (" + str(self._fodselsaar) + ")"

    def __hash__(self):
        return hash(self._resultater)

    def leggTilRes(self,resultat):
        self._resultater.append(resultat)

    def fjernRes(self,resultat):
        self._resultater.remove(resultat)
    
    def erNull(self):
        return self._navn==None
        
    def hentNavn(self):
        return self._navn
    
    def hentFAar(self):
        return self._fodselsaar
    
    def hentKjonn(self):
        return self._kjonn
    
    def hentResultater(self):
        return self._resultater