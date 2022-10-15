
class Lag:
    
    def __init__(self,klubb,lagnr,klubbnavn):
        
        self._klubb = klubb
        self._lagnr = lagnr
        self._klubbnavn = klubbnavn
        
        self._fjoraars = {"poeng": 0, "plassering": None, "div": 3, "utvikling plassering": 0, "utvikling poeng": 0}
        self._forrige = {"poeng":0, "plassering": None, "utvikling plassering": 0, "utvikling poeng": 0}

        self._posisjon = None

        self._laginfo = {"resultater": [], "poeng": 0, "antall deltakere": 0, "antall resultater": 0, "type": "laginfo"}
        self._obl_lag = {"resultater": [], "poeng": 0, "antall deltakere": 0, "antall resultater": 0, "type": "obl lag"}
        self._val_lag = {"resultater": [], "poeng": 0, "antall deltakere": 0, "antall resultater": 0, "type": "val lag"}

    def settFjoraars(self,fjPo,fjPl,fjDiv):
        self._fjoraars["poeng"]= fjPo
        self._fjoraars["plassering"] = fjPl
        self._fjoraars["div"] = fjDiv
        
    def settForrige(self,fgPl,fgPo):
        self._forrige["poeng"] = fgPo
        self._forrige["plassering"] = fgPl
    
    def settLagoppstilling(self,obl_lag,val_lag):

        self._definerLaginfo(self._laginfo,obl_lag + val_lag)
        self._definerLaginfo(self._obl_lag,obl_lag)
        self._definerLaginfo(self._val_lag,val_lag)

    def settFjoraarsUtvikling(self,utviklingPlass,utviklingPoeng):
        self._fjoraars["utvikling plassering"] = utviklingPlass
        self._fjoraars["utvikling poeng"] = utviklingPoeng

    def settForrigeUtvikling(self,utviklingPlass,utviklingPoeng):
        self._forrige["utvikling plassering"] = utviklingPlass
        self._forrige["utvikling poeng"] = utviklingPoeng

    def _definerLaginfo(self,dict,resultater):
        
        utovere = [el.hentUtover() for el in resultater if not el.erNull()]
        
        set_utovere = []
        for utover in utovere:
            if utover not in set_utovere:
                set_utovere.append(utover)

        dict["poeng"] = sum([el.hentPoeng() for el in resultater])
        dict["antall deltakere"] = len(set_utovere)
        dict["antall resultater"] = len(utovere)

        dict["resultater"] = []
        for res in resultater:
            if not res.erNull():
                dict["resultater"].append(res)

    def __lt__(self,lag2):
        if (self.hentPoeng()!=lag2.hentPoeng()):
            return self.hentPoeng()<lag2.hentPoeng()

        resultater1 = sorted(self.hentResultater(), key = lambda x: -int(x.hentPoeng()))
        resultater2 = sorted(lag2.hentResultater(), key = lambda x: -int(x.hentPoeng()))
        
        for res1,res2 in zip(resultater1,resultater2):
            if res1!=res2:
                return res1<res2

        if self.hentFjoraars()["div"]!=lag2.hentFjoraars()["div"]:
            return self.fjoraars()["div"]>lag2.hentFjoraars()["div"]
        
        if self.hentFjoraars()["plassering"]!=lag2.hentFjoraars()["plassering"]:
            return self.fjoraars()["div"]>lag2.hentFjoraars()["div"]

        return self.hentLagnavn()>lag2.hentLagnavn()

    def hentNotat(self):
        return str(self._laginfo["antall resultater"]) + "/" +  str(self._laginfo["antall deltakere"]) 
    
    def hentOblNotat(self):
        return str(self._obl_lag["antall resultater"]) + "/" +  str(self._obl_lag["antall deltakere"]) 

    def hentValNotat(self):
        return str(self._val_lag["antall resultater"]) + "/" +  str(self._val_lag["antall deltakere"]) 

    def settPos(self,posisjon):
        self._posisjon = posisjon

    def okPos(self):
        self._posisjon += 1
        
    def senkPos(self):
        self._posisjon -= 1

    def settPlass(self,plassering):
        self._plassering = plassering

    def harTag(self,tag):
        return self._klubb.harTag(tag)

    def __str__(self):
        return self.hentLagnavn() + " (" + str(self._laginfo["poeng"]) + ")"
        
    def printLag(self):

        print("Obligatoriske Øvelser")
        for el in self._obl_lag["resultater"]:
            print(el)
            
        print("\nValgfri Øvelser")
        for el in self._val_lag["resultater"]:
            print(el)

    def hentOppstilling(self,type=None):
        if type=="obl":
            return self._obl_lag
        if type=="val":
            return self._val_lag
        if type==None:
            return self._laginfo

    def hentKjonn(self):
        return self._klubb.hentKjonn()

    def hentDiv(self):
        return self._klubb.hentDiv(self._lagnr)

    def hentPoeng(self):
        return self._laginfo["poeng"]

    def hentResultater(self):
        return self._laginfo["resultater"]

    def hentFjoraars(self):
        return self._fjoraars

    def hentFjoraarsplassering(self):

        fPlass = self._fjoraars["plassering"]
        fDiv = self._fjoraars["div"]

        if fPlass==None:
            return "-"
        if fDiv != self.hentDiv():
            return str(fPlass+1)+"/"+str(fDiv)+"d"
        return str(fPlass+1)

    def hentForrige(self):
        return self._forrige

    def hentKrets(self):
        return self._klubb.hentKrets()

    def hentLagnavn(self):
        if self._lagnr==1:
            return self._klubbnavn
        return self._klubbnavn+" "+str(self._lagnr)+". lag"

    def hentPosisjon(self):
        return self._posisjon

    def hentPlass(self):
        return self._plassering
                