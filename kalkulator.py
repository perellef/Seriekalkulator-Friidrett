from itertools import combinations

from utover import Utover
from resultat import Resultat

# ny ide:
# -------
# Hvis N_sikre_tek <= N_obl_tek + N_val_tek:
# - Alle sikre tekniske ovelser -> settes som obligatoriskeN_sikre_obl_tek <= N_obl_tek
#Hvis N_sikre_tek > N_obl_tek + N_val_tek
# - Antall sikre tekniske ovelser: N_sikre_tek-N_obl_tek-N_val_tek
# 
# 
#  Antall obligatoriske sikre tekniske resultater blir:
#      N_obl_tek_sikre = N_val_tek - N_obl_tek


class Kalk:
    
    @staticmethod
    def rek_loop(liste,n,steg,kombo):
        
        full_kombo = []
        if steg+1==len(liste):
            for el in combinations(liste[steg],n[steg]): ## lager ny liste med ulike lister dannet av forrige liste satt sammen med en gruppe elementer
                full_kombo += [kombo+list(el)]
        else:
            for el in combinations(liste[steg],n[steg]): ## sla sammen alle de dannede listene
                full_kombo += Kalk.rek_loop(liste,n,steg+1,kombo+list(el))
                
        return full_kombo

    @staticmethod
    def kombinasjoner(liste):
        
        if liste==[]:
            return None
        
        n = len(liste)*[1] # antall elementer det hentes fra hver gruppe av resultater
        
        return Kalk.rek_loop(liste,n,0,[])

    @staticmethod
    def sorter(liste):     
        return sorted(liste, key = lambda x: int(x.hentPoeng()))[::-1]

    @staticmethod
    def finn(mylist,char):

        for sub_list in mylist:
            if char in sub_list:
                return mylist.index(sub_list)
            
    @staticmethod
    def tell_tek(liste,lop): ###### ikke lop, for at nullresultater skal telle som tek
        s = 0
        for el in liste:
            if not el.er(lop):
                s += 1
        return s

    @staticmethod
    def sumPoeng(liste):
        return sum([el.hentPoeng() for el in liste])

    @staticmethod
    def setObj(liste):
        set_objects = []
        for obj in liste:
            if obj not in set_objects:
                set_objects.append(obj)
        return set_objects    
            
    @staticmethod
    def rekursiv_kalkulator(datasenter,klubb,lag_nr,resultater,lag_info,n_liste,steg):
        
        "1.3.2.1. Henter relevante krav."

        settinger = datasenter.settinger()
        ovelsesinfo = datasenter.ovelsesinfo()["sluttform"]

        div = klubb.hentDiv(lag_nr+steg)
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

        "1.3.2.2. Finner og skiller resultatene inn i obl., tek. og løpsresultater."

        ai = Kalk.sorter([el for el in resultater if el.er(obl)])
        bi = Kalk.sorter([el for el in resultater if el.er(tek)])
        ci = Kalk.sorter([el for el in resultater if el.er(lop)])

        ovelser = []
        a = []
        for el in ai:
            if el.hentOvelse() not in ovelser:
                ovelser.append(el.hentOvelse())
                a.append(el)

        nullresultat = Resultat(Utover(None,None,None),None,0,None,None,None,None)
                
        if len(a)==0: ###### Fyller opp listene med 0-resultater
            a = [nullresultat]
        while len(Kalk.sorter(bi))<30:
            bi.append(nullresultat)
        while len(Kalk.sorter(ci))<30:
            ci.append(nullresultat)

        "1.3.2.3. Lager liste med de (i utgangspunktet) beste obligatoriske resultatene."
        
        if krav_obl_tek==0: # dersom det ikke er noe krav til antall obligatoriske tekniske resultater
            a = a[:krav_obl]
            
        else:
            
            N_tek = Kalk.tell_tek(a[:krav_obl],lop) # antall tek. øvelser
            
            if krav_obl_tek <= N_tek: 
                a = a[:krav_obl]
            
            else:
                a_tek = Kalk.sorter([el for el in a if (el.er(tek) or el.erNull())])[:krav_obl_tek]
                a_lop = Kalk.sorter([el for el in a if el.er(lop)])[:(krav_obl-krav_obl_tek)]
                
                a = a_tek + a_lop

            
        "1.3.2.4. Lager backup-lister der (eventuelle) nye obligatoriske resultater hentes fra."
            
        a_ers = ai[:] # a_ers er erstatter for øvelser som allerede finnes i a      
        a_ers_ny = [] # a_ers_ny henter ny øvelse (ikke i a) som erstatning
        
        obl_lag = Kalk.sorter(ai)
        
        """
        sjekk at dette nedenfor er beste maaten"
        
        
        ----------------
        
        """
        
        for ovelse in obl: # k angir (nr til) øvelse
            n = 0
            while True: # for at den skal iterere helt til alle resultater med øvelsen er tatt
                
                pos = None
                for i in range(len(obl_lag)):
                    if obl_lag[i].hentOvelse()==ovelse:
                        pos = i
                        break

                if pos != None:
                    if obl_lag[pos].hentPoeng()>=n:
                        a_ers_ny.append(obl_lag[pos])
                        n = obl_lag[pos].hentPoeng()
                        del obl_lag[pos]
                                
                    else:
                        break
                else:
                    break
                        
        a_i = a[:]
                
        a_ers_ny = Kalk.sorter([el for el in a_ers_ny if (not el in a)]) ## fjerner overlappende resultater

        a_ers = Kalk.sorter([el for el in a_ers if ((not el in a) and (not el in a_ers_ny))])

        "1.3.2.5. Lager (ikke-overlappende med obl) lister for løps- og tekniske øvelser."

        b = Kalk.sorter([el for el in bi if (not el in a or el.erNull())])
                            
        c = Kalk.sorter([el for el in ci if (not el in a or el.erNull())])
                        
        b_c = Kalk.sorter(b + c)
            
        "1.3.2.6. Henter inn nye obligatoriske resultater for hver gang 'maks 5'-kravet 'brytes'."

            
        N_tek = Kalk.tell_tek(b_c[:krav_val],lop) # antall tek. øvelser  
                
        if N_tek >= krav_val_tek:
            d = a+b_c[:krav_val] # d = aktuelle resultater = obl + beste valgfri øvelser inklusive ekstra resultater tilsvarende antall ganger "maks 5"-kravet brytes.
        else:
            d = a+b[:krav_val_tek]+c[:krav_val-krav_val_tek]
            
            
        utovere_5 = [] # utøver med over 5 resultater totalt, med tilhørende antall
        ov = [] # øvelser til en utøver med over 5 resultater som har fått en erstatter
        ov_krav = [] # øvelser til en utøver med over 5 resultater som det må skaffes en erstatter for
        
        N_ny = 0
        
        obl_null = [] # ovelsene med obl.-resultater som potensielt kan erstattes med et 0-resultat og gi bedre total-poengsum.
        
        N_tomme_brukt = 0 # antall obl lopsøvelser hentet inn for eventuelt å eventuelt erstatte en teknisk obl øvelse, som dermed kan brukes i valgfri istedenfor.
        
        while True: # uendelig løkke fordi erstatter resultatene kan igjen bryte "maks 5"-kravet som igjen krever at det hentes resultater. Exiter løkken ved første iterasjon der kravet ikke brytes.
            
            N_ek = 0 # antall ganger "maks 5"-kravet brytes
            
            utovere = [el.hentUtover() for el in d]
            
            for utover in Kalk.setObj(utovere):
                
                N_res = utovere.count(utover) # N_res = antall res av utøver blant (foreløpig) gjeldende obl. og val.
                
                condition1 = N_res>N_maks
                condition2 = not utover.erNull()
                condition3 = not utover in utovere_5 # utøvere allerede hentet res
                
                if condition1 and condition2:
                    
                    N_ek += N_res-N_maks
                
                    if condition3:
                        utovere_5.append(utover)
                        ov_krav.append([el.hentOvelse() for el in a if el.hentUtover() is utover]) # øvelser det skal hentes erstatter for
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
            
            b = [el for el in b if (not el in a or el.erNull())]
                            
            c = [el for el in c if (not el in a or el.erNull())]
                    
            b_c = Kalk.sorter(b + c)

            N_tek = Kalk.tell_tek(b_c[:krav_val+N_ek],lop)
                    
            if N_tek >= krav_val_tek+N_ek:
                d = a+b_c[:krav_val+N_ek]
            else:
                d = a+b[:krav_val_tek+N_ek]+c[:krav_val-krav_val_tek+N_ek]
                
                    
            cond1 = True 
            cond2 = True
                
            for i in range(len(utovere_5)): ###### sjekker om noen av utøverne med over 5 øvelser, har fått nye øvelser som må erstattes (skjer hvis erstattingsresulter er av en utøver med mer enn 5 øvelser)
                
                utover_obl = [el.hentOvelse() for el in a if el.hentUtover() == utovere_5[i]] # obligatoriske resultater til utøveren
                
                if len(utover_obl)>len(ov_krav[i]):
                    ov_krav[i] = utover_obl
                    
                    cond1 = False
                    break
                
            utovere = [el.hentUtover() for el in d]
                
            i = 0 ######## sjekker om noen nye utøvere har over 5 øvelser
            for utover in Kalk.setObj(utovere):
                
                condition1 = utovere.count(utover)>N_maks
                condition2 = not utover.erNull()
                condition3 = not utover in utovere_5
                
                if condition1 and condition2 and condition3:
                    
                    cond2 = False
                    break
                    
            if cond1 and cond2:
                break
            
        
        "1.3.2.7. Legger til obl lopsøvelser som erstatter tek. obl øvelser som kan brukes for manglende tekniske valgfri"

        # (...)
            

        "1.3.2.8. Legger til resultater med lik poeng som et annet i obl. listen." # for håndtering av "beste 2. lag"-kravet

        a_ers = [el for el in a_ers if not (el in a or el in a_ers_ny)]
        
        a_poeng = [el.hentPoeng() for el in a]
        a_ovelser = [el.hentOvelse() for el in a]
        
        for el in a_ers_ny+a_ers:
            
            con1 = (el.hentPoeng() in a_poeng) and (el.hentOvelse() not in a_ovelser)
            con2 = any( (el.hentPoeng()==elem.hentPoeng() and el.hentOvelse()==elem.hentOvelse()) for elem in a )
            
            if any((con1,con2)):
                a.append(el)
        
        a = Kalk.sorter(a)
        
        "1.3.2.9. Finner potensielle oblig øvelser som av ulike grunner kan måtte erstattes av null-resultater"
        
        b = [el for el in b if (not el in a or el.erNull())]
                            
        c = [el for el in c if (not el in a or el.erNull())]
        
        b_c = Kalk.sorter(b + c)
                
        N_tek = Kalk.tell_tek(b_c[:krav_val+N_ek],lop) 
                
        if N_tek>=krav_val_tek:
            d = a + b[:krav_val+N_ek]
        else:
            d = a + b[:krav_val_tek+N_ek]+c[:krav_val-krav_val_tek+N_ek]
        
        set_a = [] ######## a gruppert etter øvelse
        for el in a:
            if not el.hentOvelse() in [el2[0].hentOvelse() for el2 in set_a]:
                set_a.append([el])
            else:
                for i in range(len(set_a)):
                    if set_a[i][0].hentOvelse()==el.hentOvelse():
                        set_a[i].append(el)
        

        N_null = 0 # N_null = maks antall resultater som kan erstattes av null-resultater (trengs for tilfeller der en utøver har >5 øvelser deriblant minst en (god) valgfri res, 
        # og der det typisk er få valgfri res totalt. Da vil utøveren som i utg. har 5 gitte obl. øvelser kunne gi fra seg obl. plassen til et 0-resultat for å få med
        # den gode valgfrie øvelsen som bedrer totalsummen.
        
        utovere = [el.hentUtover() for el in d] #  alle utøvere med res blant aktuelle resultater
        
        for utover in Kalk.setObj(utovere):
            if (utovere.count(utover)>N_maks and not utover.erNull()):
                        
                N_null += utovere.count(utover) - N_maks # antall ekstra res til utøveren
                
        if N_null > krav_obl:
            N_null = krav_obl
            
        N_tek = Kalk.tell_tek(a,lop)
        
        lop_sikker = True # om løpsøvelser kan ha sikre resultater. Er ikke tilfelle hvis det ikke er nok plasser til tekniske plasser som vil si at løpsøvelser må ut.
        
        if krav_obl_tek - N_tek > krav_obl - len(set_a): # obl plasser - antall ulike øvelser = tomme plasser som kan være 0-resultater (= teknisk øvelse)
            # krav_obl_tek - N_tek = antall obl tek plasser som er igjen å fylle. Hvis den er større enn tomme plasser, må løpsøvelser erstattes med 0-resultater
            
            N_null += (krav_obl_tek - N_tek) - (krav_obl - len(set_a)) # ekstra null-resultater forårsaket av mangel på nok tekniske øvelser
            
            lop_sikker = False
            
            obl_null = set(obl_null + [el.hentOvelse() for el in a if (el.hentOvelse() in obl) and (not el.erNull())]) # alle lopsovelser fordi enhver potensielt må 'gi fra seg plassen'
            
        
        "1.3.2.10. Lager (og fjerner fra obl. listen) en liste med 'sikre resultater' - resultater som sikkert vil gjelde som obl. resultat"
        
        a_sikker = []

        for utover in Kalk.setObj(utovere):

            condition1 = utovere.count(utover)>N_maks # om utøveren har mer enn 5 øvelser
            condition2 = not utover.erNull()
            if condition1 and condition2:
                        
                d_ut = Kalk.sorter([el for el in d if el.hentUtover()==utover]) # utøverens resultater
                N_si = len([el for el in d_ut[:N_maks] if el in a]) # hvor mange av utøverens resultater som maksimalt kan være sikre
                
                l = 0
                i = 0
                        
                while l<N_si and i<len(set_a) and i<krav_obl:
                            
                    it = [j for j in range(len(set_a[i])) if set_a[i][j].hentUtover()==utover] # liste med iterasjons element nr. til utøverens res, dersom han har res i øvelsen
                        
                    if len(it)==1: # om utøveren har øvelsen som gj. obl
                        l += 1
                        
                        cond1 = (len(set_a[i])==1) # om kun utøveren kan ha øvelsen som obl.
                        cond2 = (not set_a[i][0].er(lop))
                        cond3 = (set_a[i][0].er(lop) and (i<krav_obl-krav_obl_tek) and lop_sikker) # for å forhindre at den sikrer flere lopsovelser enn lovlig
                        
                        if cond1 and (cond2 or cond3):
                            a_sikker.append(set_a[i][it[0]])
                    i += 1
                                        
            if not condition1:
                        
                i = 0            
                while i<len(set_a) and i<krav_obl:
                        
                    it = [j for j in range(len(set_a[i])) if set_a[i][j].hentUtover()==utover]
                    
                    if len(it)==1: # om utøveren har øvelsen som gj. obl
                        
                        like_mer = [el for el in set_a[i] if el.hentPoeng() >= set_a[i][it[0]].hentPoeng()] ## sjekker om andre utøvere har likt eller bedre resultat i øvelsen
                        
                        cond1 = (len(like_mer)==1)
                        cond2 = (not set_a[i][0].er(lop))
                        cond3 = (set_a[i][0].er(lop) and (i<krav_obl-krav_obl_tek) and lop_sikker) # for å forhindre at den sikrer flere lopsovelser enn lovlig
                        
                        if cond1 and (cond2 or cond3):

                            # condition1==False ->  <= 5 øvelser

                            # i<len(set_a)      ->  
                            # i<krav_obl        ->  

                            # if len(it)==1     ->  ovelsen er blant utoverens 5 beste

                            # cond1==True       ->  ingen andre har likt eller bedre resultat i ovelsen
                            # cond2==True       ->  resultatet er teknisk
                            # cond3 er irrelevant teknisk ovelse
                            
                            # endre til: sjekk sikre valgfri+oblig tek res. Av disse ta N_sikre_obl = N_sikre - N_tek_val (hvis > 0) av tek som sikre (de sterkeste resultatene, for bedre res skal i obl)

                            a_sikker.append(set_a[i][it[0]])
                            
                    i += 1
        
        a_sikker = Kalk.sorter(a_sikker)
        
        N_a_ovelser = len(set([el.hentOvelse() for el in a]))
        
        con1 = (len(a_sikker) == N_a_ovelser)
        con2 = (len(a_sikker) == krav_obl)
                
        if any((con1,con2)): ## for å unngå at obl. listen har lengde 0 som gir feilmelding senere
            del a_sikker[-1]

            
        "1.3.2.11. Fordeler ikke-sikre obligatoriske resultater etter øvelse, og legger til eventuelle null-resultater"
        
        a_gruppert = []
        for el in a:
            if not el.hentOvelse() in [el2.hentOvelse() for el2 in a_sikker]: # skal kun iterere gjennom kombinasjoner av ikke-sikre obl. resultater
                if not el.hentOvelse() in [el2[0].hentOvelse() for el2 in a_gruppert]: # hvis øvelsen ikke er lagt til enda
                    a_gruppert.append([el])
                else:
                    for i in range(len(a_gruppert)):
                        if a_gruppert[i][0].hentOvelse()==el.hentOvelse():
                            a_gruppert[i].append(el)

        if len(obl_null)>0: #### legger til null-resultat for de gitte øvelsene
            for i in range(len(a_gruppert)):
                if a_gruppert[i][0].hentOvelse() in obl_null:
                    a_gruppert[i].append(nullresultat)

        "1.3.2.12. Finner alle aktuelle kombinasjoner av obligatoriske oppstillinger"

        liste = []
        if len(a_gruppert)>=krav_obl-len(a_sikker): ## dersom det er flere obl. øvelser enn plasser. Finner først alle kombinasjonene av øvelsesutvalg som fyller opp plassene.
            for ov_liste in combinations(a_gruppert,krav_obl-len(a_sikker)):
                liste += Kalk.kombinasjoner(ov_liste) #-# finner hvilket resultat til hver øvelse
        else:
            liste = Kalk.kombinasjoner(a_gruppert)
            
        if liste==None:
            liste = [[nullresultat]]
        
        
        N_obl_lop = krav_obl - krav_obl_tek ### N_obl_lop = antall løpsøvelser som kan brukes fra obl. listen
        if len(a_sikker)>0:
            N_obl_lop = krav_obl - krav_obl_tek - (len(a_sikker) - Kalk.tell_tek(a_sikker,lop))
            
        """
        if len(a_sikker)>0:
                                    
            poeng1_si = tuple(np.array(a_sikker)[:,0].astype(int))
            ovelse1_si = tuple(np.array(a_sikker)[:,2])
            navn1_si = tuple(np.array(a_sikker)[:,1])
        else:
            poeng1_si = ()
            ovelse1_si = ()
            navn1_si = ()
        """
            
        utover_si = [el.hentUtover() for el in a_sikker]
        
        ny_liste = [] ######### Fjerner siste ugyldige/for dårlige kombinasjoner
        for el in liste:
            
            utover = utover_si + [elem.hentUtover() for elem in el if not elem.erNull()]
            
            con1 = ((not el.count(nullresultat) > N_null) or len(el)==1) # at det ikke er flere null-resultatserstatninger enn maksimal mhp. mest mulig poeng, siste del er hardkodet inn for at Bardu IL skal fungere (generell mate ma lages)
            con2 = (not len(el)-Kalk.tell_tek(el,lop) > N_obl_lop) # at det ikke er flere obl. løpsøvelser enn maksimum
            if (len(utover)>0):
                con3 = (not utover.count(max(Kalk.setObj(utover), key = utover.count)) > N_maks) # at alle utøvere har mindre (eller lik) enn 5 gjeldende obl. res
            else:
                con3 = True
            
            if all((con1,con2,con3)):
                ny_liste.append(el)
        liste = ny_liste[:]
        
        "1.3.2.13. Finner høyeste mulige poeng til valgfrie øvelser - er med på å bestemme beregningsavslutning"
        
        ######## regner ut den høyeste mulig b og c summen for å exite beregning når de obligatoriske øvelsene gir en for lav sum til å kunne forbedre seriepoengene.
        
        b_val = Kalk.sorter([el for el in bi if (el not in a_sikker+a_i) or el.erNull()]) # ikke-sikre tekniske resultater som vil kunne være i valgfri oppstilling
        c_val = Kalk.sorter([el for el in ci if (el not in a_sikker+a_i) or el.erNull()]) # ikke-sikre løpsresultater som vil kunne være i valgfri oppstilling
        
        b_c = Kalk.sorter(b_val+c_val)
        
        N_tek = Kalk.tell_tek(b_c[:krav_val],lop)
            
        if N_tek>=krav_val_tek:
            maks_val = Kalk.sumPoeng(b_c[:krav_val]) # høyeste mulig poengsum for til en valgfri oppstilling
        else:
            maks_val = Kalk.sumPoeng(b_val[:krav_val_tek]+c_val[:(krav_val - krav_val_tek)])

        sum_liste = [[Kalk.sumPoeng(komb),komb] for komb in liste] ## sorterer obl-kombinasjonene etter poeng (muliggjør å exite når det er for lite obl. poeng)

        liste = [komb for poeng,komb in sorted(sum_liste, key = lambda x: int(x[0]))[::-1]]
                
        n = -1
        
        "1.3.2.14. Til hver lagkombinasjon, beregner poengsum, og eventuelt lagrer laginfo"
        
        "1.3.2.14.1. Itererer gjennom kombinasjoner av obligatoriske oppstillinger"

        for obl_usikker in liste:
            
            obl_komb = a_sikker + list(obl_usikker)

            """
            poeng1 = tuple(np.array(obl_usikker)[:,0].astype(int))
            ovelse1 = tuple(np.array(obl_usikker)[:,2])
            navn1 = tuple(np.array(obl_usikker)[:,1])
            """
            
            unntatte = [] # resultater som fjernes fra potensielle valgfri fordi de ville ha maattet vaere obligatoriske for aa kunne gjelde
            
            for i in range(len(obl_usikker)):
                for j in range(len(a_gruppert)):
                    if a_gruppert[j][0].hentOvelse()==obl_usikker[i].hentOvelse(): # sjekker potensielle oblig. øvelser opp mot de gitte
                        
                        pos = None
                        for l in range(len(a_gruppert[j])):
                            if a_gruppert[j][l].hentUtover()==obl_usikker[i].hentUtover():
                                pos = l
                                break
                            
                        for l in range(pos+1): ## legger til resultater som i samme øvelse har mer poeng
                            unntatte.append(a_gruppert[j][l])
            
            """
            poeng1 = poeng1 + poeng1_si
            ovelse1 = ovelse1 + ovelse1_si
            navn1 = navn1 + navn1_si
            """
                    
            if Kalk.sumPoeng(obl_komb)+maks_val<n: ## dersom obl. kombinasjonen (og alle etter den ettersom de er sortert etter poeng) gir for lite poeng i forhold til n exites beregningen
                break
            
            b = Kalk.sorter([el for el in bi if (el not in obl_komb+unntatte) or el.erNull()])
            
            c = Kalk.sorter([el for el in ci if (el not in obl_komb+unntatte) or el.erNull()]) 

            b_c = Kalk.sorter(b+c)
            N_tek = Kalk.tell_tek(b_c[:krav_val+N_ek],lop) 
                    
            if N_tek>=krav_val_tek:
                b_c = Kalk.sorter(b[:krav_val+N_ek])
            else:
                b_c = Kalk.sorter(b[:krav_val_tek+N_ek]+c[:krav_val-krav_val_tek+N_ek])
            
            "1.3.2.14.2. Finner antall gjenværende øvelser til utøvere med over 5 resultater totalt"
                    
            utovere = [el.hentUtover() for el in b_c]
            utovere_obl = [el.hentUtover() for el in obl_komb]
            
            begrensing = {}
            for utover in Kalk.setObj(utovere):
                if (utovere+utovere_obl).count(utover) > N_maks and not utover.erNull(): # hvis utøveren har flere totalt har flere enn 5 resultater
                    N_obl_ut = utovere_obl.count(utover)
                    begrensing[utover] = [N_maks-N_obl_ut,N_maks-N_obl_ut,N_maks-N_obl_ut] # gj. øvelser til utøveren
                
                
            "1.3.2.14.3. Finner en valgfri oppstilling like god eller bedre enn beste gyldig oppstilling"
            
            """
            delen under maa skrives om. Antakelig kan bare .index brukes uten problemer
            
            
            
            
            
            
            ------------------------------------------
            """
            
            t_valgfri = [] # teoretisk valgfri oppstilling. Vil være lik eller bedre enn faktisk beste oppstilling
            if len(begrensing)>0:
                
                begr_utovere = list(begrensing.keys())
                
                for i in range(len(b_c)):
                    oop = 1
                    if b_c[i].hentUtover() in begr_utovere: # hvis utøveren har begrensing i antall gj. øvelser (fordi >5 totalt)
                        
                        begr = begrensing[b_c[i].hentUtover()]
                        
                        if begr[2]<=0:
                            oop = 0
                            break
                        else:
                            begr[2] -= 1
                            break              
                    if oop == 1:
                        t_valgfri.append(b_c[i])
            else:
                t_valgfri = b_c
                
                
            "1.3.2.14.4. Skipper til neste obligatoriske oppstillingen dersom den teoretiske valgfri oppstillingen er for svak"
                        
            if len(t_valgfri)>krav_val:
                t_valgfri = t_valgfri[:krav_val]
                    
            if len(t_valgfri)>0:
                if Kalk.sumPoeng(t_valgfri+obl_komb)<n:
                    continue
            else:
                if Kalk.sumPoeng(obl_komb)<n:
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
                    
            while len(b_c)<krav_val: ## fyller eventuelle rest plasser med null resultater
                b_c.append(nullresultat)   
                                
            b = [el for el in b_c if (not el.erNull()) and (not el.er(lop))] ### henter de beste tekniske øvelsene
            
            while len(b)<krav_val_tek:
                b.append(nullresultat)
            
            
            "1.3.2.14.6. Finner start- og sluttverdi av antall tekniske øvelser blant de valgfrie"    
            
            if len(b)>krav_val: #### finner start- og sluttverdi for antall tekniske valgfri øvelser som det skal sjekkes for
                N_maks_tek = krav_val
            else:
                N_maks_tek = len(b)
                
                
            "1.3.2.14.7. Henter eventuelle resultater like gode som den/de svakeste blant valgfri tekniske"    
            
            b_pot = Kalk.sorter([el for el in bi if not (el in b or el.erNull() or el.hentUtover() in utovere_obl)]) ############# Legger til tekniske valgfri øvelser som har lik poeng som den dårligste i valgfri tek. listen
            
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

            utovere = [el.hentUtover() for el in b_c]

            begr = [] ##### finner de gj. tekniske øvelsene til >5 res utøvere
            for utover in Kalk.setObj(utovere):
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
            
            liste_tek_i = Kalk.kombinasjoner(liste_N_tek) ##### finner alle kombinasjoner av antall tekniske resultater som vil itereres gjennom fra >5 res utøvere. 
            

            "1.3.2.14.9. Beregner samlet poengsum, og lagrer laginfo, til beste valgfri og den gitte obligatoriske oppstillingen"    

            "1.3.2.14.9.1. Itererer gjennom et intervall av antall mulige teknisk valgfrie øvelser"

            for N_tek in range(krav_val_tek,N_maks_tek+1): # tek = antall tekniske valgfri resultater

                b = [el for el in b_i if not el in b_5_unostet] # fjerner overlappende resultater med b_5 (5> utøvernes res håndteres sepearat fra de andre resultatene)
                
                if liste_tek_i == None:
                    kombs_tek = [[]]
                else:
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
                        tek_res = Kalk.sorter(res_5 + b[:N_tek-len(res_5)])
                                
                    elif len(b)==0:
                        tek_res = Kalk.sorter(res_5)
                                    
                    else:
                        tek_res = Kalk.sorter(res_5 + b)
                        
                    
                    "1.3.2.14.9.3. Henter eventuelle resultater like gode som det svakeste av de tekniske valgfri"
                    
                    b = [el for el in b if not el in tek_res] # finner b-resultater som ikke overlapper med tek_sikker
                    
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
                    
                    tek_sikker = [el for el in tek_res if not el in like_res] # fjerner dårligste tek. res
                    
                    i = 0 ####### Henter inn eventuelle resultater med likt antall poeng som de den/de svakeste i val. tek. Enhver av disse kan erstatte den eller de dårligste.
                    while len(b)>i:
                        if b[i].hentPoeng()==P_svak_res and P_svak_res != 0:
                            like_res.append(b[i])
                            i += 1
                        else:
                            break
                        
                        
                    "1.3.2.14.9.4. Itererer gjennom kombinasjoner av den/de svakeste resultatene blant tekniske valgfri"
                    
                    for tek_usikker in combinations(like_res,N_gj_res): # itererer gjennom kombinasjoner svakeste res. i de valgfri tekniske øvelsene. Dette er viktig for å finne beste lagoppstilling mhp. beste 2. lag.
                    
                        
                        tek_komb = tek_sikker + list(tek_usikker) # samler de valgfri tekniske øvelsene
                        
                        if len(tek_komb)>krav_val:
                            tek_komb = tek_komb[:krav_val]
                        
                        """
                        poeng2 = tuple(np.array(tek)[:,0].astype(int))
                        ovelse2 = tuple(np.array(tek)[:,2])
                        navn2 = tuple(np.array(tek)[:,1])
                        
                        if len(poeng2) > krav_val:
                            
                            poeng2 = poeng2[:krav_val]
                            ovelse2 = ovelse2[:krav_val]
                            navn2 = navn2[:krav_val]
                        
                        """
                        
                            
                        "1.3.2.14.9.5. Fyller gjenværende valgfrie plasser med løpsøvelser og beregner poengsum"
        
                        if krav_val - len(tek_komb)>0: # sjekker om det er gjenværende plass til løpsøvelser. Hvis ikke, har vi en allerede en komplett oppstilling.
                            
                            c = c_i[:]
                            
                            utovere = [el.hentUtover() for el in tek_komb+obl_komb]
                                        
                            maks = [] #### utøvere som allerede har brukt sine 5 øvelser
                            for utover in Kalk.setObj(utovere):
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
                                            
                                utovere_like_res = [el.hentUtover() for el in like_res]
                                
                                if (c[i].hentUtover() not in maks) and (c[i].hentUtover() not in utovere_like_res):
                                    like_res.append(c[i])
                                i += 1
                            
                            lop_si = [el for el in lop_si if not el in like_res] # fjerner løpsresultatene lik den med svakest antall poeng
                            
                            """
                            if len(val_lop)>0:
                                poeng3_si = tuple(np.array(val_lop)[:,0].astype(int))
                                ovelse3_si = tuple(np.array(val_lop)[:,2])
                                navn3_si = tuple(np.array(val_lop)[:,1])
                            else:
                                poeng3_si = ()
                                ovelse3_si = ()
                                navn3_si = ()
                            """
                            
                            for lop_ek in combinations(like_res,N_gj_res): # itererer gjennom kombinasjoner av løpsresultatene med svakest poeng. 
                                
                                lop_komb = lop_si + list(lop_ek)
                                
                                """
                                poeng3 = poeng3_si + tuple(np.array(val_lop)[:,0].astype(int).tolist())
                                ovelse3 = ovelse3_si + tuple(np.array(val_lop)[:,2].tolist())
                                navn3 = navn3_si + tuple(np.array(val_lop)[:,1].tolist())
                                """
                                
                                set_utovere = Kalk.setObj([el.hentUtover() for el in obl_komb+tek_komb+lop_komb if not el.erNull()])
                                
                                s = Kalk.sumPoeng(obl_komb + tek_komb + lop_komb)
                                                                
                                if s>n: ###... hvis høyere poengusm - oppdaterer laginfo
            
                                    n = s
                                        
                                    lag = [[s,obl_komb,tek_komb+lop_komb]]
            
                                    utover_liste = [set_utovere]
                                                                
                                elif s==n and set_utovere not in utover_liste: ###... hvis lik poengsum - legger til en ekstra lagoppstilling. Senere vil det vurderes hvilken av disse som gir beste 2. lag.
                    
                                    utover_liste.append(set_utovere)
                                    lag.append([s,obl_komb,tek_komb+lop_komb])
                        
                        else:
                                
                            set_utovere = Kalk.setObj([el.hentUtover() for el in lop_komb+tek_komb if not el.erNull()])
                            
                            s = Kalk.sumPoeng(obl_komb + tek_komb)
                                                            
                            if s>n: ###... hvis høyere poengusm - oppdaterer laginfo
        
                                n = s
                                    
                                lag = [[s,obl_komb,tek_komb]]
        
                                utover_liste = [set_utovere]
                                                            
                            elif s==n and set_utovere not in utover_liste: ###... hvis lik poengsum - legger til en ekstra lagoppstilling. Senere vil det vurderes hvilken av disse som gir beste 2. lag.
                
                                utover_liste.append(set_utovere)
                                lag.append([s,obl_komb,tek_komb])

        "1.3.2.15. Bruker rekursjon til å finne beste lag av to (eller flere) med samme poeng, basert på de neste lagene til klubben"
        
        if steg == 0:
            lag_info = lag[0]
                
        if len(utover_liste)==1: ## hvis kun en optimal lagoppstilling, returnerer direkte laginfoen

            return [n_liste+[n],lag_info]

        else:   

            like_lag = [] # liste med lag_info av to eller flere lag med likt antall seriepeong
            
            resultater_i = resultater[:] # gjenværende resultater til klubben. Lagres ettersom den senere endres ved iterasjon.
                
            for i in range(len(utover_liste)):###### finner poeng til neste lag (2. lag hvis dette er 1. lag) til de ulike lagoppstillingene
                
                if steg == 0: ## lager laginfo lister til hver "optimale" lagoppstilling
                    lag_info = lag[i]
                    
                resultater = [el for el in resultater_i[:] if not el.hentUtover() in utover_liste[i]]
                
                like_lag.append(Kalk.rekursiv_kalkulator(datasenter,klubb,lag_nr,resultater,lag_info,n_liste+[n],steg+1))
            
            i = 0
            while True:
                
                len_n_liste = [len(el[0]) for el in like_lag] # rekursiv iterasjonsdybde (2 - neste lag, 3 - de to neste lagene, osv)
                
                if i>=max(len_n_liste) or len(like_lag)==1: ## i>=høyeste iterasjonsdybde vil si at lagene er like gode og kombinasjon kan velges vilkårlig.
                    break    
                
                liste_poeng_lister = [el[0] for el in like_lag] # liste med alle aktuelle lister av poenger til klubbens ulike lag
                P_gj_lag = []
                for poeng_liste in liste_poeng_lister: # l = liste med poenger til 1. lag, 2. lag osv
                    if len(poeng_liste)>i: # len(l) = iterasjonsdybde
                        P_gj_lag.append(poeng_liste[i]) # henter gjeldende poeng til det siste laget (poengene til alle de øvrige lagene vil være like)

                beste_lag = [] ##### sammenlikner poengene og henter ut kun det beste
                for laginfo in like_lag:
                    if len(laginfo[0])>i:
                        if laginfo[0][i]==max(P_gj_lag): # hvis lagoppstillingen har likt antall poeng som høyeste mulig
                            beste_lag.append(laginfo)
                
                like_lag = beste_lag
                
                i += 1
                
            # Returnerer laginfo med den beste oppstillingen. Ettersom det er en rekursiv funksjon vil den beregne seg først nedover alle lag helt til den finner en entydig beste lagoppstilling. Ut ifra denne kan den velge beste lagoppstilling av flere som gir samme poeng.
            # Eksempelvis betyr dette at for en klubb som har to oppstillinger med samme beste poengsum, samt samme beste 2. lag, 3. lag, men ulikt 4. lag, vil algoritmen regne ulike ruter ned og sammenlikne 4. lagene slik at den finne den mest ideelle lagoppstillingen.
            
            return like_lag[0]

    @staticmethod
    def LagKalk(datasenter,klubb):

        "1.2. Finner klubbens beste resultater"

        kjonn = klubb.hentKjonn()
        klubbres = klubb.hentResultater()

        besteKlubbres = klubbres.set()
            
        "1.3. Looper gjennom lagene til en klubb"        
        
        lag_nr = 1 # lag til klubb (1 -> 1. lag, 2 -> 2. lag, osv)

        while len(besteKlubbres)>0: # nytt lag dersom det er gj. res.
            
            "1.3.2. Beregner seriepoeng og annen tilhørende informasjon til lag"
            
            n,obl_lag,val_lag = Kalk.rekursiv_kalkulator(datasenter,klubb,lag_nr,besteKlubbres,[],[],0)[1]

            "1.3.3. Finner relevante statuetter, prosesserer og så lagrer laginformasjon fra beregning." 
            
            lag = klubb.hentLag(lag_nr)
            div = klubb.hentDiv(lag_nr)
        
            ovelsesinfo = datasenter.ovelsesinfo()
            
            obl_sekvens = ovelsesinfo["sluttform"] # inkluderer ogsa ikke-obl ovelser, men er uten betydning


            obl_lag = [el for x in obl_sekvens for el in obl_lag if el.hentOvelse() == x]
            val_lag = Kalk.sorter([res for res in val_lag])
            
            tabell = datasenter.tabell(kjonn)

            lag.settLagoppstilling(obl_lag,val_lag)
            tabell.plasserLag(lag)

            "1.3.4. Klargjør for beregning av klubbens neste lag."
            
            brukte_utovere = Kalk.setObj([el.hentUtover() for el in obl_lag+val_lag])
            
            besteKlubbres = [el for el in besteKlubbres if el.hentUtover() not in brukte_utovere] # fjerner "brukte" utøvere fra gjenværende klubbresultater.
            
            lag_nr += 1
        
        