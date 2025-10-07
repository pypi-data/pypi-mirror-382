"""
UpDay Download Script - Web scraping per scaricare transazioni da utilizzatori.day.it

Questo modulo contiene tutte le funzionalità per il download automatico
dei dati dal sito UpDay tramite web scraping con Selenium.
"""

import csv
import os
import re
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# ============================================================================
# DATE VALIDATION FUNCTIONS
# ============================================================================

def _validate_start_date(start_date: str) -> bool:
    """
    Valida che la data di inizio non sia antecedente a 1 anno fa

    Args:
        start_date: Data di inizio nel formato gg/mm/aaaa

    Returns:
        True se la data è valida, False altrimenti
    """
    try:
        # Parse della data di inizio
        start_dt = datetime.strptime(start_date, "%d/%m/%Y").date()

        # Calcola la data limite (1 anno fa da oggi + 1 giorno per evitare problemi dovuti all'orario di esecuzione)
        one_year_ago = (datetime.now() - timedelta(days=364)).date()

        # Verifica se la data di inizio è troppo vecchia
        if start_dt < one_year_ago:
            print("\n" + "=" * 70)
            print("❌ ERRORE: DATA DI INIZIO NON VALIDA")
            print("=" * 70)
            print(f"🚫 Data inserita: {start_date}")
            print(f"📅 Data limite del sito: {one_year_ago.strftime('%d/%m/%Y')}")
            print(f"⚠️  Il sito UpDay non permette di accedere a dati antecedenti a 1 anno fa.")
            print(f"✅ La prima data ammissibile è: {one_year_ago.strftime('%d/%m/%Y')}")
            print("\n💡 Suggerimento: Inserisci una data di inizio più recente.")
            print("=" * 70)
            return False

        return True

    except ValueError:
        print(f"❌ Errore nel parsing della data: {start_date}")
        return False
    except Exception as e:
        print(f"❌ Errore nella validazione della data: {e}")
        return False


def get_date_from_user(info: str = "inizio", optional: bool = False) -> str:
    """Chiede all'utente di inserire la data"""
    while True:
        date_input = input(f"Inserisci la data di {info} (formato gg/mm/aaaa, g/m/aa, ecc.): ").strip()
        if optional and date_input == "":
            return ""
        # Prova diversi formati di data
        date_formats = [
            "%d/%m/%Y",
            "%d/%m/%y",
            "%d-%m-%Y",
            "%d-%m-%y",
            "%d.%m.%Y",
            "%d.%m.%y"
            ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_input, fmt)
                # Converte nel formato richiesto dal sito (gg/mm/aaaa)
                formatted_date = parsed_date.strftime("%d/%m/%Y")

                # Valida la data solo per la data di inizio (non opzionale)
                if not optional and not _validate_start_date(formatted_date):
                    break  # Esci dal loop dei formati e richiedi una nuova data

                return formatted_date
            except ValueError:
                continue

        # Se arriviamo qui, o il formato non è valido o la data non è ammissibile
        if not optional:
            # Per la data di inizio, mostra un messaggio più specifico
            one_year_ago = datetime.now() - timedelta(days=365)
            print(f"⚠️  Inserisci una data valida non antecedente al {one_year_ago.strftime('%d/%m/%Y')}")
        else:
            print("Formato data non valido. Riprova con formato gg/mm/aaaa")


# ============================================================================
# BROWSER SETUP
# ============================================================================

def _check_internet_connection() -> bool:
    """Verifica se c'è connessione internet disponibile"""
    try:
        import requests
        response = requests.get("https://www.google.com", timeout=5)
        return response.status_code == 200
    except:
        return False


