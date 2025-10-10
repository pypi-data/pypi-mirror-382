# PyPrestaScan 🔍

[![PyPI version](https://badge.fury.io/py/pyprestascan.svg)](https://pypi.org/project/pyprestascan/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/andreapianidev/pyprestascan/pulls)

![PyPrestaScan Screenshot](https://www.andreapiani.com/pyprestascan.png)

**Scanner SEO professionale per PrestaShop con sistema di fix automatici**

PyPrestaScan è uno strumento open-source avanzato per l'analisi SEO completa di siti PrestaShop. Scansiona il tuo e-commerce, identifica problemi SEO critici e genera suggerimenti automatici per risolverli.

📦 **Installazione rapida:** `pip install pyprestascan[gui]`

---

## 👨‍💻 Autore

**Andrea Piani**
Full-Stack Developer & SEO Specialist

🔗 **Link:** [linktr.ee/andreapianidev](http://linktr.ee/andreapianidev)

> **Progetto open-source in continuo miglioramento!** Contributi, feedback e segnalazioni sono sempre benvenuti. 🚀

📋 **Roadmap**: [ROADMAP.md](ROADMAP.md) - Piano sviluppo v1.2.0 → v2.0.0
🤝 **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md) - Guida per contributor

---

## 🎯 Caratteristiche Principali

### 📊 Analisi SEO Completa
- **Crawling intelligente** con supporto sitemap.xml e robots.txt
- **Rilevamento automatico** di prodotti, categorie, CMS e filtri faceted
- **Analisi approfondita** di meta tag, title, headings, canonical, hreflang
- **Controllo immagini** con rilevamento ALT mancanti, vuoti o generici
- **Rilevamento duplicati** tramite content hash
- **Scoring SEO** per ogni pagina con severity (CRITICAL, WARNING, INFO)

### 🔧 Sistema di Fix Suggeriti + AI-Powered (v1.1.0 🆕)
- **🤖 Generazione AI intelligente** con DeepSeek, OpenAI GPT o Anthropic Claude
- **Meta description contestuali** generate dall'AI invece di template generici
- **Batch processing**: 20 prodotti in 1 chiamata = -30% token
- **Costi ultra-bassi**: ~$0.02 per 500 prodotti (DeepSeek)
- **Fallback automatico**: se AI fallisce, usa template standard
- **Suggerimenti intelligenti** per:
  - 🎯 Meta description mancanti o non ottimizzate (AI-powered!)
  - 📝 Title troppo corti o troppo lunghi
  - 🖼️ ALT text mancanti per le immagini
  - 🔗 Canonical URL mancanti
  - 📋 H1 multipli o mancanti
  - 🌍 Hreflang mancanti
- **Confidence scoring** (0-100%) per ogni fix suggerito
- **Export SQL** per fix automatizzabili
- **Export CSV** con dettagli completi

#### 💡 AI Fix: Esempio Reale
**Template Standard:**
> "Scarpe Nike Air Zoom - Acquista online su myshop.it"

**AI DeepSeek (v1.1.0):**
> "Scarpe Nike Air Zoom: ammortizzazione reattiva per running. Scopri la collezione 2024 con tecnologia React Foam!"

**Differenza:** Contestuale, benefici evidenziati, CTA naturale. Confidence: 0.95 vs 0.70. Costo: $0.00004 per prodotto.

### 🎨 Interfaccia Grafica Moderna
- **GUI intuitiva** con Qt/PySide6
- **4 Tab principali**:
  1. ⚙️ **Configurazione**: setup URL, limiti, concorrenza
  2. 📊 **Progress & Log**: monitoraggio real-time con log dettagliati
  3. 📈 **Risultati**: statistiche, tabella issues filtrabili
  4. 🔧 **Fix Suggeriti**: visualizza e gestisci i fix automatici
- **Log in tempo reale** durante la scansione
- **Contatori live** (pagine crawlate, issues trovati, immagini senza ALT)
- **Filtri avanzati** per issues e fix
- **Export multipli** (CSV, JSON, HTML, SQL)

### 📈 Report Dettagliati
- **Report HTML interattivo** con grafici e tabelle
- **Export CSV/JSON** per analisi dati
- **Export SQL** per applicazione fix diretta al database
- **Visualizzazione issues** per severity e tipologia
- **Dashboard statistiche** complete

### ⚡ Performance & Scalabilità
- **Crawling asincrono** con concorrenza configurabile (default: 20 worker)
- **Rate limiting** automatico per non sovraccaricare il server
- **Database SQLite** per gestione efficiente dei dati
- **Resume support** per riprendere scansioni interrotte
- **Gestione memoria ottimizzata** per siti con migliaia di pagine

---

## 🚀 Installazione

### Requisiti
- Python 3.8+ (3.12+ raccomandato)
- pip

### 📦 Installazione da PyPI (Consigliata)

```bash
# Installazione base (CLI)
pip install pyprestascan

# Con interfaccia grafica
pip install pyprestascan[gui]

# Avvia la GUI
pyprestascan-gui

# Oppure usa la CLI
pyprestascan scan https://tuosito.com/it/ --max-urls 1000
```

### 🔧 Installazione da sorgenti (Development)

```bash
# Clona il repository
git clone https://github.com/andreapianidev/pyprestascan.git
cd pyprestascan

# Installa in modalità development
pip install -e ".[gui]"

# Avvia l'interfaccia grafica
python -m pyprestascan.gui.main_window

# Oppure usa la CLI
python -m pyprestascan scan https://tuosito.com/it/ --max-urls 1000
```

---

## 📖 Utilizzo

### Interfaccia Grafica (Consigliata)

1. **Avvia la GUI**:
   ```bash
   # Se installato da PyPI
   pyprestascan-gui

   # Oppure se installato da sorgenti
   python -m pyprestascan.gui.main_window
   ```

2. **Configura la scansione**:
   - Inserisci l'URL del tuo sito PrestaShop
   - Imposta il numero massimo di pagine da analizzare
   - Configura concorrenza e altre opzioni avanzate

3. **Avvia la scansione**:
   - Clicca su "▶️ Avvia Scansione"
   - Monitora il progresso in tempo reale nel tab "Progress & Log"

4. **Analizza i risultati**:
   - Vai al tab "📊 Risultati" per vedere gli issues rilevati
   - Filtra per severity (Critical, Warning, Info)
   - Esporta in CSV per analisi dettagliate

5. **Genera e applica fix**:
   - Vai al tab "🔧 Fix Suggeriti"
   - Clicca su "Genera Fix Suggeriti"
   - Visualizza i fix con confidence score
   - Esporta SQL per applicarli direttamente al database PrestaShop

### 🤖 Utilizzo AI Fix (v1.1.0+)

PyPrestaScan può usare **AI generativa** per creare meta description di qualità superiore:

1. **Registrati su un provider AI** (raccomandato: DeepSeek):
   - [DeepSeek](https://platform.deepseek.com) - $5 credito gratuito!
   - [OpenAI](https://platform.openai.com) - GPT-4o-mini
   - [Anthropic](https://console.anthropic.com) - Claude Haiku

2. **Configura in PyPrestaScan**:
   - Vai in tab **Configurazione** → sezione **"AI Fix Avanzati (Opzionale)"**
   - Spunta **"✨ Abilita generazione AI per Fix Suggeriti"**
   - Seleziona provider (es: DeepSeek)
   - Inserisci la tua API key

3. **Genera fix intelligenti**:
   - Esegui scansione normalmente
   - Tab **Fix Suggeriti** → clicca **"Genera Fix Suggeriti"**
   - L'AI creerà meta description **contestuali** invece di template generici
   - Costo stimato: **~$0.02 per 500 prodotti** (DeepSeek)

#### 💰 Confronto Costi AI

| Provider | Costo per 1M token | Costo 500 prodotti | Qualità |
|----------|-------------------|-------------------|---------|
| **DeepSeek** 🏆 | $0.14 | **$0.02** | ⭐⭐⭐⭐⭐ |
| OpenAI GPT-4o-mini | $0.15 | $0.03 | ⭐⭐⭐⭐⭐ |
| Claude Haiku | $0.80 | $0.15 | ⭐⭐⭐⭐⭐ |

**Risparmio vs lavoro manuale**: 8 ore ($240) → 30 secondi ($0.02) = **99.99% di risparmio!**

📖 **Documentazione completa**: Leggi [AI_INTEGRATION.md](AI_INTEGRATION.md) per guide dettagliate, troubleshooting e best practices.

### Command Line Interface (CLI)

```bash
# Scansione base (se installato da PyPI)
pyprestascan scan https://tuosito.com/it/

# Oppure se installato da sorgenti
python -m pyprestascan scan https://tuosito.com/it/

# Scansione con opzioni avanzate
pyprestascan scan https://tuosito.com/it/ \
  --max-urls 5000 \
  --concurrency 30 \
  --timeout 20 \
  --project mio-progetto \
  --export-dir ./reports

# Riprendi scansione interrotta
pyprestascan scan https://tuosito.com/it/ --resume

# Debug mode
python -m pyprestascan scan https://tuosito.com/it/ --debug

# Quiet mode (solo errori)
python -m pyprestascan scan https://tuosito.com/it/ --quiet
```

---

## 📋 Regole SEO Implementate

PyPrestaScan controlla automaticamente oltre **20 regole SEO** PrestaShop-specific:

### 🔴 Critical Issues
- `TITLE_MISSING`: Title tag mancante
- `TITLE_TOO_SHORT`: Title < 10 caratteri
- `TITLE_TOO_LONG`: Title > 60 caratteri
- `META_DESCRIPTION_MISSING`: Meta description mancante
- `H1_MISSING`: Tag H1 mancante
- `H1_MULTIPLE`: Più di un H1 nella pagina
- `CANONICAL_MISSING`: Canonical URL mancante
- `PRODUCT_NO_JSONLD`: Prodotto senza JSON-LD

### 🟡 Warning Issues
- `META_DESCRIPTION_TOO_SHORT`: Description < 50 caratteri
- `META_DESCRIPTION_TOO_LONG`: Description > 160 caratteri
- `IMAGES_MISSING_ALT`: Immagini senza attributo ALT
- `IMAGES_EMPTY_ALT`: Immagini con ALT vuoto
- `CART_INDEXABLE`: Carrello indicizzabile (bad practice)
- `FACETED_NO_CANONICAL`: Filtri faceted senza canonical

### 🔵 Info Issues
- `IMAGES_GENERIC_ALT`: ALT text generico ("image", "photo", etc.)
- `NO_HREFLANG`: Hreflang mancante (siti multilingua)
- `SLOW_TTFB`: Time To First Byte > 1000ms

---

## 🔧 Sistema di Fix Automatici

### Tipi di Fix Supportati

1. **Meta Description Fixer**
   - Genera description ottimizzate 120-160 caratteri
   - Basate su title e tipologia pagina
   - Confidence: 50-90% (dipende dalla qualità del title)

2. **Title Fixer**
   - Ottimizza lunghezza title (10-60 caratteri)
   - Tronca title lunghi preservando il significato
   - Espande title corti aggiungendo brand
   - Confidence: 60-90%

3. **ALT Text Fixer**
   - Suggerisce ALT text basato su contesto pagina
   - Richiede revisione manuale (confidence: 50%)
   - Template-based per prodotti/categorie

4. **Canonical Fixer**
   - Genera canonical URL auto-referenziali
   - Rimuove parametri query non necessari
   - Confidence: 90% (alta affidabilità)

### Come Usare i Fix

1. **Genera fix dopo la scansione**:
   - Tab "Fix Suggeriti" → "Genera Fix Suggeriti"
   - Attendi alcuni secondi per la generazione

2. **Visualizza i fix**:
   - Tabella con tutti i fix ordinati per severity e confidence
   - Filtri per status, tipo, automatizzabili

3. **Dettagli fix**:
   - Clicca sull'icona 👁️ per vedere:
     - Valore attuale vs suggerito
     - Spiegazione del problema
     - Query SQL per applicare il fix

4. **Esporta ed applica**:
   - **Export CSV**: per revisione manuale
   - **Export SQL**: script pronto per l'esecuzione
   - ⚠️ **Fai sempre un backup prima di applicare le query SQL!**

---

## 📁 Struttura File Export

Dopo ogni scansione, PyPrestaScan genera:

```
report/
├── crawl.db              # Database SQLite con tutti i dati
├── report.html           # Report interattivo con grafici
├── pages.csv             # Dettagli di tutte le pagine
├── issues.csv            # Tutti gli issues rilevati
├── images_missing_alt.csv # Immagini con problemi ALT
├── duplicates.csv        # Contenuti duplicati
├── fixes.csv             # Fix suggeriti (dopo generazione)
└── fixes.sql             # Script SQL per fix automatici
```

---

## 🛠️ Configurazione Avanzata

### Parametri CLI Principali

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| `--url` | *richiesto* | URL base del sito da analizzare |
| `--max-urls` | 10000 | Numero massimo di URL da crawlare |
| `--concurrency` | 20 | Richieste HTTP parallele (1-100) |
| `--delay` | 0 | Delay minimo tra richieste (ms) |
| `--timeout` | 15 | Timeout richieste HTTP (secondi) |
| `--depth` | ∞ | Profondità massima crawling |
| `--project` | default | Nome progetto per database |
| `--export-dir` | ./report | Directory output report |

### Filtri URL Avanzati

```bash
# Include solo categorie e prodotti
python run_cli.py scan https://shop.com \
  --include "/category/.+" \
  --include "/.*-p\\d+\\.html"

# Escludi parametri di ordinamento
python run_cli.py scan https://shop.com \
  --exclude "\\?.*orderby=" \
  --exclude "\\?.*selected_filters="
```

---

## 🤝 Contribuire

PyPrestaScan è un progetto **open-source** e in **continuo miglioramento**!

Contributi, segnalazioni bug e feature request sono sempre benvenuti:

1. Fai fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

### Roadmap Futura
- [ ] Integrazione API PrestaShop per applicazione fix automatica
- [ ] Supporto multi-lingua migliorato
- [ ] Analisi performance (Core Web Vitals)
- [ ] Monitoraggio scheduled con notifiche
- [ ] Plugin per PrestaShop back-office
- [ ] AI-powered content suggestions
- [ ] Report PDF professionali
- [ ] Export Excel nativo

---

## 🚨 Risoluzione Problemi

### Problemi Comuni

#### ❌ "Bloccato da robots.txt"
```bash
# Verifica robots.txt manualmente
curl https://tuo-sito.com/robots.txt
```

#### ⚡ Crawling lento
```bash
# Aumenta concorrenza (attenzione al server)
python run_cli.py scan https://sito.com --concurrency 50

# Riduci delay se robots.txt lo permette
python run_cli.py scan https://sito.com --delay 0
```

#### 💾 Errori di memoria
```bash
# Riduci concorrenza per grandi siti
python run_cli.py scan https://sito.com --concurrency 10 --max-urls 20000
```

### Log e Debug

```bash
# Debug completo
python run_cli.py scan https://sito.com --debug

# Log minimal
python run_cli.py scan https://sito.com --quiet
```

---

## 🔒 Sicurezza e Privacy

### Responsabilità

- **Rispetta robots.txt** e ToS dei siti
- **Non fare overload** sui server di destinazione
- **Autentica appropriatamente** per siti privati
- **Proteggi credenziali** in ambienti condivisi

### Rate Limiting Responsabile

```bash
# Per siti piccoli/medi
python run_cli.py scan https://shop.com --delay 100 --concurrency 20

# Per siti grandi/condivisi
python run_cli.py scan https://shop.com --delay 500 --concurrency 10
```

---

## 🤖 Integrazione e API

### Script Python

```python
import asyncio
from pyprestascan.cli import CrawlConfig, CliContext
from pyprestascan.core.crawler import PyPrestaScanner

async def custom_scan():
    config = CrawlConfig(
        base_url="https://myshop.com",
        max_urls=5000,
        concurrency=20
    )

    cli_context = CliContext(debug=False, quiet=False, no_color=False)
    scanner = PyPrestaScanner(config, cli_context)
    return await scanner.run()

# Esegui
asyncio.run(custom_scan())
```

### Export Dati

```python
import pandas as pd

# Carica dati da CSV
pages_df = pd.read_csv('report/pages.csv')
issues_df = pd.read_csv('report/issues.csv')

# Analisi personalizzate
low_score_pages = pages_df[pages_df['score'] < 50]
critical_issues = issues_df[issues_df['severity'] == 'CRITICAL']
```

---

## 📄 Licenza

Questo progetto è distribuito con licenza **MIT** - vedi il file [LICENSE](LICENSE) per i dettagli.

---

## 🙏 Ringraziamenti

- **PrestaShop Community** per la fantastica piattaforma e-commerce
- **PySide6** per il framework GUI
- **httpx** per le richieste HTTP async
- **BeautifulSoup4** per il parsing HTML
- Tutti i **contributori** che aiutano a migliorare il progetto

---

## 📞 Supporto

Per domande, bug o feature request:

- 🐛 **Issues GitHub**: [github.com/andreapianidev/PyPrestaScan/issues](https://github.com/andreapianidev/PyPrestaScan/issues)
- 💬 **Discussioni**: [github.com/andreapianidev/PyPrestaScan/discussions](https://github.com/andreapianidev/PyPrestaScan/discussions)
- 🔗 **Contatto diretto**: [linktr.ee/andreapianidev](http://linktr.ee/andreapianidev)

---

## ⭐ Star History

Se PyPrestaScan ti è stato utile, considera di lasciare una ⭐ su GitHub!

---

<div align="center">

**Made with ❤️ by Andrea Piani for the PrestaShop Community**

🔗 [linktr.ee/andreapianidev](http://linktr.ee/andreapianidev)

*Progetto open-source in continuo miglioramento*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[🏠 Homepage](https://github.com/andreapianidev/PyPrestaScan) •
[📚 Docs](https://github.com/andreapianidev/PyPrestaScan/wiki) •
[🐛 Report Bug](https://github.com/andreapianidev/PyPrestaScan/issues) •
[✨ Request Feature](https://github.com/andreapianidev/PyPrestaScan/issues)

</div>