from database.impianto_DAO import ImpiantoDAO
from model.impianto_DTO import Impianto
from database.consumo_DAO import ConsumoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        risultati = []
        for impianto in self._impianti:
            lista_consumi = impianto.get_consumi()
            consumi_totali = 0.0
            giorni = 0
            for consumo in lista_consumi:
                # visto che in consumo_DTO la data è inizializzata come datetime.date, uso consumo.data.month == mese
                # per estrarre il mese
                if consumo.data.month == mese:
                    giorni = giorni + 1
                    consumi_totali = consumi_totali + consumo.kwh
            if giorni > 0:
                media = consumi_totali / giorni
            else:
                media = 0.0
            risultati.append((impianto.nome, media))
        return risultati

        # TODO

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """
        Ricorsione per trovare la sequenza ottimale di interventi nei primi 7 giorni.
        """
        # Caso base: abbiamo pianificato tutti i 7 giorni
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

        # Prova ciascun impianto (ad es. A e B)
        for id_impianto, consumi in consumi_settimana.items():
            # Costo consumo giornaliero
            costo_giorno = consumi[giorno - 1].kwh

            # Se si cambia impianto rispetto al giorno precedente, aggiungi costo di spostamento
            if ultimo_impianto is not None and id_impianto != ultimo_impianto:
                costo_giorno += 5

            # Aggiorna la sequenza
            nuova_sequenza = sequenza_parziale + [id_impianto]
            nuovo_costo = costo_corrente + costo_giorno

            # Potatura semplice (se già oltre il miglior costo trovato)
            if self.__costo_ottimo != -1 and nuovo_costo >= self.__costo_ottimo:
                continue

            # Ricorsione per il giorno successivo
            self.__ricorsione(nuova_sequenza, giorno + 1, id_impianto, nuovo_costo, consumi_settimana)
        # TODO

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        consumi = {}
        for impianto in self._impianti:
            consumi_mese = [c for c in impianto.get_consumi() if c.data.month == mese]
            consumi[impianto.id] = consumi_mese[:7]
        return consumi
        # TODO