def setup_browser():
    """Configura e avvia il browser Chrome con strategie multiple di fallback"""
    _log_section("🚀 Avvio del browser...")

    chrome_options = Options()

    # FORZA la modalità con UI visibile - importante per il debugger
    chrome_options.add_argument("--disable-headless")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-default-apps")

    # Configurazioni di sicurezza e prestazioni
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")

    # Imposta una finestra di dimensioni moderate invece di schermo intero
    chrome_options.add_argument("--window-size=1200,800")
    chrome_options.add_argument("--window-position=100,100")

    # Rimuovo start-maximized per evitare schermo intero
    chrome_options.add_experimental_option("detach", True)

    # Configurazioni per supportare CAPTCHA e login
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.media_stream": 2,
        "profile.default_content_setting_values.geolocation": 2
        }
    chrome_options.add_experimental_option("prefs", prefs)

    # Aggiungi User-Agent realistico per evitare detection
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Disabilita automation flags per sembrare più umano
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Per il debugging: aggiungi log verboso ma meno invasivo
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=1")

    # STRATEGIA 1: Usa ChromeDriver predefinito di sistema (PRIORITÀ MASSIMA - più affidabile)
    _log_step("🔍 Tentativo 1: Uso ChromeDriver predefinito di sistema")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.implicitly_wait(10)
        _log_substep("🎉 Browser avviato con successo usando ChromeDriver predefinito")
        return driver
    except Exception as e:
        _log_substep(f"❌ ChromeDriver predefinito non funziona: {e}")

    # STRATEGIA 2: Cerca ChromeDriver già installato nel sistema
    _log_step("🔍 Tentativo 2: Ricerca ChromeDriver già installato nel sistema")
    system_chromedriver_paths = [
        "chromedriver",  # PATH del sistema (prova prima questo)
        "/opt/homebrew/bin/chromedriver",  # Homebrew Apple Silicon Mac
        "/usr/local/bin/chromedriver",  # Homebrew Intel Mac
        "/usr/bin/chromedriver",  # Sistema Linux/Mac
        ]

    for chromedriver_path in system_chromedriver_paths:
        try:
            import shutil
            # Verifica se il path esiste o è nel PATH
            if chromedriver_path == "chromedriver":
                actual_path = shutil.which("chromedriver")
                if actual_path is None:
                    continue
                _log_substep(f"✅ Trovato ChromeDriver nel PATH: {actual_path}")
            elif not os.path.exists(chromedriver_path):
                continue
            else:
                _log_substep(f"✅ Trovato ChromeDriver in: {chromedriver_path}")

            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.implicitly_wait(10)
            _log_substep("🎉 Browser avviato con successo usando ChromeDriver locale")
            return driver
        except Exception as e:
            _log_substep(f"❌ ChromeDriver {chromedriver_path} non funziona: {e}")
            continue

    # STRATEGIA 3: WebDriverManager come ULTIMA RISORSA (richiede connessione internet)
    has_internet = _check_internet_connection()
    if has_internet:
        _log_step("🌐 Tentativo 3: ChromeDriver non trovato localmente, provo il download automatico")
        _log_substep("⚠️  Questa operazione richiede connessione internet e potrebbe fallire per restrizioni di sistema")
        try:
            # Configura WebDriverManager per cache locale
            service = Service(ChromeDriverManager(cache_valid_range=7).install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.implicitly_wait(10)
            _log_substep("🎉 Browser avviato con successo tramite download automatico")
            _log_detail("💡 Suggerimento: Per evitare download futuri, installa ChromeDriver localmente")
            return driver
        except Exception as e:
            _log_substep(f"❌ Download automatico fallito: {e}")
    else:
        _log_step("🚫 Connessione internet non disponibile - salto il download automatico")

    # Se tutti i tentativi falliscono, fornisci istruzioni dettagliate per l'installazione
    error_message = """🚨 Impossibile avviare Chrome - ChromeDriver non trovato

🔧 SOLUZIONI RACCOMANDATE:

📋 REQUISITI:
   • Google Chrome deve essere installato e aggiornato
   • ChromeDriver deve essere compatibile con la versione di Chrome

🛠️  INSTALLAZIONE ChromeDriver:

   macOS (raccomandato):
   ▶️  brew install chromedriver
   ▶️  xattr -d com.apple.quarantine $(which chromedriver)

   macOS alternativo:
   ▶️  Scarica da https://chromedriver.chromium.org
   ▶️  Estrai in /usr/local/bin/ e rendi eseguibile

   Linux Ubuntu/Debian:
   ▶️  sudo apt-get install chromium-chromedriver

   Linux altre distro:
   ▶️  Scarica da https://chromedriver.chromium.org
   ▶️  Estrai in /usr/bin/ e rendi eseguibile

   Windows:
   ▶️  Scarica da https://chromedriver.chromium.org
   ▶️  Aggiungi al PATH di sistema

🔍 VERIFICA INSTALLAZIONE:
   ▶️  Apri terminale e digita: chromedriver --version

⚠️  POSSIBILI PROBLEMI:
   • Versione Chrome non compatibile → Aggiorna Chrome
   • Permessi insufficienti → Usa sudo per installazione
   • Firewall aziendale → Installazione manuale richiesta
   • macOS Gatekeeper → Esegui: xattr -d com.apple.quarantine /path/to/chromedriver

💡 DOPO L'INSTALLAZIONE:
   Il plugin funzionerà offline senza bisogno di connessione internet."""

    _handle_fatal_error(None, error_message, Exception("Tutte le strategie di avvio del browser sono fallite"))


# ============================================================================
# WEB NAVIGATION FUNCTIONS
# ============================================================================

def _wait_page_load(driver, href_click_url, destination_url, timeout: int = 120):
    """Attende che l'utente completi le azioni necessarie partendo dall' href_click_url per arrivare al destination_url, entro un timeout"""
    driver.execute_script(f"window.location.href = '{href_click_url}';")
    print(f"Link cliccato, in attesa di giungere a '{destination_url}' entro il timeout di {timeout}s ...")
    # Attendi che la pagina navighi all'URL target
    try:
        WebDriverWait(driver, timeout).until(lambda driver: driver.current_url == destination_url)
    except Exception as e:
        raise TimeoutError(f"Timeout: non sono riuscito a navigare a '{destination_url}' automaticamente.") from e


def navigate_to_login(driver):
    """Naviga alla pagina di login e clicca sul pulsante evidenziato"""
    _log_section("🔐 Navigazione alla pagina di login")

    login_url = "https://www.day.it/login-utilizzatori#:~:text=Accesso%20piattaforma%20unica%20per%20Buoni%20Pasto%2C%20Piattaforma%20Welfare%20e%20Buoni%20Acquisto%20Cadhoc%C2%A0"
    driver.get(login_url)

    # Attendi e clicca sul link specifico per l'accesso alla piattaforma
    try:
        # Cerca il link specifico per l'accesso alla piattaforma utilizzatori
        login_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='https://utilizzatori.day.it/day/it/login']")))

        # Forza la navigazione nello stesso tab usando JavaScript
        target_url = login_link.get_attribute('href')
        try:
            _log_step("Reindirizzamento automatico alla home page")
            _wait_page_load(driver, target_url, "https://utilizzatori.day.it/day/it/home", timeout=120)
        except Exception as e:
            _handle_fatal_error(driver, "Timeout nel login automatico - il sito potrebbe essere lento o non raggiungibile", e)
        _log_substep(f"✅ Navigazione completata: {driver.current_url}")
        return

    except Exception as e:
        _log_step("⚠️  Pulsante di login non trovato automaticamente. Procedi manualmente.")
        raise ReferenceError("Pulsante di login non trovato") from e


