
class Resultater: # liste med resultater, automatisk sortert etter poeng

    def __init__(self):
        self._resultater = []

    def __len__(self):
        return len(self._resultater)

    def __str__(self):
        streng = "["
        for res in self._resultater:
            streng += "(" + str(res) + "),"
        return streng + "]"

    def __iter__(self):
        return self._resultater.__iter__()

    def __next__(self):
        return self._resultater.__next__()

    def append(self,resultat):
        for i,res in enumerate(self._resultater):
            if res<resultat:
                self._resultater.insert(i,resultat)
                return
        
        self._resultater.append(resultat)

    def remove(self,res):
        self._resultater.remove(res)

    def hent(self):
        return self._resultater

    def set(self):
        resultater = [] # finner en utovers beste resultat i en ovelse
        for res1 in self._resultater:
            con1 = (not any(all((res1.hentUtover() is res2.hentUtover(),res1.hentOvelse()==res2.hentOvelse())) for res2 in resultater))
            con2 = (not res1.erNull())
            if all((con1,con2)):
                resultater.append(res1)
        return resultater

    def avvik(self):
        return [res for res in self._resultater if res.hentKlubbFra()!=res.hentKlubbTil()]
    