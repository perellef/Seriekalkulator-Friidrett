from datasenter import Datasenter

import os
import requests
import sys

url = "http://www.minfriidrettsstatistikk.info/php/SeriePoengPrKlubb.php"

class Kommandosenter:

    def __init__(self):
        self._hentetKlubbIDer = False

    def settAar(self,aar):
        
        con1 = aar.isdigit()

        if not con1:
            print("FEIL: Et heltall må velges")
            return False

        con2 = os.path.exists(f"settinger_{aar}.json")
        con3 = os.path.exists(f"ovelsesinfo_{aar}.json")
        con4 = os.path.exists(f"resultatavvik_{aar}.json")

        for con,fil in zip([con2,con3,con4],["settinger","ovelsesinfo","resultatavvik"]):
            if not con:
                print(f"FEIL: '{fil}_{aar}.json' eksisterer ikke")
                return False

        self._datasenter = Datasenter(aar)

        return True

    def velgStatistikkHandling(self):
        handling = input("> ")

        if handling not in ["-1","0","1","2","3"]:
            print(f"FEIL: Mulige handlinger er -1, 0, 1, 2 og 3, ikke '" + handling + "'")
            return None

        return handling
    
    def hentStatistikkTilAlleKlubber(self):

        try:
            requests.get(url, timeout=5)
        except (requests.ConnectionError, requests.Timeout) as exception:
            print("FEIL: Mangler nett-tilgang.")
            return

        if not self._hentetKlubbIDer:
            print("\nHANDLING: Klargjør seriesystem.")
            self._datasenter.hentSeriedata()
            self._hentetKlubbIDer = True

        print("\nVelg kjonn:\n[1] 'menn'\n[2] 'kvinner'\n [3] 'begge'")

        while (True):

            svar= input("> ")

            if svar=="avslutt":
                print("HANDLING: Avslutter")
                sys.exit()

            if svar=="-1":
                return

            if svar not in ["1","2","3","menn","kvinner","begge"]:
                print(f"FEIL: {svar} er ikke et gyldig alternativ.")
                continue

            print(f"HANDLING: Klubbstatistikk til alle klubber ({svar}) hentes")
            self._datasenter.hentKlubbstatistikkTilAlle()

            if svar in ["1","menn","3","begge"]:
                self._datasenter.hentKlubbstatistikkTilAlle("menn")
            elif svar in ["2","kvinner"]:
                self._datasenter.hentKlubbstatistikkTilAlle("kvinner")
            
    def hentStatistikkTilKlubb(self):

        try:
            requests.get(url, timeout=5)
        except (requests.ConnectionError, requests.Timeout) as exception:
            print("FEIL: Mangler nett-tilgang.")
            return

        if not self._hentetKlubbIDer:
            print("HANDLING: Klargjør seriesystem.")
            self._datasenter.hentSeriedata()
            self._hentetKlubbIDer = True

        print("\nVelg kjonn:\n[1] 'menn'\n[2] 'kvinner'")

        while (True):

            svar= input("> ")

            if svar=="avslutt":
                print("HANDLING: Avslutter")
                sys.exit()

            elif svar=="-1":
                return

            elif svar not in ["1","2","menn","kvinner"]:
                print(f"FEIL: {svar} er ikke et gyldig alternativ.")
                continue

            if svar in ["1","menn"]:
                kjonn = "menn"
            elif svar in ["2","kvinner"]:
                kjonn = "kvinner"

            print("\nVelg klubb ved å oppgi klubbnavn eller id.")

            while (True):

                svar = input("> ")

                if svar=="avslutter":
                    print("HANDLING: Avslutter")
                    sys.exit()

                if svar=="-1":
                    return

                if svar.isdigit():
                    try:
                        klubb = self._datasenter.hentKlubbFraID(kjonn,svar)
                    except NameError:
                        print("FEIL: Klubb med gitt ID finnes ikke")
                        continue
                else:
                    try:
                        klubb = self._datasenter.hentKlubbFraNavn(kjonn,svar,lagNy=False)
                    except NameError:
                        print("FEIL: Klubb med gitt navn finnes ikke")
                        continue

                print(f"HANDLING: Statistikk fra {klubb} hentes.")
                self._datasenter.hentKlubbstatistikk(klubb)
                return

    def hentStatistikkFraFil(self):

        print("\nOppgi filnavn til filen det skal hentes statistikk fra (eksempel: 'test', som leser filen test.xlsx)")

        while (True):

            svar= input("> ")

            if svar=="avslutt":
                print("HANDLING: Avslutter")
                sys.exit()

            if svar=="-1":
                return

            if not os.path.exists(f"{svar}.xlsx"):
                print("FEIL: Filen eksisterer ikke.")
                continue

            try:
                self._datasenter.lesStatistikkFraFil(svar + ".xlsx")
            except SystemError:
                print("Feil: Oppgitt fil har feil filformat.")
                continue
 
            print(f"Statistikk fra {svar}.xlsx hentet.!")
            return

    def prosesserStatistikk(self):
        self._datasenter.korrigerKlubbStatistikk()
        self._datasenter.beregnAlleKlubber()

    def lagOffisiellSerietabell(self):

        aar = self._datasenter.aar()

        i = 97
        for m in range(26):
            for n in range(26):
                filnavn = f"serietabell {aar} ({chr(i+m)}{chr(i+n)})"

                if any((os.path.exists(f"{filnavn} 1-2. div.xlsx"),
                        os.path.exists(f"{filnavn} menn 3. div.xlsx"),
                        os.path.exists(f"{filnavn} kvinner 3. div.xlsx")
                    )):
                    continue

                self._datasenter.lagOffisiellSerietabell(filnavn)
                print("HANDLING: Setter opp serieark.")
                return
        
        print("FEIL: Fant ingen ledige filnavn.")
    
    def lagUtviklingsSerietabell(self):

        filnavn = "utv_serietabell"

        print("'Lager serietabell med utvikling'")

        #while True:
        #    self._datasenter.lagUtviklingsSerietabell(filnavn)
        #    break

    def lagResultatFil(self):

        aar = self._datasenter.aar()

        i = 97
        for m in range(26):
            for n in range(26):
                filnavn = f"resultatark {aar} ({chr(i+m)}{chr(i+n)})"

                if os.path.exists(f"{filnavn}.xlsx"):
                    continue

                self._datasenter.lagResultatFil(filnavn)
                print("HANDLING: Setter opp resultatark.")
                return
        
        print("FEIL: Fant ingen ledige filnavn.")
            