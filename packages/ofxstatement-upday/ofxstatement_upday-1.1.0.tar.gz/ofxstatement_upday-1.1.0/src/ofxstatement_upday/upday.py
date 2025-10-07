"""
UpDay Plugin per ofxstatement - Conversione CSV -> OFX

Questo modulo contiene il plugin per ofxstatement che converte i file CSV
generati da upday-download nel formato OFX standard.

NOTA: Questo plugin funziona in combinazione con il comando 'upday-download'.
      Vedi 'upday-download --help' per maggiori informazioni sul workflow completo.
"""

import csv
import os
import re
from datetime import datetime
from decimal import Decimal
from io import TextIOWrapper
from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import Statement, StatementLine
from typing import Iterable


# ============================================================================
# OFXSTATEMENT PLUGIN CLASSES
# ============================================================================


class UpDayPlugin(Plugin):
    """UpDay Buoni Pasto plugin - converts CSV files to OFX format"""

    def get_parser(self, filename: str) -> "UpDayParser":
        """Main entry point for parsers - parses existing CSV files"""
        # Verifica che il file esista
        if not os.path.exists(filename):
            print(f"❌ ERRORE: File '{filename}' non trovato")
            print()
            print("Assicurati di:")
            print("1. Aver eseguito prima 'upday-download' per scaricare i dati")
            print("2. Specificare il percorso corretto del file CSV")
            print()
            print("Per vedere come usare il workflow completo, esegui:")
            print("  upday-download --help")
            exit(1)

        f = open(filename, 'r', encoding=self.settings.get("charset", "UTF-8"))
        default_account = self.settings.get("default_account", "UPDAY_BUONI_PASTO")
        return UpDayParser(f, default_account)


class UpDayParser(CsvStatementParser):
    """Parser per i file CSV di UpDay - converte in formato OFX"""

    date_format = "%d/%m/%Y"

    # Csv column names
    columns = ["data", "ora", "descrizione_operazione", "tipo_operazione", "numero_buoni", "valore", "luogo_utilizzo", "indirizzo", "codice_riferimento", "pagina_origine"]

    mappings = {
        'date': 'data',
        'memo': 'descrizione_operazione',
        'amount': 'valore'
    }

    def __init__(self, csv_file: TextIOWrapper, account_id: str) -> None:
        super().__init__(csv_file)
        self.statement.account_id = account_id

    def parse(self) -> Statement:
        """Parse del file CSV e creazione dello statement OFX"""
        stmt = super().parse()

        # Imposta informazioni account da configurazione
        stmt.currency = 'EUR'
        stmt.bank_id = 'UPDAY'

        return stmt

    def split_records(self) -> Iterable[str]:
        """Return iterable object consisting of a line per transaction"""

        reader = csv.reader(self.fin, delimiter=',')
        next(reader, None)
        return reader

    def parse_record(self, line: str) -> StatementLine:
        """Parse della singola riga CSV """

        row_dict = dict(zip(self.columns, line))

        # Crea oggetto StatementLine
        stmt_line = StatementLine()

        # Parse data
        try:
            parsed_date = datetime.strptime(row_dict['data'], self.date_format)
            stmt_line.date = parsed_date  # Passa datetime completo, non solo date
        except (ValueError, KeyError):
            return StatementLine()  # Ritorna StatementLine vuoto invece di None

        # Parse importo usando Decimal per compatibilità OFX
        try:
            stmt_line.amount = Decimal(str(row_dict['valore']))
        except (ValueError, KeyError):
            stmt_line.amount = Decimal('0.0')

        # Crea ID unico per la transazione
        date_str = row_dict.get('data', '')
        time_str = row_dict.get('ora', '')
        amount_str = row_dict.get('valore', '')
        ref_code = row_dict.get('codice_riferimento', '')

        # ID basato su data, ora, importo e codice riferimento
        unique_id = re.sub(r'[\/: ,\.]', '', f"{date_str}_{time_str}_{amount_str}_{ref_code}")
        stmt_line.id = unique_id

        # Determina il tipo di operazione per personalizzare il memo
        tipo_op = row_dict.get('tipo_operazione', '')

        if tipo_op == 'credit':
            # MEMO PER ACCREDITI - stile specifico con mese di assegnazione
            try:
                # Estrai il mese dalla data per determinare il mese di assegnazione
                parsed_date = datetime.strptime(row_dict['data'], self.date_format)
                mese_nomi = {
                    1: 'Gennaio', 2: 'Febbraio', 3: 'Marzo', 4: 'Aprile',
                    5: 'Maggio', 6: 'Giugno', 7: 'Luglio', 8: 'Agosto',
                    9: 'Settembre', 10: 'Ottobre', 11: 'Novembre', 12: 'Dicembre'
                }
                mese_nome = mese_nomi.get(parsed_date.month, 'Sconosciuto')

                # Numero buoni accreditati
                num_buoni = row_dict.get('numero_buoni', '0')
                if num_buoni and num_buoni != '0':
                    stmt_line.memo = f"Buoni pasto assegnati per il mese di {mese_nome} (+{num_buoni})"
                else:
                    stmt_line.memo = f"Buoni pasto assegnati per il mese di {mese_nome}"

                # Aggiungi codice riferimento se disponibile
                if row_dict.get('codice_riferimento'):
                    stmt_line.memo += f" - Cod.Rif: {row_dict['codice_riferimento']}"

            except:
                # Fallback se c'è un errore nel parsing della data
                stmt_line.memo = row_dict.get('descrizione_operazione', 'Accredito Buoni')
                if row_dict.get('numero_buoni') and row_dict.get('numero_buoni') != '0':
                    stmt_line.memo += f" (+{row_dict['numero_buoni']})"

            stmt_line.trntype = 'DEP'

        elif tipo_op == 'usage':
            # MEMO PER UTILIZZI - stile come negli acquisti con luogo e orario
            memo_parts = []

            # Nome esercente se disponibile
            luogo = row_dict.get('luogo_utilizzo', '').strip()
            if luogo:
                memo_parts.append(f"Spesa al {luogo}")
            else:
                memo_parts.append("Spesa")

            # Numero buoni utilizzati
            num_buoni = row_dict.get('numero_buoni', '0')
            if num_buoni and num_buoni != '0':
                try:
                    buoni_int = int(num_buoni)
                    if buoni_int == 1:
                        memo_parts.append(f"{buoni_int} buono pasto")
                    else:
                        memo_parts.append(f"{buoni_int} buoni pasto")
                except ValueError:
                    pass

            # Aggiungi indirizzo se disponibile
            if row_dict.get('indirizzo'):
                memo_parts.append(f"({row_dict['indirizzo']})")

            # Aggiungi ora se significativa (non 00:00)
            if row_dict.get('ora') and row_dict['ora'] != '00:00':
                memo_parts.append(f"ore {row_dict['ora']}")

            stmt_line.memo = ' - '.join(memo_parts)
            stmt_line.trntype = 'PAYMENT'

        else:
            # Fallback per tipi di operazione sconosciuti
            stmt_line.memo = row_dict.get('descrizione_operazione', 'Transazione')
            stmt_line.trntype = 'OTHER'

        return stmt_line
