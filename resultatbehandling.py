from resultat import Resultat

class Resultatbehandling:  

    @staticmethod
    def hentManueltManglendeRes(datasenter,kjonn):
        
        resultatavvik = datasenter.resultatavvik()
        manglende_res = resultatavvik["manglende resultater"][kjonn]
        
        for resultat in manglende_res:
            
            klubbnavn,navn,fAar,poeng,ovelse,res,sted,dato = resultat["resultat"]
            
            klubb = datasenter.hentKlubbFraNavn(kjonn,klubbnavn,lagNy=False)
            utover = datasenter.hentUtover(kjonn,navn,fAar)
            
            res = Resultat(utover,ovelse,poeng,res,dato,sted,None)
            
            klubb.leggTilRes(res)
            utover.leggTilRes(res)
            
            res.settKlubbTil(klubb)
            res.settBegrunnelse(resultat["begrunnelse"])
            

    @staticmethod
    def fjernManueltUgyldigeRes(datasenter,kjonn):

        resultatavvik = datasenter.resultatavvik()
        ugyldige_res = resultatavvik["ugyldige resultater"][kjonn]
        
        for resultat in ugyldige_res:
            
            klubbnavn,navn,fAar,poeng,ovelse,pres,sted,dato = resultat["resultat"]
            
            klubb = datasenter.hentKlubbFraNavn(kjonn,klubbnavn,lagNy=False)
            utover = datasenter.hentUtover(kjonn,navn,fAar)
            
            resultater = klubb.hentResultater()

            for res in reversed(resultater):
            
                con1 = (res.hentUtover() is utover)
                con2 = (res.hentPoeng()==int(poeng))
                con3 = (res.hentOvelse()==ovelse)
                con4 = (res.hentPrestasjon()==pres)
                con5 = (res.hentSted()==sted)
                con6 = (res.hentDato()==dato)
                
                if all((con1,con2,con3,con4,con5,con6)):
                       
                    klubb.fjernRes(res)
                    utover.fjernRes(res)

                    res.settKlubbTil(None)
                    res.settBegrunnelse(resultat["begrunnelse"])
                    break

    @staticmethod
    def fjernMellomtider(datasenter,kjonn):

        klubber = datasenter.klubber(kjonn)
        
        for klubb in klubber:
            resultater = klubb.hentResultater()
            for res in reversed(resultater):
                prestasjon = res.hentPrestasjon()

                if "+" in prestasjon:
                    klubb = res.hentKlubbFra()
                    utover = res.hentUtover()

                    klubb.fjernRes(res)
                    utover.fjernRes(res)

                    res.settKlubbTil(None)
                    res.settBegrunnelse("Mellomtid")

                
    @staticmethod
    def fjernMellomtiderTilSerieres(datasenter,kjonn):

        utovere = datasenter.utovere(kjonn)
        ovelsesinfo = datasenter.ovelsesinfo()["sluttform"]

        for utover in utovere:
            resultater = utover.hentResultater()

            for res1 in reversed(resultater):
                
                ovelse1 = res1.hentOvelse()
                prestasjon = res1.hentPrestasjon()

                con1 = ("mellomtid" in ovelsesinfo[ovelse1])
                con2 = ("+" in prestasjon)

                if not all((con1,con2)):
                    continue

                for res2 in resultater:

                    ovelse2 = res2.hentOvelse()

                    con3 = (res2.hentDato()==res1.hentDato())
                    con4 = (res2.hentSted()==res1.hentSted())
                    con5 = (res2.hentUtover() is utover)
                    con6 = ("mellomtid" in ovelsesinfo[ovelse2])

                    if not all((con3,con4,con5,con6)):
                        continue

                    ovelsestype1, dist1 = ovelsesinfo[ovelse1]["mellomtid"]
                    ovelsestype2, dist2 = ovelsesinfo[ovelse2]["mellomtid"]

                    con7 = (ovelsestype1==ovelsestype2)
                    con8 = (dist1<dist2) # kortere distanse

                    if not all((con7,con8)):
                            continue

                    # ma være mellomtid til serieovelse og skal derfor fjernes

                    klubb = res1.hentKlubbFra()

                    klubb.fjernRes(res1)
                    utover.fjernRes(res1)

                    res1.settKlubbTil(None)
                    res2.settBegrunnelse("Mellomtid til et serieresultat")
                    break
                        
    @staticmethod    
    def fjernForUngeUtovere(datasenter,kjonn):

        settinger = datasenter.settinger()
        klubber = datasenter.klubber(kjonn)

        min_alder = settinger["aldersgrense for deltakelse"]
        
        for klubb in klubber:
            resultater = klubb.hentResultater()
            for res in reversed(resultater):
                alder = res.hentAlderTilUtover()
                        
                con1 = (alder<min_alder)
                con2 = (alder>0) 

                if all((con1,con2)):

                    klubbFra = res.hentKlubbFra()
                    utover = res.hentUtover()

                    klubbFra.fjernRes(res)
                    utover.fjernRes(res)

                    res.settKlubbTil(None)
                    res.settBegrunnelse(f"Resultat til en for ung utøver (<{min_alder})")
                
    @staticmethod      
    def fjernRullestolutovere(datasenter,kjonn):

        resultatavvik = datasenter.resultatavvik()
        rullestolutovere = resultatavvik["rullestolutøvere"][kjonn]
        
        for rull_utover in rullestolutovere:
            
            navn,fAar = rull_utover.split("/")
            utover = datasenter.hentUtover(kjonn,navn,fAar)
            
            utoverRes = utover.hentResultater()
            
            for res in utoverRes:
                klubb = res.hentKlubbFra()
                
                klubb.fjernRes(res)
                utover.fjernRes(res)
                
                res.settKlubbTil(None)
                res.settBegrunnelse("Resultat av en rullestolutøver")     
            
    @staticmethod
    def flyttOverbygningsresultater(datasenter,kjonn):

        resultatavvik = datasenter.resultatavvik()

        overbygning = resultatavvik["overbygningsklubber"]
        utovereUnntatt = resultatavvik["utøvere unntatt overbygning"][kjonn]
        
        for overbygKlubbnavn in overbygning:
            
            overbygKlubb = datasenter.hentKlubbFraNavn(kjonn,overbygKlubbnavn,lagNy=False)
            
            alder_krav, moderklubber = overbygning[overbygKlubbnavn]
            
            for moderklubbnavn in moderklubber:

                utovere_unntatt = []
                if moderklubbnavn in utovereUnntatt: # finner alle unntatte utovere i klubben
                    for el in utovereUnntatt[moderklubbnavn]:
                        navn,fAar = el.split("/")

                        utover = datasenter.hentUtover(kjonn,navn,fAar)

                        utovere_unntatt.append(utover)

                moderKlubb = datasenter.hentKlubbFraNavn(kjonn,moderklubbnavn,lagNy=False)
                
                resultater = moderKlubb.hentResultater()
                
                for res in reversed(resultater):

                    utover = res.hentUtover()
                    alder = res.hentAlderTilUtover()
                    
                    condition1 = (utover in utovere_unntatt)
                    
                    con1 = (alder_krav[0] and alder in [11,12,13,14])
                    con2 = (alder_krav[1] and alder in [15,16,17,18,19])
                    con3 = (alder_krav[2] and alder>=20)
                    
                    condition2 = any((con1,con2,con3))

                    if all((condition1,condition2)):
                        res.settBegrunnelse("Utøver unntatt overbygning")
                    
                    elif all((not condition1,condition2)):
                        
                        overbygKlubb.leggTilRes(res)
                        moderKlubb.fjernRes(res)

                        res.settKlubbTil(overbygKlubb)
                        res.settBegrunnelse("Overbygning")  

    @staticmethod        
    def handterKlubberUnntattOverbygning(datasenter,kjonn):

        resultatavvik = datasenter.resultatavvik()
        klubberUnntatt = resultatavvik["klubber unntatt overbygning"]
        
        for overbygKlubbnavn in klubberUnntatt:

            overbygKlubb = datasenter.hentKlubbFraNavn(kjonn,overbygKlubbnavn,lagNy=False)
            alder_krav = klubberUnntatt[overbygKlubbnavn][0]

            moderklubber = klubberUnntatt[overbygKlubbnavn][1]

            for moderKlubbnavn in moderklubber:
                moderklubb = datasenter.hentKlubbFraNavn(kjonn,moderKlubbnavn,lagNy=False)

                klubbResultater = moderklubb.hentResultater() # henter moderresultatene for å finne moderutoverene. Dersom disse har resultater for overb.klubben overfores disse tilbake.

                utovereSjekket = []
                for klubbRes in reversed(klubbResultater):
                    
                    utover = klubbRes.hentUtover()

                    if utover not in utovereSjekket:
                        utovereSjekket.append(utover)
                    else:
                        continue

                    utoverResultater = utover.hentResultater()

                    for utoverRes in utoverResultater:

                        if utoverRes.hentKlubbFra() is not overbygKlubb:
                            continue

                        alder = utoverRes.hentAlderTilUtover()
                        
                        con1 = (alder_krav[0] and alder in [11,12,13,14])
                        con2 = (alder_krav[1] and alder in [15,16,17,18,19])
                        con3 = (alder_krav[2] and alder>=20)
                        
                        if any((con1,con2,con3)):
                            moderklubb.leggTilRes(utoverRes)
                            overbygKlubb.fjernRes(utoverRes)

                            utoverRes.settKlubbTil(moderklubb)
                            utoverRes.settBegrunnelse("Klubb unntatt overbygning")
