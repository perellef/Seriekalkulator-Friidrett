from klubb import Klubb
from utover import Utover
from resultater import Resultater
from tabell import Tabell

from filleser import Filleser
from filskriver import Filskriver
from statistikkhenting import Statistikkhenting
from resultatbehandling import Resultatbehandling
from kalkulator import Kalk

import asyncio
from datetime import datetime


class Datasenter:

    def __init__(self,aar):

        self._aar = aar
        self._initieringTid = datetime.now()

        self._settinger = Filleser.json(f"settinger_{aar}")
        self._ovelsesinfo = Filleser.json(f"ovelsesinfo_{aar}")
        self._resultatavvik = Filleser.json(f"resultatavvik_{aar}")

        self._utovere = {"menn": [], "kvinner": []}
        self._resultater = {"menn": Resultater(),"kvinner": Resultater()}

        klubberMenn = []
        klubberKvinner = []

        self._klubber = {"menn": klubberMenn, "kvinner": klubberKvinner}
        self._tabell = {"menn": Tabell(self), "kvinner": Tabell(self)}

    def __str__(self):

        antallLagMenn = sum(len(klubb.hentAlleLag()) for klubb in self._klubber["menn"])
        antallLagKvinner = sum(len(klubb.hentAlleLag()) for klubb in self._klubber["kvinner"])

        return (f"Datasenter:\nMenn:    | {len(self._klubber['menn'])} klubber, {antallLagMenn} lag, "
              + f"{len(self._utovere['menn'])} utovere, {len(self._resultater['menn'])} resulater |"
              + f"\nKvinner: | {len(self._klubber['kvinner'])} klubber, {antallLagKvinner} lag, "
              + f"{len(self._utovere['kvinner'])} utovere, {len(self._resultater['kvinner'])} resultater |")

    def hentSeriedata(self):
        Statistikkhenting.definerKlubbIDer(self)
        Filleser.fjorarstabell(self)
        Filskriver.tabellhistorie(self)
    
    def hentKlubbstatistikk(self,klubb):
        Statistikkhenting.hentKlubbstatistikk(self,klubb)

    def hentKlubbstatistikkTilAlle(self,kjonn):

        i = 0
        for klubb in self._klubber[kjonn]:
            if i%250==0:
                print(f"{i}/{len(self._klubber[kjonn])} ({kjonn})",datetime.now())
            self.hentKlubbstatistikk(klubb)

            i+= 1

    def hentStatistikkFraFil(self,filnavn):
        Statistikkhenting.hentStatistikkFraFil(self,filnavn)

    def korrigerKlubbStatistikk(self): 

        for kjonn in ["menn","kvinner"]:

            Resultatbehandling.hentManueltManglendeRes(self,kjonn)
            Resultatbehandling.fjernManueltUgyldigeRes(self,kjonn)
            Resultatbehandling.fjernManuelleResultater(self,kjonn)
            
            if (self._settinger["tillat mellomtider"]):
                Resultatbehandling.fjernMellomtiderTilSerieres(self,kjonn)
            else: 
                Resultatbehandling.fjernMellomtider(self,kjonn)

            Resultatbehandling.fjernForUngeUtovere(self,kjonn)
            Resultatbehandling.fjernRullestolutovere(self,kjonn)
            Resultatbehandling.flyttOverbygningsresultater(self,kjonn)
            Resultatbehandling.handterKlubberUnntattOverbygning(self,kjonn)

    def beregnKlubb(self,klubb):
        print(klubb,datetime.now())
        Kalk.LagKalk(self,klubb)
        print(klubb,datetime.now())

    def beregnAlleKlubber(self):
        for kjonn in ["menn","kvinner"]:
            for klubb in self._klubber[kjonn]:
                print(klubb,datetime.now())
                Kalk.LagKalk(self,klubb)

    def lagOffisiellSerietabell(self,filnavn):
        Filskriver.offisieltSerieark(self,filnavn)

    def lagUtviklingsSerietabell(self,filnavn):
        print("utviklingsserietabell")

    def lagResultatFil(self,filnavn):
        Filskriver.resultatark(self,filnavn)

    def hentAlleKretser(self):

        kretser = []

        for kjonn in ["menn","kvinner"]:
            for klubb in self._klubber[kjonn]:

                con1 = ((krets := klubb.hentKrets()) not in kretser)
                con2 = (krets!=None)

                if all((con1,con2)):
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


    def inititieringTid(self):
        return self._initieringTid

    def aar(self):
        return self._aar
            