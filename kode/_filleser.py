import json
import numpy as np
import pandas as pd
from datetime import datetime

class Filleser:

    @staticmethod
    def json(filnavn):

        streng = ""
        with open(filnavn + '.json', encoding='utf-8') as fil:
            for linje in fil:
                streng += linje.strip()

        return json.loads(streng)

    @classmethod
    def fjorarstabell(cls,datasenter):

        aar = int(datasenter.aar())

        fjorarsfil = f"./data/serietabell_{aar-1}.txt"

        ###### hvis filen ikke finnes ma handteres
        
        data = []
        try:
            with open(fjorarsfil,"r",encoding="utf8") as fil:
                for linje in fil:
                    data.append(linje.strip().split("|"))

        except FileNotFoundError:
            print(f"MERKNAD: Fant ingen fjoraarstabell ('{fjorarsfil}'). Fortsetter uten.")
            return

        for linje in data:

            kj = linje[0]
            poeng = int(linje[3])
            plassering = int(linje[2])
            div = int(linje[1])
            lagnavn = linje[4]

            klubbnavn, lag_nr = cls._hentInfoFraLagnavn(lagnavn)

            klubb = datasenter.hentKlubbFraNavn(kj,klubbnavn,lagNy=False)
            lag = klubb.hentLag(lag_nr)
            lag.settFjoraars(poeng,plassering,div)

            opprykk = (div in [2,3]) and (plassering <=3)
            nedrykk = (div in [1,2]) and (plassering >=10)

            if opprykk:
                div -= 1
            if nedrykk:
                div += 1

            klubb.leggTilDiv(div)   

            
    @classmethod
    def tabellhistorie(cls,datasenter):
        
        aar = datasenter.aar()

        tabellhistorie = f"./data/tabellhistorie_{aar}.txt"

        data = {}
        try:
            with open(tabellhistorie,"r",encoding="utf8") as fil:
                
                for linje in fil:
                    if linje[0]=="|":
                        tidspunkt = linje.split("|")[1]
                        tabell = []

                        data[tidspunkt] = tabell
                    else:
                        tabell.append(linje.strip().split("|"))
        except FileNotFoundError:
            print(f"MERKNAD: Fant ingen tabellhistorie ('{tabellhistorie}'). Fortsetter uten.")
            return

        na = datetime.now()

        tabell = []
        for tidspunkt in data:

            tabellTid = datetime.strptime(tidspunkt, "%Y-%m-%d %H:%M:%S.%f")

            dagerSiden = (na - tabellTid).days + (na - tabellTid).seconds/(24*60*60)

            if dagerSiden > 14*0.97:
                tabell = data[tidspunkt]
        
        for linje in tabell:

            lagnavn = linje[4]
            klubbnavn,lag_nr = cls._hentInfoFraLagnavn(lagnavn)

            kj = linje[0]
            poeng = int(linje[3])
            plassering = int(linje[2])
            div = int(linje[1])
            
            klubb = datasenter.hentKlubbFraNavn(kj,klubbnavn,lagNy=False)
            klubb.leggTilDiv(div)   
            
            lag = klubb.hentLag(lag_nr)
            lag.settForrige(poeng,plassering)

    @staticmethod
    def _hentInfoFraLagnavn(lagnavn):

        lag_nr = 1
        klubbnavn = lagnavn
        if len(klubbnavn)>7:
            if klubbnavn[-5:] == ". lag":
                lag_nr = int(klubbnavn[-6])

                klubbnavn = klubbnavn[:-7]     
        try:
            klubbnavn = klubbnavn.encode('latin1').decode('utf8')
        except (UnicodeEncodeError,UnicodeDecodeError):
            klubbnavn = klubbnavn.replace("Ã…","Å")

        return klubbnavn,lag_nr