def wait_for_manual_login(driver):
    """Attende che l'utente effettui il login manualmente"""
    print("\n" + "=" * 60)
    print("EFFETTUA IL LOGIN MANUALMENTE NEL BROWSER")
    print("Una volta loggato, premi INVIO qui per continuare...")
    print("=" * 60)

    input("Premi INVIO quando hai completato il login: ")

    if driver.current_url != "https://utilizzatori.day.it/day/it/home":
        _handle_fatal_error(driver, f"Login non completato correttamente - URL attuale: {driver.current_url}. Assicurati di essere sulla home page prima di premere INVIO")


def navigate_to_movements(driver):
    """Naviga alla pagina dei movimenti"""
    _log_section("📊 Navigazione alla pagina dei movimenti")

    movements_url = "https://utilizzatori.day.it/day/it/pausa-pranzo/monitora/movimenti"
    driver.get(movements_url)

    # Attendi che la pagina si carichi completamente
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        _log_step("✅ Pagina caricata correttamente")
    except Exception as e:
        _handle_fatal_error(driver, "La pagina dei movimenti non si è caricata correttamente", e)

    # Gestisci automaticamente il banner dei cookie
    _handle_cookie_banner(driver)


def set_date_filter(driver, start_date: str, end_date: str = None):
    """Imposta il filtro data e avvia la ricerca"""
    _log_section(f"🗓️  Impostazione filtro data: da {start_date} a {end_date if end_date else 'oggi'}")

    try:
        # Campo data di inizio - selettore specifico per dataDa
        _log_step("Ricerca e compilazione campo data di inizio")
        start_date_field = None
        try:
            start_date_field = driver.find_element(By.ID, "dataDa")
            _log_substep("Campo data di inizio trovato con ID 'dataDa'")
        except:
            try:
                start_date_field = driver.find_element(By.CSS_SELECTOR, "input[name='dataDa']")
                _log_substep("Campo data di inizio trovato con name 'dataDa'")
            except:
                _log_substep("❌ Campo data di inizio non trovato")

        if start_date_field:
            start_date_field.clear()
            start_date_field.send_keys(start_date)
            _log_substep(f"✅ Data di inizio impostata: {start_date}")
        else:
            _handle_fatal_error(driver, "Campo data di inizio non trovato!")

        # Campo data di fine - selettore specifico per dataA (opzionale)
        if end_date:
            _log_step("Ricerca e compilazione campo data di fine")
            end_date_field = None
            try:
                end_date_field = driver.find_element(By.ID, "dataA")
                _log_substep("Campo data di fine trovato con ID 'dataA'")
            except:
                try:
                    end_date_field = driver.find_element(By.CSS_SELECTOR, "input[name='dataA']")
                    _log_substep("Campo data di fine trovato con name 'dataA'")
                except:
                    _log_substep("Campo data di fine non trovato")

            if end_date_field:
                end_date_field.clear()
                end_date_field.send_keys(end_date)
                _log_substep(f"✅ Data di fine impostata: {end_date}")
            else:
                _log_substep("⚠️  Campo data di fine non trovato, ma continuo...")
        else:
            _log_step("Data di fine non specificata, verrà usata la data odierna automaticamente")

        # Pulsante di ricerca - selettore specifico per btnNext
        _log_step("Ricerca e click del pulsante CERCA")
        search_button = None
        try:
            search_button = driver.find_element(By.ID, "btnNext")
            _log_substep("Pulsante di ricerca trovato con ID 'btnNext'")
        except:
            try:
                search_button = driver.find_element(By.CSS_SELECTOR, "input[name='btnNext']")
                _log_substep("Pulsante di ricerca trovato con name 'btnNext'")
            except:
                try:
                    search_button = driver.find_element(By.CSS_SELECTOR, "input[value='CERCA']")
                    _log_substep("Pulsante di ricerca trovato con value 'CERCA'")
                except:
                    _log_substep("❌ Pulsante di ricerca non trovato")

        if search_button:
            search_button.click()
            _log_substep("✅ Pulsante CERCA cliccato")

            # Attendi che la pagina si ricarichi e i risultati appaiano
            _log_substep("⏳ Attendo il caricamento dei risultati...")

            # Verifica che la tabella dei risultati sia presente
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".wrap-table table.table tbody")))
                _log_substep("✅ Risultati caricati correttamente")
                return
            except:
                _handle_fatal_error(driver, "I risultati non sono stati caricati correttamente dopo la ricerca")
        else:
            _handle_fatal_error(driver, "Pulsante di ricerca non trovato - impossibile procedere")

    except Exception as e:
        _handle_fatal_error(driver, "Errore nell'impostazione dei filtri", e)


