from bs4 import BeautifulSoup
import requests

from resultat import Resultat

url = "http://www.minfriidrettsstatistikk.info/php/SeriePoengPrKlubb.php"

class Statistikkhenting:

    @staticmethod
    def definerKlubbIDer(datasenter):
                
        try:
            data = BeautifulSoup(requests.get(url, timeout=5).text, "lxml")
        except (requests.ConnectionError, requests.Timeout):
            print(f"Mangler nett-tilgang og får ikke hentet klubbid-er.")
            return      
        klubber = data.find("select",{"name":"showclub"})
        
        unnga = True
        for html_linje in klubber:
            
            if unnga:
                unnga = False
                continue

            ID = html_linje["value"]
            klubbnavn = str(html_linje).replace('<option value="'+ID+'">','').replace('</option>','')

            klubbnavn = klubbnavn.replace("&amp;","&")
            
            for kjonn in ["menn","kvinner"]:
            
                klubb = datasenter.hentKlubbFraNavn(kjonn,klubbnavn)
                klubb.settID(ID)

    @staticmethod
    def hentKlubbstatistikk(datasenter,klubb):

        ovelsesinfo = datasenter.ovelsesinfo()
        
        ovelser_statistikk = ovelsesinfo["i statistikk"]
        ovelser_sluttform = ovelsesinfo["sluttform"]
        
        ID = klubb.hentID()
        kjonn = klubb.hentKjonn()
        aar = datasenter.aar()
        
        gender = "M" if kjonn=="menn" else "W" if kjonn=="kvinner" else None
            
        inputs = {'showclub': ID, 'showgender': gender, 'showyear': str(aar), "submit": "BEREGN"}

        while True:
            
            try:
                data = BeautifulSoup(requests.post(url, data=inputs, timeout=5).text, "lxml")
            except (requests.ConnectionError, requests.Timeout):
                print(f"Mangler nett-tilgang og får ikke hentet statistikk til {klubb}.")
                return                       
            all_data = data.findAll("table",{"id":"liten"})
            
            try:
                samlet_indiv_data = all_data[1].findAll("tr")[1:]
                break
            except IndexError:
                continue
            
        lag_data = [el.text for el in all_data[0].findAll("td")]
        
        klubb.settKrets(lag_data[1].replace(" Friidrettskrets",""))  
        
            
        data = [[el.text for el in indiv_data.findAll("td")] for indiv_data in samlet_indiv_data]            
            
        for ovelse,navn,fAar,res,poeng,sted,dato in data:
            
            skip = False
            for i in range(len(ovelser_statistikk)):
                for ov_st in ovelser_statistikk[i]:
                    if ov_st == ovelse:
                        ovelse = list(ovelser_sluttform.keys())[i]
                        skip = True
                        break
                if skip:
                    break
            
            utover = datasenter.hentUtover(kjonn,navn,fAar)
            
            resultat = Resultat(utover,ovelse,poeng,res,dato,sted,klubb)

            utover.leggTilRes(resultat)
            klubb.leggTilRes(resultat)
            datasenter.leggTilRes(kjonn,resultat)       

    def hentStatistikkFraFil(datasenter,filnavn):

        ...