
from kommandosenter import Kommandosenter

import sys

class Kommandolokke:

    @staticmethod
    def start():

        kommandosenter = Kommandosenter()

        Kommandolokke.printLettVeiledning()

        hovedmeny = True
        while (hovedmeny):
            menyAar = True
            menyStatistikk = True
            prosesser = True
            filskriving = True

            Kommandolokke.printMenyAar()

            while (menyAar):

                svar = input("> ")

                if svar=="avslutt":
                    print("HANDLING: Avslutter")
                    sys.exit(0)

                if not kommandosenter.settAar(svar):
                    continue
                menyAar = False


            Kommandolokke.printMenyStatistikkhenting()

            while (menyStatistikk):

                Kommandolokke.printMenyStatistikkhandling()

                svar = input("> ")

                if svar=="avslutt":
                    print("HANDLING: Avslutter")
                    sys.exit(0)

                elif svar=="-1":
                    menyStatistikk = False
                    filskriving = False
                    prosesser = False

                elif svar=="0":      
                    menyStatistikk = False

                elif svar=="1":
                    kommandosenter.hentStatistikkTilAlleKlubber()
                    continue

                elif svar=="2":
                    kommandosenter.hentStatistikkTilKlubb()
                    continue

                elif svar=="3":
                    kommandosenter.hentStatistikkFraFil()
                    continue

                else:
                    print(f"FEIL: '{svar}' er ikke et gyldig alternativ.")
                
            if prosesser:
                kommandosenter.prosesserStatistikk()

            while filskriving:

                Kommandolokke.printMenyFilskriving()

                lagFil = True
                while (lagFil):

                    svar = input("> ")

                    if svar=="avslutt":
                        print("HANDLING: Avslutter")
                        sys.exit(0)

                    elif svar=="-1":
                        filskriving = False
                        lagFil = False

                    elif svar=="0":
                        print("HANDLING: Avslutter")
                        sys.exit(0)

                    elif svar=="1":
                        kommandosenter.lagOffisiellSerietabell()
                        continue

                    elif svar=="2":
                        kommandosenter.lagUtviklingsSerietabell()
                        continue

                    elif svar=="3":
                        kommandosenter.lagResultatFil()
                        continue

                    else:
                        print(f"FEIL: '{svar}' er ikke et gyldig alternativ.")

    @staticmethod
    def printLettVeiledning():
        print("\nLag et seriesystem på 3 steg:\n1) Velg år. NB: Sørg for å ha oppdaterte input-filer.\n2) Hent statistikk fra kommandoløkke\n3) Prosesser data fra statistikk, og hent ønskede filer")

    @staticmethod
    def printMenyAar():
        print("\nMeny Statistikkhenting\n----------------\nOppgi seriesystemets år.")

    @staticmethod
    def printMenyStatistikkhenting():
        print("\nMeny Statistikkhenting\n----------------\nVelg en av følgende handlinger:\n[-1] Gå tilbake\n[0] Gå videre\n[1] Hent all klubbstatistikk\n[2] Hent statistikk til klubb\n[3] Hent statistikk fra fil")

    @staticmethod
    def printMenyStatistikkhandling():
        print("\nVelg en handling for å hente mer statistikk. Med '0' gå videre")

    @staticmethod
    def printMenyFilskriving():
        print("\nMeny filskriving\n------------\nVelg en av følgende handlinger:\n[-1] Gå tilbake\n[0] Avslutt\n[1] Offisiell serietabell\n[2] Utviklingstabell\n[3] Resultatark")