def _handle_cookie_banner(driver):
    """Gestisce il banner dei cookie cliccando su 'Usa solo i cookie necessari'"""
    try:
        _log_step("🍪 Controllo presenza banner cookie")

        # Cerca il pulsante "Usa solo i cookie necessari"
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline"))
            )

        _log_substep("Banner cookie trovato, clicco su 'Usa solo i cookie necessari'")
        cookie_button.click()

        # Attendi che il banner scompaia
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "CybotCookiebotDialogBodyButtonDecline"))
            )

        _log_substep("✅ Banner cookie chiuso con successo")
        return True

    except Exception as e:
        _log_substep("Banner cookie non trovato o già gestito")
        return False


# ============================================================================
# SCRAPING FUNCTIONS
# ============================================================================

def scrape_all_pages(driver) -> List[Dict[str, Any]]:
    """Esegue lo scraping di tutte le pagine dei risultati"""
    _log_section("📄 Inizio scraping delle pagine")

    all_transactions = []
    page_number = 1

    while True:
        _log_step(f"Scraping pagina {page_number}")

        # Estrai i dati della tabella della pagina corrente
        table_html = _extract_table_html(driver)
        if table_html:
            # Analizza l'HTML e estrae le transazioni strutturate
            page_transactions = _parse_transactions_from_html(table_html)

            # Aggiungi informazioni sulla pagina di origine
            for transaction in page_transactions:
                transaction['pagina_origine'] = page_number

            all_transactions.extend(page_transactions)
            _log_substep(f"✅ Estratte {len(page_transactions)} transazioni dalla pagina {page_number}")

        # Controlla se ci sono altre pagine
        if not _go_to_next_page(driver):
            break

        page_number += 1

    _log_section(f"✅ Scraping completato. Totale transazioni estratte: {len(all_transactions)} da {page_number} pagine")

    # Stampa un riepilogo delle transazioni per debug
    if all_transactions:
        _log_section("📊 RIEPILOGO TRANSAZIONI")
        credits = [t for t in all_transactions if t['tipo_operazione'] == 'credit']
        usages = [t for t in all_transactions if t['tipo_operazione'] == 'usage']

        _log_step(f"Accrediti: {len(credits)}")
        _log_step(f"Utilizzi: {len(usages)}")

        total_credits = sum(t['valore'] for t in credits)
        total_usage = sum(abs(t['valore']) for t in usages)

        _log_step(f"Totale accreditato: +{total_credits:.2f}€")
        _log_step(f"Totale utilizzato: -{total_usage:.2f}€")

    return all_transactions


