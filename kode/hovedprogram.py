from _datasenter import Datasenter

from datetime import datetime

aar = "2023"

print(datetime.now(),"Initialiserer")
datasenter = Datasenter(aar)

print(datetime.now(),"Henter seriedata")
datasenter.hentSeriedata()

print(datetime.now(),"Henter tagger")
datasenter.settTagger()

print(datetime.now(),"Henter statistikk")
datasenter.hentKlubbstatistikkTilAlle("menn")
datasenter.hentKlubbstatistikkTilAlle("kvinner")

print(datetime.now(),"Korrigerer statistikk")
datasenter.korrigerKlubbStatistikk()

print(datetime.now(),"Lager resultatark")
datasenter.lagResultatFil("Resultater")

print(datetime.now(),"Beregner seriepoeng")
datasenter.beregnAlleKlubber()

print(datetime.now(),"Oppdaterer tabellhistorie")
datasenter.oppdaterTabellhistorie()

print(datetime.now(),"Lager serietabeller")
datasenter.lagOffisiellSerietabell(f"Lagserien {aar}")

print(datetime.now(),"Ferdig")