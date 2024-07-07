from _klubb import Klubb
from _utover import Utover
from _resultater import Resultater
from _tabell import Tabell

from _filleser import Filleser
from _filskriver import Filskriver
from _statistikkhenting import Statistikkhenting
from _resultatbehandling import Resultatbehandling
from _kalkulator import Kalkulator

from datetime import datetime
import time


class Datasenter:

    def __init__(self,aar):
        self._kretsserien = False

        self._aar = aar
        self._initieringTid = datetime.now()

        settingfil = "settinger"
        if self._kretsserien:
            settingfil = "settinger_kretsserie"
        self._settinger = Filleser.json(f"./konfig/{aar}/{settingfil}")
        self._ovelsesinfo = Filleser.json(f"./konfig/{aar}/ovelsesinfo")
        self._resultatavvik = Filleser.json(f"./konfig/{aar}/resultatavvik")
        self._innstillinger = Filleser.json(f"./konfig/innstillinger")

        self._utovere = {"menn": [], "kvinner": []}
        self._resultater = {"menn": Resultater(),"kvinner": Resultater()}

        klubberMenn = []
        klubberKvinner = []

        self._klubber = {"menn": klubberMenn, "kvinner": klubberKvinner}
        self._tabell = {"menn": Tabell(self), "kvinner": Tabell(self)}

    def kjor_og_last(self, kjonn=["menn","kvinner"], klubber=[]):

        self.hentSeriedata()
        self.settTagger()

        for kj in kjonn:
            if not klubber:
                self.hentKlubbstatistikkTilAlle(kj)
            else:
                for klubbid in klubber:
                    klubb = self.hentKlubbFraID(kj, klubbid)
                    self.hentKlubbstatistikk(klubb)
                    for overb_klubb in self.hentOverbygningsklubberTilKlubb(klubb):
                        self.hentKlubbstatistikk(overb_klubb)

        self.korrigerKlubbStatistikk()
        self.lagResultatFil()
        self.beregnAlleKlubber()
        self.oppdaterTabellhistorie()
        self.lagOffisiellSerietabell()

        print(datetime.now(),"Ferdig")

    def __str__(self):

        antallLagMenn = sum(len(klubb.hentAlleLag()) for klubb in self._klubber["menn"])
        antallLagKvinner = sum(len(klubb.hentAlleLag()) for klubb in self._klubber["kvinner"])

        return (f"Datasenter:\nMenn:    | {len(self._klubber['menn'])} klubber, {antallLagMenn} lag, "
              + f"{len(self._utovere['menn'])} utovere, {len(self._resultater['menn'])} resulater |"
              + f"\nKvinner: | {len(self._klubber['kvinner'])} klubber, {antallLagKvinner} lag, "
              + f"{len(self._utovere['kvinner'])} utovere, {len(self._resultater['kvinner'])} resultater |")

    def hentSeriedata(self):
        print(datetime.now(),"Henter seriedata")
        Statistikkhenting.definerKlubbIDer(self)
        Filleser.fjorarstabell(self)
        Filleser.tabellhistorie(self)

    def settTagger(self):
        print(datetime.now(),"Sett tagger")
        for tag,klubbdata in self._settinger["tagger"].items():
            for klubbnavn,kjonn in klubbdata:
                klubb = self.hentKlubbFraNavn(kjonn,klubbnavn,lagNy=False)
                klubb.settTag(tag)


    def hentKlubbstatistikk(self,klubb):
        print(datetime.now(),f"Henter klubbstatistikk til {klubb}")
        Statistikkhenting.hentKlubbstatistikk(self,klubb)

    def hentKlubbstatistikkTilAlle(self,kjonn):
        print(datetime.now(),f"Henter all klubbstatistikk til {kjonn}")
        i = 0
        for klubb in self._klubber[kjonn]:
            if i%250==0:
                print(f"{i}/{len(self._klubber[kjonn])} ({kjonn})",datetime.now())
            Statistikkhenting.hentKlubbstatistikk(self,klubb)

            i+= 1

    def hentStatistikkFraFil(self,filnavn):
        Statistikkhenting.hentStatistikkFraFil(self,filnavn)

    def korrigerKlubbStatistikk(self):
        print(datetime.now(),"Korrigerer statistikk")

        for kjonn in ["menn","kvinner"]:

            Resultatbehandling.hentManueltManglendeRes(self,kjonn)
            Resultatbehandling.fjernManueltUgyldigeRes(self,kjonn)
            
            if (self._settinger["tillat mellomtider"]):
                Resultatbehandling.fjernMellomtiderTilSerieres(self,kjonn)
            else: 
                Resultatbehandling.fjernMellomtider(self,kjonn)

            Resultatbehandling.fjernManuelleResultater(self,kjonn)
            Resultatbehandling.fjernForUngeUtovere(self,kjonn)
            Resultatbehandling.fjernRullestolutovere(self,kjonn)
            Resultatbehandling.flyttOverbygningsresultater(self,kjonn)
            Resultatbehandling.handterKlubberUnntattOverbygning(self,kjonn)

    def beregnKlubb(self,klubb):
        if self._kretsserien and klubb._krets != "Hordaland":
            return

        start = time.time()
        try:
            Kalkulator.LagKalk(self,klubb)
        except Exception:
            print(datetime.now(), f"Feil ved beregning av poeng til '{klubb}'.")
            raise ValueError
        
        end = time.time()

        if klubb.hentLag(1)._laginfo["poeng"]>0:
            print(datetime.now(), klubb,klubb.hentLag(1)._laginfo["poeng"])
        
        minutter_brukt = (end - start)//60
        if minutter_brukt > 3:
            print(datetime.now(), f"Beregning av '{klubb}' krevde {minutter_brukt} minutter.")


    def beregnAlleKlubber(self):
        print("Beregner seriepoeng")
        for kjonn in ["menn","kvinner"]:
            for klubb in self._klubber[kjonn]:
                self.beregnKlubb(klubb)

    def oppdaterTabellhistorie(self):
        print(datetime.now(),"Oppdaterer tabellhistorie")
        Filskriver.tabellhistorie(self)

    def lagOffisiellSerietabell(self):
        print(datetime.now(),"Lager serietabeller")
        Filskriver.offisieltSerieark(self,f"Lagserien {self._aar}")

    def lagUtviklingsSerietabell(self,filnavn):
        print(datetime.now(),"Lager utviklingsserietabell")

    def lagResultatFil(self):
        print(datetime.now(),"Lager resultatark")
        Filskriver.resultatark(self,"Resultater")

    def hentOverbygningsklubberTilKlubb(self, klubb):
        kjonn = klubb.hentKjonn()
        overb_klubber = []
        
        klubber = self._resultatavvik["overbygningsklubber"]
        try:
            for klubbnavn in klubber[klubb.hentKlubbnavn()][1]:
                klubb = self.hentKlubbFraNavn(kjonn, klubbnavn, lagNy=False)
                overb_klubber.append(klubb)
        except KeyError:
            pass
        return overb_klubber

    def hentAlleKretser(self):

        kretser = []

        for kjonn in ["menn","kvinner"]:
            for klubb in self._klubber[kjonn]:

                con1 = ((krets := klubb.hentKrets()) not in kretser)
                con2 = (krets!=None)
                con3 = (len(klubb.hentAlleLag())>0)

                if all((con1,con2,con3)):
                    kretser.append(krets)

        return sorted(kretser)

    def hentKlubbFraNavn(self,kjonn,klubbnavn,lagNy=True):
        
        for klubb in self._klubber[kjonn]:            
            if klubb.hentKlubbnavn()==klubbnavn:
                return klubb

        if not lagNy:
            raise NameError(f"Klubb med navn '" + klubbnavn + "' finnes ikke")
            
        klubb = Klubb(kjonn,klubbnavn)
        self._klubber[kjonn].append(klubb)
        
        return klubb        

    def hentKlubbFraID(self,kjonn,ID):

        for klubb in self._klubber[kjonn]:            
            if klubb.hentID()==ID:
                return klubb

        raise NameError(f"Klubb med ID '" + ID + "' finnes ikke")
    
    def hentUtover(self,kjonn,navn,fodselsaar):
        
        fodselsaar = int(fodselsaar)
        
        for utover in self._utovere[kjonn]:
            if utover.hentNavn()==navn and utover.hentFAar()==fodselsaar:
                return utover
        
        utover = Utover(kjonn,navn,fodselsaar)
        self._utovere[kjonn].append(utover)
        
        return utover

    def leggTilRes(self,kjonn,resultat):
        self._resultater[kjonn].append(resultat)


    def utovere(self,kjonn):
        return self._utovere[kjonn]

    def resultater(self,kjonn):
        return self._resultater[kjonn]

    def klubber(self,kjonn):
        return self._klubber[kjonn]

    def tabell(self,kjonn):
        return self._tabell[kjonn]


    def settinger(self):
        return self._settinger

    def resultatavvik(self):
        return self._resultatavvik

    def ovelsesinfo(self):
        return self._ovelsesinfo
    
    def innstillinger(self):
        return self._innstillinger


    def inititieringTid(self):
        return self._initieringTid

    def aar(self):
        return self._aar
            