def _extract_table_html(driver) -> str:
    """Estrae l'HTML della tabella dei movimenti"""
    try:
        # Selettore specifico per la tabella UpDay basato sull'HTML fornito
        table_selector = ".wrap-table .table-responsive table.table"

        try:
            table = driver.find_element(By.CSS_SELECTOR, table_selector)
            html_content = table.get_attribute('outerHTML')
            return html_content
        except:
            print("Tabella principale non trovata, provo con selettori alternativi...")

            # Selettori alternativi specifici per UpDay
            alternative_selectors = [
                ".wrap-table table",
                "table.table",
                ".table-responsive table",
                "div.wrap-table > div.table-responsive > table"
                ]

            for selector in alternative_selectors:
                try:
                    table = driver.find_element(By.CSS_SELECTOR, selector)
                    html_content = table.get_attribute('outerHTML')
                    print(f"Tabella trovata con selettore alternativo '{selector}': {len(html_content)} caratteri")
                    return html_content
                except:
                    continue

            print("ERRORE: Nessuna tabella trovata con i selettori UpDay")

            # Debug: mostra tutte le tabelle presenti nella pagina
            try:
                all_tables = driver.find_elements(By.TAG_NAME, "table")
                print(f"DEBUG: Trovate {len(all_tables)} tabelle nella pagina")
                for i, table in enumerate(all_tables):
                    class_attr = table.get_attribute('class') or 'no-class'
                    print(f"  Tabella {i + 1}: class='{class_attr}'")

                # Se c'è almeno una tabella, usa la prima
                if all_tables:
                    html_content = all_tables[0].get_attribute('outerHTML')
                    print(f"Usando la prima tabella trovata: {len(html_content)} caratteri")
                    return html_content
            except Exception as debug_e:
                print(f"Errore nel debug delle tabelle: {debug_e}")

            return ""

    except Exception as e:
        print(f"Errore nell'estrazione della tabella: {e}")
        return ""


def _go_to_next_page(driver) -> bool:
    """Controlla se esiste una pagina successiva e ci naviga"""
    try:
        # Salva il numero della pagina corrente prima di fare qualsiasi operazione
        current_page_number = None
        try:
            current_active = driver.find_element(By.CSS_SELECTOR, "#pg_page li.item.active a")
            current_page_number = current_active.text.strip()
            _log_substep(f"Pagina corrente: {current_page_number}")
        except:
            _log_substep("⚠️  Non riesco a determinare la pagina corrente")

        # Cerca la paginazione con id pg_page
        pagination = driver.find_element(By.ID, "pg_page")

        # Trova tutti gli elementi li con classe item
        items = pagination.find_elements(By.CSS_SELECTOR, "li.item")

        if not items:
            _log_substep("Nessun elemento di paginazione trovato")
            return False

        # Trova l'elemento attivo
        active_item = None
        active_index = -1

        for i, item in enumerate(items):
            if "active" in item.get_attribute("class"):
                active_item = item
                active_index = i
                break

        if active_item is None:
            _log_substep("⚠️  Elemento di paginazione attivo non trovato")
            return False

        # Controlla se esiste un elemento successivo
        if active_index + 1 < len(items):
            next_item = items[active_index + 1]

            # Cerca un link nell'elemento successivo
            try:
                next_link = next_item.find_element(By.TAG_NAME, "a")
                next_page_number_text = next_link.text.strip()
                next_page_url = next_link.get_attribute('href')

                _log_substep(f"Navigazione alla pagina successiva: {next_page_number_text}")

                # Strategia 1: Prova con il click normale
                try:
                    next_link.click()
                except Exception as click_e:
                    _log_detail(f"Click normale fallito: {click_e}")
                    # Strategia 2: Usa JavaScript per il click
                    try:
                        driver.execute_script("arguments[0].click();", next_link)
                        _log_detail("Click JavaScript riuscito")
                    except Exception as js_e:
                        _log_detail(f"Click JavaScript fallito: {js_e}")
                        # Strategia 3: Naviga direttamente con l'URL
                        if next_page_url:
                            _log_detail(f"Navigazione diretta all'URL: {next_page_url}")
                            driver.get(next_page_url)
                        else:
                            _log_detail("❌ Tutte le strategie di click fallite")
                            return False

                # Attendi che la pagina si carichi con una strategia più robusta
                _log_substep("⏳ Attendo il caricamento della pagina successiva...")

                # Strategia di attesa più robusta
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        # Aspetta che la tabella sia presente (indica che la pagina è caricata)
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".wrap-table table.table tbody"))
                            )

                        # Verifica che la paginazione sia nuovamente disponibile
                        WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#pg_page li.item.active"))
                            )

                        # Verifica che la pagina sia effettivamente cambiata
                        try:
                            new_active = driver.find_element(By.CSS_SELECTOR, "#pg_page li.item.active a")
                            new_page_number = new_active.text.strip()

                            if new_page_number == next_page_number_text:
                                _log_substep(f"✅ Navigazione riuscita alla pagina {new_page_number}")
                                return True
                            elif new_page_number != current_page_number:
                                _log_substep(f"✅ Pagina cambiata da {current_page_number} a {new_page_number}")
                                return True
                            else:
                                _log_detail(f"⚠️  Tentativo {attempt + 1}: Pagina non cambiata, riprovo...")
                                if attempt < max_attempts - 1:
                                    import time
                                    time.sleep(1)
                                    continue

                        except Exception as verify_e:
                            _log_detail(f"⚠️  Tentativo {attempt + 1}: Errore nella verifica: {verify_e}")
                            if attempt < max_attempts - 1:
                                import time
                                time.sleep(1)
                                continue

                        break

                    except Exception as wait_e:
                        _log_detail(f"⚠️  Tentativo {attempt + 1}: Timeout nell'attesa: {wait_e}")
                        if attempt < max_attempts - 1:
                            import time
                            time.sleep(2)
                            continue
                        else:
                            _log_detail("❌ Timeout definitivo nel caricamento della pagina")
                            return False

                return True

            except Exception as e:
                _log_substep(f"⚠️  Errore nella ricerca del link successivo: {e}")
                return False
        else:
            _log_substep("✅ Nessuna pagina successiva disponibile (fine paginazione)")
            return False

    except Exception as e:
        _log_substep(f"❌ Errore generale nella navigazione alla pagina successiva: {e}")
        return False


