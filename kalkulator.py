import itertools

from utover import Utover
from resultat import Resultat

class Kalk:

    nullutover = Utover(None,None,None)
    nullresultat = Resultat(nullutover,None,0,None,None,None,None)

    @staticmethod
    def LagKalk(datasenter,klubb):

        "1. Henter klubbens resultater"

        kjonn = klubb.hentKjonn()
        klubbres = klubb.hentResultater()

        ubrukte_klubbres = klubbres.set()
            
        "2. Bestemmer lagene til klubben fra resultatene."        
        
        lag_nr = 1

        while len(ubrukte_klubbres)>0: # nytt lag dersom det er flere (ubrukte) resultater i klubben.
            
            "2.1. Beregner seriepoeng og annen tilhørende informasjon til beste lag"
            
            obl_lag,val_lag = Kalk.__rekursiv_lagberegner(datasenter,klubb,lag_nr,ubrukte_klubbres,[],[],0)[0]

            "2.2. Finner relevante statuetter, prosesserer og så lagrer laginformasjon fra beregning" 
            
            lag = klubb.hentLag(lag_nr)        
            ovelsesinfo = datasenter.ovelsesinfo()
            
            obl_sekvens = ovelsesinfo["sluttform"] # inkluderer ogsa ikke-obl ovelser, men er uten betydning

            obl_lag = [res for x in obl_sekvens for res in obl_lag if res.hentOvelse() == x]
            val_lag = Kalk.__sorter([res for res in val_lag])
            
            tabell = datasenter.tabell(kjonn)

            lag.settLagoppstilling(obl_lag,val_lag)
            tabell.plasserLag(lag)

            "2.3. Klargjør for beregning av klubbens neste lag."
            
            brukte_utovere = Kalk.__set_obj([res.hentUtover() for res in obl_lag+val_lag])
            
            ubrukte_klubbres = [res for res in ubrukte_klubbres if res.hentUtover() not in brukte_utovere] # fjerner "brukte" utøvere fra gjenværende klubbresultater.

            lag_nr += 1

    @staticmethod
    def __rekursiv_lagberegner(datasenter,klubb,lag_nr,resultater,lag_info,n_liste,steg):

        "2.1.1. Beregner (evt. flere) lag med høyeste mulige seriepoengsum"

        n,lag,utovere_brukt = Kalk.__beregn_lagoppstilling(datasenter,klubb,lag_nr+steg,resultater)

        "2.1.2. Bruker rekursjon til å finne beste av flere lag med samme poeng, basert på de neste lagene til klubben"

        if steg == 0:
            lag_info = lag[0]
                
        if len(utovere_brukt)==1: ## hvis kun en optimal lagoppstilling, returnerer direkte laginfoen
            return [lag_info,n_liste+[n]]

        else:   

            like_lag = [] # liste med lag_info av to eller flere lag med likt antall seriepeong
            
            resultater_i = resultater[:] # gjenværende resultater til klubben. Lagres ettersom den senere endres ved iterasjon.
                
            for i in range(len(utovere_brukt)):###### finner poeng til neste lag (2. lag hvis dette er 1. lag) til de ulike lagoppstillingene
                
                if steg == 0: ## lager laginfo lister til hver "optimale" lagoppstilling
                    lag_info = lag[i]
                    
                resultater = [res for res in resultater_i[:] if not res.hentUtover() in utovere_brukt[i]]
                
                like_lag.append(Kalk.__rekursiv_lagberegner(datasenter,klubb,lag_nr,resultater,lag_info,n_liste+[n],steg+1))
            
            i = 0
            while True:
                len_n_liste = [len(el[1]) for el in like_lag] # rekursiv iterasjonsdybde (2 - neste lag, 3 - de to neste lagene, osv)

                if i>=max(len_n_liste) or len(like_lag)==1: ## i>=høyeste iterasjonsdybde vil si at lagene er like gode og kombinasjon kan velges vilkårlig.
                    break    
                
                liste_poeng_lister = [el[1] for el in like_lag] # liste med alle aktuelle lister av poenger til klubbens ulike lag
                P_gj_lag = []
                for poeng_liste in liste_poeng_lister: # l = liste med poenger til 1. lag, 2. lag osv
                    if len(poeng_liste)>i: # len(l) = iterasjonsdybde
                        P_gj_lag.append(poeng_liste[i]) # henter gjeldende poeng til det siste laget (poengene til alle de øvrige lagene vil være like)

                beste_lag = [] ##### sammenlikner poengene og henter ut kun det beste
                for laginfo in like_lag:
                    if len(laginfo[1])>i:
                        if laginfo[1][i]==max(P_gj_lag): # hvis lagoppstillingen har likt antall poeng som høyeste mulig
                            beste_lag.append(laginfo)
                
                like_lag = beste_lag
                
                i += 1
                
            # Returnerer laginfo med den beste oppstillingen. Ettersom det er en rekursiv funksjon vil den beregne seg først nedover alle lag helt til den finner en entydig beste lagoppstilling. Ut ifra denne kan den velge beste lagoppstilling av flere som gir samme poeng.
            # Eksempelvis betyr dette at for en klubb som har to oppstillinger med samme beste poengsum, samt samme beste 2. lag, 3. lag, men ulikt 4. lag, vil algoritmen regne ulike ruter ned og sammenlikne 4. lagene slik at den finne den mest ideelle lagoppstillingen.
            
            return like_lag[0]  
            
    @staticmethod
    def __beregn_lagoppstilling(datasenter,klubb,lag_nr,resultater):
        
        "2.1.1.1. Henter relevant informasjon og krav"

        settinger = datasenter.settinger()
        ovelsesinfo = datasenter.ovelsesinfo()["sluttform"]

        div = klubb.hentDiv(lag_nr)
        kjonn = klubb.hentKjonn()

        antallOvelser = settinger["antall øvelser"][f""+str(div)+". div"]
            
        krav_obl = antallOvelser["obl"]
        krav_obl_tek = antallOvelser["obl-tek"]
                
        krav_val = antallOvelser["val"]
        krav_val_tek = antallOvelser["val-tek"]
        
        obl = [ovelse for ovelse in ovelsesinfo if "obl" in ovelsesinfo[ovelse][kjonn]]
        tek = [ovelse for ovelse in ovelsesinfo if "tek" in ovelsesinfo[ovelse][kjonn]]
        lop = [ovelse for ovelse in ovelsesinfo if "løp" in ovelsesinfo[ovelse][kjonn]]
        
        N_maks = settinger["maks resultater per person"]

        "2.1.1.2. Finner og skiller resultatene inn i obl-, tek- og løpsresultater."

        ai = Kalk.__sorter([res for res in resultater if res.er(obl)])
        bi = Kalk.__sorter([res for res in resultater if res.er(tek)])
        ci = Kalk.__sorter([res for res in resultater if res.er(lop)])

        ovelser = []
        a = []
        for res in ai:
            if res.hentOvelse() not in ovelser:
                ovelser.append(res.hentOvelse())
                a.append(res)

        a_temp = a[:]
      
        if len(a)==0: ###### Fyller opp listene med 0-resultater
            a = [Kalk.nullresultat]
        while len(Kalk.__sorter(bi))<30:
            bi.append(Kalk.nullresultat)
        while len(Kalk.__sorter(ci))<30:
            ci.append(Kalk.nullresultat)

        "1.3.2.3. Lager liste med de (i utgangspunktet) beste obligatoriske resultatene."
        
        N_tek = Kalk.__tell_tek(a[:krav_obl],lop) # antall tek. øvelser
        
        if krav_obl_tek <= N_tek:
            a = a[:krav_obl]
        
        else:
            a_tek = Kalk.__sorter([res for res in a if (res.er(tek) or res.erNull())])[:krav_obl_tek]
            a_lop = Kalk.__sorter([res for res in a if res.er(lop)])[:(krav_obl-krav_obl_tek)]
            
            a = Kalk.__sorter(a_tek + a_lop)

        a_i = a[:]

        "1.3.2.13. Finner resultater som (praktisk sett) ikke vil kunne befinne seg i valgfri oppstilling"
        
        tek_ikkeval = [res for res in a if res.er(tek)][:krav_obl_tek] # tekres som aldri vil kunne befinne seg i val oppstilling
        lop_ikkeval = [res for res in a if res.er(lop)] # lopsres som aldri vil kunne befinne seg i val oppstilling

        ikkeval = tek_ikkeval+lop_ikkeval

        "1.3.2.4. Lager backup-lister der (eventuelle) nye obligatoriske resultater hentes fra."

        a_ers_ny = [res for res in a_temp if (not res in a)] ## fjerner overlappende resultater

        a_ers = [res for res in ai[:] if (not res in a+a_ers_ny)]

        "1.3.2.6. Legger til obl øvelser som erstatter eventuelle tekniske obl øvelser som kan falle ned i valgfri oppstilling."

        N_a_tek = Kalk.__tell_tek(a,lop)

        l = 0
        t = 0
        while True:
            flere = False
            for i,res in enumerate(a_ers_ny):

                if res.er(lop):
                    a.append(res)
                    del a_ers_ny[i]

                    l += 1
                    flere = True
                    break

            if l==N_a_tek-krav_obl_tek or not flere:
                break        

        "1.3.2.5. Lager (ikke-overlappende med obl) lister for løps- og tekniske øvelser."

        b = [res for res in bi if (not res in a or res.erNull())]
        c = [res for res in ci if (not res in a or res.erNull())]
                        
        b_c = Kalk.__sorter(b + c)

        "1.3.2.7. Henter inn nye obligatoriske resultater for hver gang 'maks 5'-kravet 'brytes'."
            
        N_tek = Kalk.__tell_tek(b_c[:krav_val],lop) # antall tek. øvelser  
                
        if N_tek >= krav_val_tek:
            d = a+b_c[:krav_val] # d = aktuelle resultater = obl + beste valgfri øvelser inklusive ekstra resultater tilsvarende antall ganger "maks 5"-kravet brytes.
        else:
            d = a+b[:krav_val_tek]+c[:krav_val-krav_val_tek]
            
        utovere_5 = [] # utøver med over 5 resultater totalt, med tilhørende antall
        ov = [] # øvelser til en utøver med over 5 resultater som har fått en erstatter
        ov_krav = [] # øvelser til en utøver med over 5 resultater som det må skaffes en erstatter for
        
        N_ny = 0
        
        obl_null = [] # ovelsene med obl.-resultater som potensielt kan erstattes med et 0-resultat og gi bedre total-poengsum.
        
        while True: # uendelig løkke fordi erstatter resultatene kan igjen bryte "maks 5"-kravet som igjen krever at det hentes resultater. Exiter løkken ved første iterasjon der kravet ikke brytes.
            
            N_ek = 0 # antall ganger "maks 5"-kravet brytes
            
            utovere = [res.hentUtover() for res in d]

            for utover in Kalk.__set_obj(utovere):
                
                N_res = utovere.count(utover) # N_res = antall res av utøver blant (foreløpig) gjeldende obl. og val.
                
                condition1 = N_res>N_maks
                condition2 = not utover.erNull()
                condition3 = not utover in utovere_5 # utøvere allerede hentet res
                
                if condition1 and condition2:
                    
                    N_ek += N_res-N_maks
                
                    if condition3:

                        utovere_5.append(utover)
                        ov_krav.append([res.hentOvelse() for res in a if res.hentUtover() is utover]) # øvelser det skal hentes erstatter for
                        ov.append([])
        
            for i in range(len(ov_krav)): # i = utøver nr.
                for l in range(len(ov_krav[i])): # ov_krav[i][l] = øvelse
                    
                    if ov_krav[i][l] in ov[i]: ## hvis erstatter resultatene allerede er hentet
                        continue
                    
                    ov[i].append(ov_krav[i][l])
                
                    pos = None
                    for j in range(len(a_ers)):
                        if a_ers[j].hentOvelse()==ov_krav[i][l]:
                            pos = j
                            break
                    
                    if pos != None:
                        a.append(a_ers[pos])
                        del a_ers[pos]
                    else:
                        obl_null.append(ov_krav[i][l])
                            
            while N_ny < N_ek: ###### henter erstatter resultat fra øvelser i utgangspunktet ikke var gode nok for obl.
                if len(a_ers_ny)==0:
                    break
                
                N_ny += 1
                
                a.append(a_ers_ny[0])
                del a_ers_ny[0]
                    
        
            ######## oppdaterer listen med gjeldende valgfri resultater gitt de nye obligatoriske øvelsene samt ny N_ek verdi.
            
            b = [res for res in b if (not res in a or res.erNull())]      
            c = [res for res in c if (not res in a or res.erNull())]
                    
            b_c = Kalk.__sorter(b + c)

            N_tek = Kalk.__tell_tek(b_c[:krav_val+N_ek],lop)
                    
            if N_tek>=krav_val_tek+N_ek:
                d = a+b_c[:krav_val+N_ek]
            else:
                d = a+b[:krav_val_tek+N_ek]+c[:krav_val-krav_val_tek+N_ek]       
                    
            cond1 = True 
            cond2 = True
                
            for i in range(len(utovere_5)): ###### sjekker om noen av utøverne med over 5 øvelser, har fått nye øvelser som må erstattes (skjer hvis erstattingsresulter er av en utøver med mer enn 5 øvelser)
                
                utover_obl = [res.hentOvelse() for res in a if res.hentUtover() == utovere_5[i]] # obligatoriske resultater til utøveren
                
                if len(utover_obl)>len(ov_krav[i]):
                    ov_krav[i] = utover_obl
                    
                    cond1 = False
                    break
                
            utovere = [res.hentUtover() for res in d]
                
            i = 0 ######## sjekker om noen nye utøvere har over 5 øvelser
            for utover in Kalk.__set_obj(utovere):
                
                condition1 = utovere.count(utover)>N_maks
                condition2 = not utover.erNull()
                condition3 = not utover in utovere_5
                
                if condition1 and condition2 and condition3:
                    
                    cond2 = False
                    break
                    
            if cond1 and cond2:
                break
            
        "1.3.2.8. Legger til like gode resultater i obl. listen for håndtering av 'beste 2. laget'"

        a_ers = [res for res in a_ers if not (res in a+a_ers_ny)]
        
        a_poeng = [res.hentPoeng() for res in a]
        a_ovelser = [res.hentOvelse() for res in a]

        for res in a_ers_ny+a_ers:
            
            con1 = (res.hentPoeng() in a_poeng) and (res.hentOvelse() not in a_ovelser) # res er et like god resultat men i en øvelse som ikke er brukt
            con2 = any(   ###### res er like god som et annet resultat i a (lik øvelse og poeng)
                        (all((
                            (res.hentPoeng()==res2.hentPoeng()),
                            (res.hentOvelse()==res2.hentOvelse())
                        )) for res2 in a)
                    )

            if any((con1,con2)):
                a.append(res)
        
        a = Kalk.__sorter(a)

        "1.3.2.11. Fordeler ikke-sikre obligatoriske resultater etter øvelse, og legger til eventuelle null-resultater"
        
        b = [res for res in b if (not res in a or res.erNull())]  
        c = [res for res in c if (not res in a or res.erNull())]

        b_c = Kalk.__sorter(b + c)
                
        N_tek = Kalk.__tell_tek(b_c[:krav_val+N_ek],lop) 
                
        if N_tek>=krav_val_tek+N_ek:
            d = a + b_c[:krav_val+N_ek]
        else:
            d = a + b[:krav_val_tek+N_ek]+c[:krav_val-krav_val_tek+N_ek]

        a_fordelt = {True: {}, False: {}}  ######## a fordelt etter øvelse

        for res in a:
            ovelse = res.hentOvelse()
            try:
                a_fordelt[res.er(tek)][ovelse].append(res)
            except KeyError: # ovelsen finnes ikke enda
                a_fordelt[res.er(tek)][ovelse] = [res]

        for ovelse in obl_null: ## legger til null-resultat for de gitte øvelsene
            a_fordelt[ovelse in tek][ovelse].append(Kalk.nullresultat)

        N = {"tek": {}, "lop": {}}

        N["tek"]["tot"] = len(a_fordelt[True])
        N["lop"]["tot"] = len(a_fordelt[False])

        "1.3.2.10. Samlet (og fjerner fra obl listen) sikre resultater - resultater som er garantert å være i obl oppstillingen"
        
        a_sikker = []

        ovelser_sjekket = [] # ovelser i a der beste resultat allerede har vært sett på 
        l = 0
        t = 0
        for res in a: # lops obl resultater
            ovelse = res.hentOvelse()

            if ovelse in ovelser_sjekket:
                continue
            ovelser_sjekket.append(ovelse)

            if (omTek := res.er(tek)):
                condition1 = (t<krav_obl_tek or t<krav_obl-N["lop"]["tot"]) # om tek resultatet erstatter en ellers garantert tom obl plass
                condition2 = (N_tek>=krav_val_tek+N_ek and t+l<krav_obl) # om valgfri oppstilling ikke har mangel på tekniske øvelser, og det er plass til resultatet i obl oppstillingen

                con1 = (condition1 or condition2)
                con2 = (len(a_fordelt[True][ovelse])==1)

                t += 1

            else:
                con1 = (l<krav_obl-krav_obl_tek and t+l<krav_obl) # det er plass til resultatet blant løpsresultatene i obl oppstillingen
                con2 = (len(a_fordelt[False][ovelse])==1)

                l += 1

            if all((con1,con2)):
                a_sikker.append(a_fordelt[omTek][ovelse][0])
                del a_fordelt[omTek][ovelse]

        a_sikker = Kalk.__sorter(a_sikker)

        "1.3.2.10. Finner minimums antall resultater >5 utoverene vil ha i obligatorisk oppstilling"

        utovere_iv = [res.hentUtover() for res in ikkeval] 
        utovere_d = [res.hentUtover() for res in d] #  alle utøvere med res blant aktuelle resultater

        N_null = 0
        utoverres = {}
        for utover in utovere_5:

            N_potensiale = 0
            for omTek in [True,False]:
                for ovelse,ovelsesres in a_fordelt[omTek].items():
                    if ovelse not in obl_null: # aktuell ovelse kan ikke representeres som et nullresultat
                        continue
                        
                    utoverensRes = (ovelsesres[-2].hentUtover()==utover) # utoveren har nest siste res til ovelsen. Da vil det potensielle nullresultatet kunne erstatte utoverens res når det faller fra 
                    
                    if utoverensRes:
                        N_potensiale += 1

            N_utover_iv = utovere_iv.count(utover)
            N_utover_d = utovere_d.count(utover)

            N_null += max(min((N_utover_d-N_maks, N_potensiale)),0)

            N_res_min = min((N_maks+N_utover_iv-N_utover_d,N_utover_iv))

            if N_res_min<=0:
                continue

            utoverres[utover] = N_res_min            

        "1.3.2.12. Finner alle aktuelle kombinasjoner av obligatoriske oppstillinger"

        for sort in ["tek","lop"]:
            N[sort]["usikker"] = len(a_fordelt[sort=="tek"])
            N[sort]["sikker"] = N[sort]["tot"] - N[sort]["usikker"]

        ingenOblRes = any((
            (N["tek"]["usikker"]+N["lop"]["usikker"]==0),                            # 1. det finnes ingen usikre obligatoriske resultater
            (N["tek"]["sikker"]+N["lop"]["sikker"]==krav_obl),                       # 2. obligatorisk oppstilling allerede oppfylt
            (N["tek"]["usikker"]==0 and N["lop"]["sikker"]==krav_obl-krav_obl_tek),  # 3. det er ikke plass til noen av de siste "usikre" lopsovelse
        ))
        kunEttOvelsesutvalg = (N["lop"]["tot"]<=krav_obl-krav_obl_tek and N["tek"]["tot"]+N["lop"]["tot"]<=krav_obl)


        """print(f"\n\n ==== Lag {lag_nr} ==== ")
        
        print(" --- a_sikker --- ")
        for el in a_sikker:
            print(el)

        print("krav_obl", krav_obl)
        print("len(a_sikker)",len(a_sikker))
        print(N["tek"]["usikker"],N["lop"]["usikker"])

        for ovelse in a_fordelt[True]:
            print("\n"+ovelse, end=":  ")
            for res in a_fordelt[True][ovelse]:
                print(res,end="| ")

        for ovelse in a_fordelt[False]:
            print("\n"+ovelse, end=":  ")
            for res in a_fordelt[False][ovelse]:
                print(res,end="| ")

        for utover,verdi in utoverres.items():
            print(utover,verdi)"""

        if ingenOblRes:
            liste = [(Kalk.nullresultat,)]

        elif kunEttOvelsesutvalg:
            utvalg = list(a_fordelt[True].values()) + list(a_fordelt[False].values())

            liste = Kalk.__hent_oppstillinger(utvalg,utoverres,N_null)


        else:
            N_tek_start = max((krav_obl_tek - N["tek"]["sikker"],0))
            N_tek_slutt = min((N["tek"]["usikker"],krav_obl-N["tek"]["sikker"]-N["lop"]["sikker"]))
           
            liste = []
            for N_tek in range(N_tek_start,N_tek_slutt+1):
                nr = 0
                
                tekutvalg = []
                for utvalg in itertools.combinations(a_fordelt[True].values(),N_tek): # finner mulige (tekniske) ovelsesutvalg
                    tekutvalg.append(utvalg)
                    
                lopsutvalg = []
                for utvalg in itertools.combinations(a_fordelt[False].values(),krav_obl-N_tek-N["lop"]["sikker"]-N["tek"]["sikker"]): # finner mulige (lops-)ovelsesutvalg
                    lopsutvalg.append(utvalg)

                for tek_komb,lop_komb in itertools.product(tekutvalg,lopsutvalg):
                    nr += 1

                    kombinert_utvalg = tek_komb + lop_komb

                    obl_oppstillinger = Kalk.__hent_oppstillinger(kombinert_utvalg,utoverres,N_null)
                    liste.extend(obl_oppstillinger)

        liste = sorted(liste, key = lambda x: -Kalk.__poengsum(x))

        "1.3.2.13. Finner høyeste (praktisk) mulig poengsum for valgfri oppstilling"

        b_val = [res for res in bi if (res not in ikkeval) or res.erNull()] ######### regner ut den høyeste mulig b og c summen for å exite beregning når de obligatoriske øvelsene gir en for lav sum til å kunne forbedre seriepoengene.
        c_val = [res for res in ci if (res not in ikkeval) or res.erNull()]
        
        b_c = Kalk.__sorter(b_val+c_val)
        
        N_tek = Kalk.__tell_tek(b_c[:krav_val],lop)

        if N_tek>=krav_val_tek+N_ek:
            maks_val = Kalk.__poengsum(b_c[:krav_val]) # høyeste mulig poengsum til en valgfri oppstilling
        else:
            maks_val = Kalk.__poengsum(b_val[:krav_val_tek]+c_val[:(krav_val - krav_val_tek)])

        "1.3.2.14. Til hver lagkombinasjon, beregner poengsum, og eventuelt lagrer laginfo"
        
        "1.3.2.14.1. Itererer gjennom kombinasjoner av obligatoriske oppstillinger"

        counter = 0
        n = -1
        for obl_usikker in liste:
            counter += 1

            utovere = [res.hentUtover() for res in obl_usikker] # trenger kun å sjekke for utoverne i obl_usikker, for alle >5 utovere samles her

            utoverOver5res = any(((utovere.count(utover)>N_maks) for utover in utovere_5))

            if utoverOver5res:
                continue

            obl_komb = a_sikker + list(obl_usikker)

            if Kalk.__poengsum(obl_komb)+maks_val<n: ## dersom obl. kombinasjonen (og alle etter den ettersom de er sortert etter poeng) har for lite poeng (selv med sterkeste mulige valgfri oppstilling) til a kunne erstatte beste n-verdi
                break

            " Henter aktuelle valgfrie ovelser"

            obl_res_tek = [res for res in obl_komb if res.er(tek)]
            obl_res_lop = [res for res in obl_komb if res.er(lop)]

            svakeste_obl_res = [10000,10000]

            if len(obl_res_tek)>0:
                svakeste_obl_res[0] = min(obl_res_tek, key=lambda komb: komb.hentPoeng()).hentPoeng()
            if len(obl_res_lop)>0:
                svakeste_obl_res[1] = min(obl_res_lop, key=lambda komb: komb.hentPoeng()).hentPoeng()

            b = []
            c = []
            for lis,lis_i,svakt_res in zip([b,c],[bi,ci],svakeste_obl_res):
                for res in lis_i:

                    finnes = False
                    for obl_res in obl_komb:
                    
                        if res.hentOvelse()==obl_res.hentOvelse():
                            finnes = True

                            if (res is obl_res) and (not res.erNull()):
                                break

                            if not res>obl_res:
                                lis.append(res)
                            break

                    if not finnes:
                    
                        con1 = (res.er(obl))
                        con2 = (res.hentPoeng()<=svakt_res)

                        if all((con1,con2)):
                            lis.append(res)
                        if not con1:
                            lis.append(res)
        
            b_c = Kalk.__sorter(b+c)
            
            "1.3.2.14.2. Finner antall gjenværende øvelser til utøvere med over 5 resultater totalt"
                    
            utovere = [res.hentUtover() for res in d]
            utovere_obl = [res.hentUtover() for res in obl_komb]
            
            begrensing = {}
            for utover in Kalk.__set_obj(utovere):
                if (utovere+utovere_obl).count(utover) > N_maks and not utover.erNull(): # hvis utøveren har flere totalt har flere enn 5 resultater
                    N_obl_ut = utovere_obl.count(utover)
                    begrensing[utover] = [N_maks-N_obl_ut,N_maks-N_obl_ut,N_maks-N_obl_ut,N_maks-N_obl_ut] # gj. øvelser til utøveren
                    
                
            "1.3.2.14.3. Finner en valgfri oppstilling like god eller bedre enn beste gyldig oppstilling"
            
            
            N_tek = Kalk.__tell_tek(b_c[:krav_val+N_ek],lop) 
                    
            if N_tek>=krav_val_tek+N_ek:
                d = Kalk.__sorter(b_c[:krav_val+N_ek])
            else:
                d = Kalk.__sorter(b[:krav_val_tek+N_ek]+c[:krav_val-krav_val_tek+N_ek])

            
            """
            delen under maa skrives om. Antakelig kan bare .index brukes uten problemer
            
            
            
            
            
            
            ------------------------------------------
            """

            

            t_valgfri = [] # teoretisk valgfri oppstilling. Vil være lik eller bedre enn faktisk beste oppstilling
            if len(begrensing)>0:                
                begr_utovere = list(begrensing.keys())
                
                for i in range(len(d)):
                    oop = 1
                    if d[i].hentUtover() in begr_utovere: # hvis utøveren har begrensing i antall gj. øvelser (fordi >5 totalt)
                        
                        begr = begrensing[d[i].hentUtover()]

                        if d[i].er(lop):                        
                            if begr[2]<=0:
                                oop = 0
                            else:
                                begr[2] -= 1
                        else:
                            if begr[3]<=0:
                                oop = 0
                            else:
                                begr[3] -= 1         
                    if oop == 1:
                        t_valgfri.append(d[i])
            else:
                t_valgfri = d
                
            "1.3.2.14.4. Skipper til neste obligatoriske oppstillingen dersom den teoretiske valgfri oppstillingen er for svak"
                        
            if len(t_valgfri)>krav_val:
                t_valgfri = t_valgfri[:krav_val]
                    
            if Kalk.__poengsum(t_valgfri+obl_komb)<n:
                continue

            "1.3.2.14.5. Fjerner for dårlige valgfri løps- og tekniske resultater av utøvere med over 5 resultater totalt"

            if len(begrensing)>0: ####... Henter kun de 5-x beste valgfri øvelsene, der x er antall obl. øvelser av utøveren
                res = []
                for i in range(len(b_c)):
                    begr = None ##### finner iterasjons nr. i begrensing til utøveren

                    for utover in begrensing: ##### darlig skrevet (i lik grad som resten av denne kodeblokka)
                        if utover==b_c[i].hentUtover():
                            begr = begrensing[utover]
                            break
                    
                    if begr != None:
                        if b_c[i].er(lop): ### hvis gj. lopsovelser er 0 -> henter ikke flere valgfri løpsøvelser fra utøveren
                            if begr[1]<=0:
                                continue
                            else: ### ellers -> henter res og setter en mindre plass igjen
                                begr[1] -= 1
                        else:
                            if begr[0]<=0: ### hvis gj. tek ovelser er 0 -> henter ikke flere valgfri tekniske øvelser fra utøveren
                                continue
                            else: ### ellers -> henter res og en mindre plass igjen
                                begr[0] -= 1
                                    
                    res.append(b_c[i])
                                
                b_c = res[:]
                    
            while len(b_c)<krav_val+N_ek: ## fyller eventuelle rest plasser med null resultater
                b_c.append(Kalk.nullresultat)   
                                
            b = [res for res in b_c if (not res.erNull()) and (not res.er(lop))] ### henter de beste tekniske øvelsene
            
            while len(b)<krav_val_tek+N_ek:
                b.append(Kalk.nullresultat)
            
            
            "1.3.2.14.6. Finner start- og sluttverdi av antall tekniske øvelser blant de valgfrie"    
            
            N_maks_tek = min((krav_val,len(b))) # finner start- og sluttverdi for antall tekniske valgfri øvelser som det skal sjekkes for
                
            "1.3.2.14.7. Henter eventuelle resultater like gode som den/de svakeste blant valgfri tekniske"    
            
            b_pot = Kalk.__sorter([res for res in bi if not any((res in b, res.erNull(), res.hentUtover() in utovere_obl))]) ############# Legger til tekniske valgfri øvelser som har lik poeng som den dårligste i valgfri tek. listen
            
            P_svak_res = int(b[-1].hentPoeng()) # resultatet av tekniske valgfri med minst poeng av de gjeldende
            i = 0
            
            while len(b_pot)>i:
                
                if int(b_pot[i].hentPoeng()) != P_svak_res or P_svak_res == 0: ## om neste tek. res har ulik (mindre) poeng exites løkken (listen er sortert så derfor betyr dette at ingen har lik poeng som dårligste i tek. listen)
                    break
                                    
                condition1 = (not b_pot[i] in b)
                
                try:
                    begr = begrensing[b_pot[i].hentUtover()]

                    cond1 = (b_pot[i].er(tek) and begr[1]>0)
                    cond2 = (b_pot[i].er(lop) and begr[2]>0)
                    
                    condition2 = (cond1 or cond2)
                except KeyError:
                    condition2 = True
                    
                if condition1 and condition2:
                    b.append(b_pot[i])
                i += 1
    
            "1.3.2.14.8. Finner kombinasjoner med antall gjenværende tekniske resultater til utøvere med over 5 resultater totalt"    

            utovere = [res.hentUtover() for res in b_c]

            begr = [] ##### finner de gj. tekniske øvelsene til >5 res utøvere
            for utover in Kalk.__set_obj(utovere):
                if (utovere+utovere_obl).count(utover) > N_maks and not utover.erNull(): ## sjekker om utøveren har begrensing på valgfri øvelser (pga >5 totalt)
                    N_obl_ut = utovere_obl.count(utover)
                    begr.append([utover,N_maks-N_obl_ut])
            
            
            b_5 = [] # samleliste med de tek. res til de ulike utøverne.
            liste_N_tek = [] # samleliste med antall tek res som kan brukes av de ulike utøverne
                            
            for i in range(len(begr)):
                    
                ov = [] # valgfri tek av >5 res utøver
                N_ov = [] # antall tek øvelser utøveren kan ha
                    
                for l in range(len(b)):
                    if b[l].hentUtover()==begr[i][0]:
                        ov.append(b[l])
                            
                N_ov.append(0)
                for j in range(begr[i][1]):
                    if len(ov) >= j+1:
                        N_ov.append(j+1)
                                    
                b_5.append(ov)
                liste_N_tek.append(N_ov)
                
            b_5_unostet = [res for utover_res in b_5 for res in utover_res]
                    
            b_i = b[:] ## lagrer en initiell b og c(som senere endres) slik at den kan 'nullstilles' for hver nye iterering
            c_i = c[:]

            liste_tek_i = [el for el in itertools.product(*liste_N_tek)] # finner kombinasjoner av antall tekniske resultater til 5> res utovere

            "1.3.2.14.9. Beregner samlet poengsum, og lagrer laginfo, til beste valgfri og den gitte obligatoriske oppstillingen"    

            "1.3.2.14.9.1. Itererer gjennom et intervall av antall mulige teknisk valgfrie øvelser"

            for N_tek in range(krav_val_tek,N_maks_tek+1): # tek = antall tekniske valgfri resultater

                b = [res for res in b_i if res not in b_5_unostet] # fjerner overlappende resultater med b_5 (5> utøvernes res håndteres sepearat fra de andre resultatene)
                
                kombs_tek = [el for el in liste_tek_i if (not sum(el)+len(b)<N_tek)]

                b_i2 = b[:]
                    
                "1.3.2.14.9.2. Itererer gjennom kombinasjoner av valgfri tekniske øvelser av utøvere med over 5 resultater totalt"
                
                for liste_N_tek_5 in kombs_tek: # liste_N_tek_5 = liste med antall øvelser som skal benyttes av >5 res utøvere

                    b = b_i2[:]
                            
                    res_5 = [] ### henter de x beste gjenværende tekniske øvelser til >5 res utøvere
                    for i in range(len(liste_N_tek_5)):
                        res_5 += b_5[i][:liste_N_tek_5[i]]

                    ###### samler og sorterer de tek antall beste tekniske øvelsene
                    if len(b)>0 and len(b)>=N_tek-len(res_5):
                        tek_res = Kalk.__sorter(res_5 + b[:N_tek-len(res_5)])
                                
                    elif len(b)==0:
                        tek_res = Kalk.__sorter(res_5)
                                    
                    else:
                        tek_res = Kalk.__sorter(res_5 + b)
                        
                    
                    "1.3.2.14.9.3. Henter eventuelle resultater like gode som det svakeste av de tekniske valgfri"
                    
                    b = [res for res in b if res not in tek_res] # finner b-resultater som ikke overlapper med tek_sikker
                    
                    P_svak_res = tek_res[-1].hentPoeng() # finner poeng til det svakeste resultatet
                    
                    like_res = [] ####### finner resultatene med dårligst poeng i tek_sikker.
                    
                    i = len(tek_res)-1
                    
                    while i>=0:
                        
                        if tek_res[i].hentPoeng()==P_svak_res and P_svak_res != 0:
                            like_res.append(tek_res[i]) # like res
                            i -= 1
                        else:
                            break
                    
                    N_gj_res = len(like_res)
                    
                    tek_sikker = [res for res in tek_res if res not in like_res] # fjerner dårligste tek. res
                    
                    i = 0 ####### Henter inn eventuelle resultater med likt antall poeng som de den/de svakeste i val. tek. Enhver av disse kan erstatte den eller de dårligste.
                    while len(b)>i:
                        if b[i].hentPoeng()==P_svak_res and P_svak_res != 0:
                            like_res.append(b[i])
                            i += 1
                        else:
                            break
                        
                        
                    "1.3.2.14.9.4. Itererer gjennom kombinasjoner av den/de svakeste resultatene blant tekniske valgfri"
                    
                    for tek_usikker in itertools.combinations(like_res,N_gj_res): # itererer gjennom kombinasjoner svakeste res. i de valgfri tekniske øvelsene. Dette er viktig for å finne beste lagoppstilling mhp. beste 2. lag.
                    
                        tek_komb = tek_sikker + list(tek_usikker) # samler de valgfri tekniske øvelsene
                        
                        if len(tek_komb)>krav_val:
                            tek_komb = tek_komb[:krav_val]
                            
                        "1.3.2.14.9.5. Fyller gjenværende valgfrie plasser med løpsøvelser og beregner poengsum"
        
                        if krav_val - len(tek_komb)>0: # sjekker om det er gjenværende plass til løpsøvelser. Hvis ikke, har vi en allerede en komplett oppstilling.
                            
                            c = c_i[:]

                            utovere = [res.hentUtover() for res in tek_komb+obl_komb]
                                        
                            maks = [] #### utøvere som allerede har brukt sine 5 øvelser
                            for utover in Kalk.__set_obj(utovere):
                                if utovere.count(utover)==N_maks and not utover.erNull():
                                    maks.append(utover)
                                    
                            lop_si = []

                            i = 0 ####### Henter gjenværende løpsøvelser
                            while len(lop_si)<krav_val-len(tek_komb) and len(c)>i: # mens det fortsatt er gjenværende plasser
                                            
                                if not c[i].hentUtover() in maks: # henter ikke fra utøvere med null gjenværende øvelser
                                    lop_si.append(c[i])
                                    
                                    utovere.append(c[i].hentUtover())
                                                
                                    if utovere.count(c[i].hentUtover())==N_maks and not c[i].erNull(): ## oppdaterer listen med utøvere med null gjenværende øvelser
                                        maks.append(c[i].hentUtover())
                                i += 1
                                    
                            like_res = []
                            
                            P_svak_res = lop_si[-1].hentPoeng() # poeng til svakeste løpsresultat
                            
                            for res in lop_si[::-1]: ##### finner de/den svakeste av gjeldende løpsresultater
                                if res.hentPoeng() != P_svak_res:
                                    break
                                else:
                                    like_res.append(res)
                                    
                            N_gj_res = len(like_res)
                            
                            
                            while len(c)>i:  ###### finner like gode resultater med den/de svakeste fra resten av løpsresultatene
                                
                                if c[i].hentPoeng() != P_svak_res:
                                    break
                                            
                                utovere_like_res = [res.hentUtover() for res in like_res]
                                
                                if (c[i].hentUtover() not in maks) and (c[i].hentUtover() not in utovere_like_res):
                                    like_res.append(c[i])
                                i += 1
                            
                            lop_si = [res for res in lop_si if res not in like_res] # fjerner løpsresultatene lik den med svakest antall poeng
                            
                            for lop_ek in itertools.combinations(like_res,N_gj_res): # itererer gjennom kombinasjoner av løpsresultatene med svakest poeng. 

                                lop_komb = lop_si + list(lop_ek)
                                
                                set_utovere = Kalk.__set_obj([res.hentUtover() for res in obl_komb+tek_komb+lop_komb if not res.erNull()])
                                set_utovere = sorted(set_utovere, key=lambda x: x.hentNavn())

                                s = Kalk.__poengsum(obl_komb + tek_komb + lop_komb)

                                if s>n: ###... hvis høyere poengsum - oppdaterer laginfo

                                    n = s
                                    lag = [[obl_komb,tek_komb+lop_komb]]
                                    utovere_brukt = [set_utovere]

                                elif s==n and (set_utovere not in utovere_brukt): ###... hvis lik poengsum - legger til en ekstra lagoppstilling. Senere vil det vurderes hvilken av disse som gir beste 2. lag.
                    
                                    utovere_brukt.append(set_utovere)
                                    lag.append([obl_komb,tek_komb+lop_komb])
                        
                        else:

                            set_utovere = Kalk.__set_obj([res.hentUtover() for res in obl_komb+tek_komb if not res.erNull()])
                            set_utovere = sorted(set_utovere, key=lambda x: x.hentNavn())
                            
                            s = Kalk.__poengsum(obl_komb + tek_komb)

                            if s>n: ###... hvis høyere poengusm - oppdaterer laginfo
        
                                n = s
                                lag = [[obl_komb,tek_komb]]
                                utovere_brukt = [set_utovere]
                                                            
                            elif s==n and set_utovere not in utovere_brukt: ###... hvis lik poengsum - legger til en ekstra lagoppstilling. Senere vil det vurderes hvilken av disse som gir beste 2. lag.
                
                                utovere_brukt.append(set_utovere)
                                lag.append([obl_komb,tek_komb])
        return n,lag,utovere_brukt
        

    @staticmethod
    def __hent_oppstillinger(utvalg,utoverres,N_null):

        gjeldende = [[utfall] for utfall in utvalg[0]]

        i = 0
        while i<len(utvalg)-1:
            temp = []
            for komb in gjeldende:
                for utfall in utvalg[i+1]:

                    ny_komb = komb+[utfall]

                    utovere = [res.hentUtover() for res in ny_komb]

                    omUtoveravvik = any(((utovere.count(utover)+len(utvalg)-len(ny_komb)<verdi) for utover,verdi in utoverres.items()))
                    omNullavvik = utovere.count(Kalk.nullutover)>N_null

                    if any((omUtoveravvik,omNullavvik)):
                        continue

                    temp.append(ny_komb)

            gjeldende = temp
            i += 1

        return gjeldende

    @staticmethod
    def __sorter(liste):     
        return sorted(liste, key = lambda x: -int(x.hentPoeng()))
            
    @staticmethod
    def __tell_tek(liste,lop): ###### ikke lop, for at nullresultater skal telle som tek
        s = 0
        for res in liste:
            if not res.er(lop):
                s += 1
        return s

    @staticmethod
    def __poengsum(liste):
        poeng = lambda x: x.hentPoeng()

        return sum(map(poeng, liste))

    @staticmethod
    def __set_obj(liste):
        set_objects = []
        for obj in liste:
            if obj not in set_objects:
                set_objects.append(obj)
        return set_objects  
        