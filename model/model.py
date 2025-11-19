from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi
        self.relazioni_map={}
        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # TODO
        self.relazioni_map = TourDAO.get_tour_attrazioni()
        for relazione in self.relazioni_map:

            self.tour_map[relazione["id_tour"]].attrazioni.add(self.attrazioni_map[relazione["id_attrazione"]])
            self.attrazioni_map[relazione["id_attrazione"]].tour.add(self.tour_map[relazione["id_tour"]])

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        self._id_regione = id_regione
        self._max_giorni = max_giorni if max_giorni is not None else float('inf')
        self._max_budget = max_budget if max_budget is not None else float('inf')

        self._ricorsione(0,[],0,0,0,set())
        return self._pacchetto_ottimo, self._costo, self._valore_ottimo


    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
        if costo_corrente > self._max_budget or durata_corrente > self._max_giorni:
            return

        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._costo = costo_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()

        tours = self.tour_disponibili()
        for i in range(start_index,len(tours)):
            tour=tours[i]
            attrazioni_non_usate = tour.attrazioni.difference(attrazioni_usate)
            if attrazioni_non_usate:
                pacchetto_parziale.append(tour)
                nuovo_costo = costo_corrente + tour.costo
                nuova_durata = durata_corrente + tour.durata_giorni
                nuovo_valore = valore_corrente + sum (a.valore_culturale for a in attrazioni_non_usate)
                nuovo_attrazioni_usate = attrazioni_usate | tour.attrazioni
                self._ricorsione(i+1,pacchetto_parziale,nuova_durata,nuovo_costo,nuovo_valore,nuovo_attrazioni_usate)
                pacchetto_parziale.pop()

    def tour_disponibili(self):
        return [tour for tour in self.tour_map.values() if tour.id_regione == self._id_regione]