def _parse_transactions_from_html(html_content: str) -> List[Dict[str, Any]]:
    """
    Analizza l'HTML della tabella e estrae le informazioni delle transazioni

    Args:
        html_content: Stringa HTML della tabella

    Returns:
        Lista di dizionari con i dati delle transazioni strutturate
    """
    transactions = []

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Trova tutte le righe delle transazioni (wrap-collapse-tr)
        transaction_rows = soup.find_all('tr', class_='wrap-collapse-tr')

        for row in transaction_rows:
            try:
                # Trova la tabella interna (table-collapse) che contiene i dati della transazione
                inner_table = row.find('table', class_='table-collapse')
                if not inner_table:
                    continue

                # Trova le righe della tabella interna
                inner_rows = inner_table.find('tbody').find_all('tr')
                if len(inner_rows) < 2:
                    continue

                # Prima riga contiene i dati principali
                main_row = inner_rows[0]
                main_cells = main_row.find_all('td')

                if len(main_cells) < 4:
                    continue

                # Estrazione dati principali
                datetime_text = main_cells[0].get_text(strip=True)
                description = main_cells[1].get_text(strip=True)
                vouchers_count = main_cells[2].get_text(strip=True)
                amount_text = main_cells[3].get_text(strip=True)

                # Parsing data e ora
                date_part = None
                time_part = None
                try:
                    if ' ' in datetime_text:
                        date_part, time_part = datetime_text.split(' ', 1)
                    else:
                        date_part = datetime_text
                        time_part = "00:00"
                except:
                    date_part = datetime_text
                    time_part = "00:00"

                # Parsing dell'importo (rimuove € e converte in float)
                amount_value = None
                try:
                    # Rimuovi €, spazi e converte virgola in punto
                    clean_amount = amount_text.replace('€', '').replace(' ', '').replace(',', '.')
                    # Gestisce segno + o -
                    if clean_amount.startswith('+'):
                        amount_value = float(clean_amount[1:])
                    elif clean_amount.startswith('-'):
                        amount_value = -float(clean_amount[1:])
                    else:
                        amount_value = float(clean_amount)
                except:
                    amount_value = 0.0

                # Parsing numero buoni
                vouchers_num = None
                try:
                    vouchers_num = int(vouchers_count)
                except:
                    vouchers_num = 0

                # Seconda riga contiene i dettagli (collapse)
                details_row = inner_rows[1] if len(inner_rows) > 1 else None
                merchant_name = ""
                merchant_location = ""
                reference_code = ""

                if details_row:
                    collapse_div = details_row.find('div', class_='collapse')
                    if collapse_div:
                        # Estrai nome esercente
                        name_span = collapse_div.find('span', class_='name')
                        if name_span:
                            merchant_name = name_span.get_text(strip=True)

                        # Estrai location
                        location_span = collapse_div.find('span', class_='location')
                        if location_span:
                            merchant_location = location_span.get_text(strip=True)

                        # Estrai codice ricarica (per accrediti)
                        strong_tags = collapse_div.find_all('strong')
                        for strong in strong_tags:
                            if 'Ricarica' in strong.get_text():
                                # Il codice dovrebbe essere nel testo dopo il strong
                                parent_text = strong.parent.get_text()
                                if ':' in parent_text:
                                    reference_code = parent_text.split(':', 1)[1].strip()

                # Determina il tipo di operazione
                operation_type = "unknown"
                if "Utilizzo" in description:
                    operation_type = "usage"
                elif "Accredito" in description:
                    operation_type = "credit"

                # Crea il record della transazione
                transaction = {
                    'data': date_part,
                    'ora': time_part,
                    'numero_buoni': vouchers_num,
                    'valore': amount_value,
                    'descrizione_operazione': description,
                    'tipo_operazione': operation_type,
                    'luogo_utilizzo': merchant_name,
                    'indirizzo': merchant_location,
                    'codice_riferimento': reference_code,
                    'datetime_originale': datetime_text,
                    'importo_originale': amount_text
                    }

                transactions.append(transaction)

            except Exception as e:
                print(f"Errore nel parsing di una transazione: {e}")
                continue

        print(f"Estratte {len(transactions)} transazioni dall'HTML")
        return transactions

    except Exception as e:
        print(f"Errore nel parsing dell'HTML: {e}")
        return []


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def sanitize_filename(filename: str) -> str:
    """Sanitizza il nome del file rimuovendo caratteri non validi"""
    # Rimuovi l'estensione se presente
    if '.' in filename:
        filename = filename.rsplit('.', 1)[0]
    # Mantieni solo caratteri alfanumerici, spazi, trattini e slash
    filename = re.sub(r'[^\w\s\-/]', '', filename)
    # Sostituisci spazi con underscore
    filename = filename.replace(' ', '_')
    # Se il nome è vuoto dopo la sanitizzazione, usa la data odierna
    if not filename.strip():
        filename = date.today().strftime("%Y-%m-%d_upday")
    # Aggiungi sempre l'estensione .csv
    return f"{filename}.csv"


