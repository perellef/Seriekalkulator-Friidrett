
class Resultat:

    def __init__(self,utover,ovelse,poeng,prestasjon,dato,sted,klubb):
        
        self._utover = utover
        self._ovelse = ovelse
        self._poeng = int(poeng)
        
        self._klubb_fra = klubb # klubben resultatet ble oppnadd for
        self._klubb_til = klubb # klubben resultatet gjelder for
        self._begrunnelse = ""
        
        self._prestasjon = prestasjon
        self._dato = dato
        self._sted = sted
        
    def __eq__(self,resultat2):
        con1 = (self.hentUtover() == resultat2.hentUtover())
        con2 = (self.hentOvelse() == resultat2.hentOvelse())
        con3 = (self.hentPoeng() == resultat2.hentPoeng())
        con4 = (self.hentPrestasjon() == resultat2.hentPrestasjon())
        con5 = (self.hentDato() == resultat2.hentDato())
        con6 = (self.hentSted() == resultat2.hentSted())
        
        return all((con1,con2,con3,con4,con5,con6))

    def __lt__(self,resultat2):
        return self.hentPoeng()<resultat2.hentPoeng()

    def __gt__(self,resultat2):
        return self.hentPoeng()>resultat2.hentPoeng()

    def __ne__(self,resultat2):
        return self.hentPoeng()!=resultat2.hentPoeng()

        
    def __str__(self):
        if self._poeng==0:
            return "nullresultat"
        else:
            return str(self._poeng) + ", " + self._ovelse + " - " + self._utover.hentNavn() + " (" + str(self._utover.hentFAar()) + ")"
    
    def settBegrunnelse(self,begrunnelse):
        self._begrunnelse = begrunnelse

    def settKlubbTil(self, klubb):
        self._klubb_til = klubb
    
    def erNull(self):
        return self._poeng == 0
    
    def er(self,liste): #obl, tek eller lop
        return self._ovelse in liste
        
    def hentUtover(self):
        return self._utover
    
    def hentOvelse(self):
        return self._ovelse
    
    def hentPoeng(self):
        return self._poeng
    
    def hentPrestasjon(self):
        return self._prestasjon

    def hentDato(self):
        return self._dato
    
    def hentAar(self):
        return int(self._dato.split(".")[-1])
    
    def hentSted(self):
        return self._sted

    def hentKlubbFra(self):
        return self._klubb_fra

    def hentKlubbTil(self):
        return self._klubb_til

    def hentBegrunnelse(self):
        return self._begrunnelse
    
    def hentAlderTilUtover(self):
        return self.hentAar() - self.hentUtover().hentFAar()
        
