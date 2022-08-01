
class Tabell:

    def __init__(self,datasenter):

        self._datasenter = datasenter
        self._divisjoner = {}
        
        self._divisjoner.setdefault("1.div", {"Tabell": [], "Nullere": []})
        self._divisjoner.setdefault("2.div", {"Tabell": [], "Nullere": []})
        self._divisjoner.setdefault("3.div", {"Tabell": [], "Utenfor": [], "Svake": [], "Nullere": []})

    def __str__(self):

        streng = ""
        for divisjon in self._divisjoner.values():
            streng += "------\n"
            for deldivisjon in divisjon:
                streng += "\n--\n" + deldivisjon + "\n--\n"
                for lag in divisjon[deldivisjon]:
                    streng += str(lag.hentPosisjon()) + ". " + str(lag)+"\n"
        return streng

    def hentDivisjon(self,div):
        return self._divisjoner[str(div)+".div"]

    def plasserLag(self,nyttLag):

        self._fjernLag(nyttLag)
        self._leggTilLag(nyttLag)

    def _fjernLag(self,nyttLag):

        posisjon = nyttLag.hentPosisjon()

        if posisjon==None:
            return

        settinger = self._datasenter.settinger()
        poenggrenser = settinger["poenggrenser 3. div"]

        poeng = nyttLag.hentPoeng()
        div = nyttLag.hentDiv()

        if poeng==0:
            gjDeltabell = "Nullere"
        elif (poeng<poenggrenser[1] and div==3):
            gjDeltabell = "Svake"
        elif (poeng<poenggrenser[0] and div==3):
            gjDeltabell = "Utenfor"
        else:
            gjDeltabell = "Tabell"

        divisjon = self.hentDivisjon(div)
        deltabell = divisjon[gjDeltabell]

        senkPos = False
        for lag in deltabell:
            if nyttLag is lag:
                senkPos = True
            elif senkPos: ## senker posisjonen til alle lag svakere enn det nye laget som fjernes
                lag.senkPos()

        deltabell.remove(nyttLag)

    def _leggTilLag(self,nyttLag):

        settinger = self._datasenter.settinger()
        poenggrenser = settinger["poenggrenser 3. div"]

        div = nyttLag.hentDiv()
        divisjon = self.hentDivisjon(div)

        poeng = nyttLag.hentPoeng()

        if poeng==0:
            gjDeltabell = "Nullere"
        elif (poeng<poenggrenser[1] and div==3):
            gjDeltabell = "Svake"
        elif (poeng<poenggrenser[0] and div==3):
            gjDeltabell = "Utenfor"
        else:
            gjDeltabell = "Tabell"

        lagForan = 0
        svakereLag = []

        svakere = False
        for deltabell in divisjon:
            if gjDeltabell==deltabell:
                svakere = True

            elif svakere:
                svakereLag += divisjon[deltabell]
            else:
                lagForan += len(divisjon[deltabell])


        for i,lag in enumerate(divisjon[gjDeltabell]):
            if nyttLag>lag:
                nyttLag.settPos(lagForan+i)
                divisjon[gjDeltabell].insert(i,nyttLag)
                
                for lag in divisjon[gjDeltabell][i+1:]+svakereLag: ## oker posisjonen til alle svakere lag
                    lag.okPos()
                return

        nyttLag.settPos(lagForan+len(divisjon[gjDeltabell]))
        divisjon[gjDeltabell].append(nyttLag)

        for lag in svakereLag: ## oker posisjonen til alle svakere lag
            lag.okPos()