def save_transactions_to_csv(transactions: List[Dict[str, Any]], filename: str) -> bool:
    """
    Salva le transazioni in un file CSV

    Args:
        transactions: Lista delle transazioni estratte
        filename: Nome del file CSV dove salvare

    Returns:
        True se salvato con successo, False altrimenti
    """
    try:
        if not transactions:
            print("⚠️  Nessuna transazione da salvare")
            return False

        # Definisci le colonne del CSV nell'ordine desiderato
        fieldnames = [
            'data',
            'ora',
            'descrizione_operazione',
            'tipo_operazione',
            'numero_buoni',
            'valore',
            'luogo_utilizzo',
            'indirizzo',
            'codice_riferimento',
            'pagina_origine'
            ]

        # Crea la directory se non esiste
        directory = os.path.dirname(filename) if os.path.dirname(filename) else '.'
        os.makedirs(directory, exist_ok=True)

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Scrivi l'header
            writer.writeheader()

            # Scrivi i dati delle transazioni
            for transaction in transactions:
                # Filtra solo i campi che vogliamo nel CSV
                filtered_transaction = {key: transaction.get(key, '') for key in fieldnames}
                writer.writerow(filtered_transaction)

        print(f"✅ File CSV salvato con successo: {filename}")
        print(f"📊 Transazioni salvate: {len(transactions)}")

        # Mostra statistiche del file salvato
        file_size = os.path.getsize(filename)
        print(f"📁 Dimensione file: {file_size} bytes")

        return True

    except Exception as e:
        print(f"❌ Errore nel salvataggio del file CSV: {e}")
        return False


# ============================================================================
# ERROR HANDLING
# ============================================================================

def _handle_fatal_error(driver, error_message: str, exception: Exception = None):
    """
    Gestisce errori fatali chiudendo tutto pulitamente e fornendo feedback

    Args:
        driver: Il driver Selenium da chiudere
        error_message: Messaggio di errore da mostrare all'utente
        exception: L'eccezione originale (opzionale)
    """
    print("\n" + "=" * 60)
    print("❌ ERRORE FATALE - OPERAZIONE INTERROTTA")
    print("=" * 60)
    print(f"PROBLEMA: {error_message}")

    if exception:
        print(f"DETTAGLI TECNICI: {str(exception)}")

    print("\nIl programma si arresterà per evitare ulteriori problemi.")
    print("=" * 60)

    # Chiudi il browser se presente
    if driver:
        try:
            print("Chiusura del browser...")
            driver.quit()
        except:
            print("Browser già chiuso o non disponibile")

    # Termina l'esecuzione
    exit(1)


# ============================================================================
# LOGGING UTILITIES
# ============================================================================

_log_indent_level = 0


def _log(message: str, level: int = 0):
    """
    Log strutturato con indentazione

    Args:
        message: Messaggio da stampare
        level: Livello di indentazione (0=titolo, 1=punto, 2=sottopunto, ecc.)
    """
    global _log_indent_level

    if level == 0:
        # Titolo principale - nessuna indentazione
        print(message)
        _log_indent_level = 0
    else:
        # Punti indentati
        indent = "  " * level
        if level == 1:
            print(f"{indent}• {message}")
        else:
            print(f"{indent}◦ {message}")


def _log_section(title: str):
    """Log di una sezione principale"""
    _log(title, 0)


def _log_step(message: str):
    """Log di un passo principale"""
    _log(message, 1)


def _log_substep(message: str):
    """Log di un sottopasso"""
    _log(message, 2)


def _log_detail(message: str):
    """Log di un dettaglio"""
    _log(message, 3)


# ============================================================================
# MAIN SCRAPING FUNCTION
# ============================================================================

def scrape_upday_data(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Esegue il web scraping del sito UpDay per estrarre le transazioni

    Args:
        start_date: Data di inizio nel formato gg/mm/aaaa
        end_date: Data di fine nel formato gg/mm/aaaa (opzionale)

    Returns:
        Lista di dizionari contenenti i dati delle transazioni
    """
    driver = None
    table_data = []

    try:
        print("=== INIZIO SCRAPING UPDAY ===")

        # Setup browser
        driver = setup_browser()

        # Navigazione e login
        try:
            navigate_to_login(driver)
        except ReferenceError:
            wait_for_manual_login(driver)

        # Start automatic scraping after login
        navigate_to_movements(driver)

        # Impostazione filtri e scraping
        set_date_filter(driver, start_date, end_date)
        table_data = scrape_all_pages(driver)

        print(f"=== SCRAPING COMPLETATO: {len(table_data)} transazioni estratte ===")
        return table_data

    except Exception as e:
        print(f"Errore durante il web scraping: {e}")
        return []
    finally:
        if driver:
            print("Chiusura del browser...")
            driver.quit()


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """
    Punto di ingresso principale per il comando upday-download
    """
    import argparse

    # Configura argparse
    parser = argparse.ArgumentParser(
        prog='upday-download',
        description='Scarica le transazioni dei buoni pasto UpDay dal sito utilizzatori.day.it',
        epilog='Per maggiori informazioni: https://github.com/Alfystar/ofxstatement-upday',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    parser.add_argument('--version', action='version', version='%(prog)s 1.1.0')

    # Aggiungi descrizione dettagliata all'help
    parser.description = """
Scarica le transazioni dei buoni pasto UpDay dal sito utilizzatori.day.it
e le salva in un file CSV.

WORKFLOW IN 2 FASI:

  1️⃣  FASE 1 - Download dati da web:
     $ upday-download
     (Scarica i dati da utilizzatori.day.it e li salva in CSV)

  2️⃣  FASE 2 - Conversione CSV -> OFX:
     $ ofxstatement convert -t upday <file.csv> <output.ofx>
     (Converte il file CSV nel formato OFX per GnuCash e altri software)

ESEMPIO COMPLETO:

  $ upday-download
  Inserisci la data di inizio: 01/09/2024
  Inserisci la data di fine: 30/09/2024
  ...
  📄 File salvato: settembre_2024.csv

  $ ofxstatement convert -t upday settembre_2024.csv settembre.ofx
  ✅ Conversione completata: settembre.ofx

REQUISITI:

  • Google Chrome installato e aggiornato
  • ChromeDriver (installazione automatica o manuale)
  • Connessione internet attiva
  • Account UpDay valido su utilizzatori.day.it

VANTAGGI DEL WORKFLOW IN 2 FASI:

  ✅ Modifiche manuali: Puoi modificare il CSV prima della conversione
  ✅ Riconversioni: Puoi riconvertire lo stesso CSV più volte senza riscaricare
  ✅ Backup: Hai sempre una copia dei dati grezzi in CSV
  ✅ Offline: La fase di conversione funziona anche senza internet
"""

    # Parse degli argomenti (anche se non ce ne sono, questo gestisce -h/--help automaticamente)
    args = parser.parse_args()

    # Avvia il processo di download
    print("=" * 70)
    print("🌐 UPDAY DOWNLOAD - Estrazione dati da utilizzatori.day.it")
    print("=" * 70)
    print()

    # Richiedi la data di inizio all'utente
    start_date = get_date_from_user("inizio")
    end_date = get_date_from_user("fine [se vuoto, usa oggi]", optional=True)
    print(f"Date selezionate: da '{start_date}' a '{end_date if end_date else 'oggi'}'")
    print()

    # Esegui il web scraping
    transactions_data = scrape_upday_data(start_date, end_date)

    if not transactions_data:
        print("❌ Nessuna transazione estratta dal web")
        exit(1)

    # Chiedi il nome del file e sanitizzalo
    raw_filename = input("Inserisci il nome del file csv dove salvare questa estrazione automatica (se vuoto verrà usata la data odierna): ").strip()
    filename = sanitize_filename(raw_filename)
    print(f"Nome file sanitizzato: {filename}")

    # Salva i dati nel file CSV
    if save_transactions_to_csv(transactions_data, filename):
        print(f"\n🎉 Estrazione completata con successo!")
        print(f"📄 File salvato: {filename}")
        print(f"📍 Percorso completo: {os.path.abspath(filename)}")
        print()
        print("💡 Fase successiva - Converti il file in OFX con:")
        print(f"   ofxstatement convert -t upday {filename} output.ofx")
        print("=" * 70)
    else:
        print("❌ Errore nel salvataggio del file")
        exit(1)


if __name__ == "__main__":
    main()
