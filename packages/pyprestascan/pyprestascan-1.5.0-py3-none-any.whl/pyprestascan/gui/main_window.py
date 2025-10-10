"""
Interfaccia grafica principale per PyPrestaScan
"""
import sys
import os
import asyncio
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QTabWidget, QGroupBox, QLabel, QLineEdit, QPushButton,
    QSpinBox, QCheckBox, QComboBox, QTextEdit, QProgressBar, QSlider,
    QFileDialog, QMessageBox, QSplitter, QFrame, QScrollArea, QListWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QStatusBar, QToolBar,
    QMenuBar, QMenu, QDialog, QDialogButtonBox, QFormLayout,
    QInputDialog
)
from PySide6.QtCore import (
    Qt, QThread, QObject, Signal, QTimer, QSettings, QSize, QRect
)
from PySide6.QtGui import (
    QIcon, QFont, QPixmap, QPalette, QColor, QAction, QDesktopServices, QTextCursor
)

from ..cli import CrawlConfig, CliContext
from ..core.crawler import PyPrestaScanner
from ..core.utils import RichLogger
from ..integrations.excel_exporter import ExcelReportExporter
from ..integrations.webhook_client import WebhookClient, ScanNotification, WebhookType
from .themes import ThemeManager
from .i18n import TranslationManager, t


class CrawlerWorker(QObject):
    """Worker thread per eseguire il crawling in background"""

    # Segnali per comunicazione con UI
    progress_updated = Signal(int, int, str)  # current, total, status
    log_message = Signal(str, str)  # level, message
    crawl_finished = Signal(bool, str)  # success, message
    stats_updated = Signal(dict)  # stats dictionary

    def __init__(self, config: CrawlConfig, cli_context: CliContext):
        super().__init__()
        self.config = config
        self.cli_context = cli_context
        self.scanner: Optional[PyPrestaScanner] = None
        self._stop_requested = False
        self._pages_crawled = 0
        self._issues_found = 0
        self._images_no_alt = 0
        self._start_time = None
        self._last_crawled_urls = set()  # Per tracking URL già mostrate

    def run_crawl(self):
        """Esegue il crawling"""
        try:
            # Registra tempo di inizio
            import time
            self._start_time = time.time()

            # Crea nuovo event loop per questo thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Crea scanner
            self.scanner = PyPrestaScanner(self.config, self.cli_context, setup_signals=False)

            # Sostituisci logger con custom logger che emette segnali
            self.scanner.logger = self._create_gui_logger()

            # Avvia monitoring thread
            import threading
            monitor_thread = threading.Thread(target=self._monitor_progress, daemon=True)
            monitor_thread.start()

            # Esegui crawling
            result = loop.run_until_complete(self.scanner.run())

            if result == 0:
                self.crawl_finished.emit(True, "Crawling completato con successo!")
            else:
                self.crawl_finished.emit(False, "Crawling terminato con errori")

        except Exception as e:
            self.crawl_finished.emit(False, f"Errore durante crawling: {str(e)}")

        finally:
            if 'loop' in locals():
                loop.close()

    def _create_gui_logger(self):
        """Crea logger che emette segnali per la GUI"""
        import logging

        class GUILogHandler(logging.Handler):
            def __init__(self, worker):
                super().__init__()
                self.worker = worker

            def emit(self, record):
                try:
                    level = record.levelname
                    message = self.format(record)
                    # Rimuovi codici colore ANSI se presenti
                    import re
                    message = re.sub(r'\x1b\[[0-9;]*m', '', message)
                    self.worker.log_message.emit(level, message)
                except Exception:
                    pass

        # Crea nuovo logger
        logger = RichLogger(
            debug=self.cli_context.debug,
            quiet=self.cli_context.quiet,
            no_color=True  # Disable colors for GUI
        )

        # Aggiungi handler per GUI
        gui_handler = GUILogHandler(self)
        gui_handler.setLevel(logging.INFO)

        # Ottieni logger interno
        if hasattr(logger, '_logger'):
            logger._logger.addHandler(gui_handler)

        return logger

    def _monitor_progress(self):
        """Monitora progress in background thread"""
        import time

        # Attendi che scanner e db siano inizializzati
        for _ in range(50):  # Max 5 secondi
            if self.scanner and self.scanner.db:
                break
            time.sleep(0.1)

        while not self._stop_requested:
            time.sleep(0.5)  # Aggiorna ogni mezzo secondo per più reattività

            # Esci se scanner è terminato
            if self.scanner and not self.scanner.is_running:
                # Ultimo update prima di uscire
                self._do_progress_update()
                break

            if self.scanner and self.scanner.db:
                self._do_progress_update()

    def _do_progress_update(self):
        """Esegue aggiornamento progress leggendo dal DB"""
        try:
            import sqlite3
            import time
            db_path = self.scanner.db.db_path

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Conta pagine crawlate (TUTTE le pagine salvate, non solo con status_code)
                cursor.execute("SELECT COUNT(*) FROM pages")
                pages_crawled = cursor.fetchone()[0]

                # Conta issues
                cursor.execute("SELECT COUNT(*) FROM issues")
                issues_found = cursor.fetchone()[0]

                # Conta immagini senza ALT
                cursor.execute("""
                    SELECT SUM(images_missing_alt + images_empty_alt)
                    FROM pages
                """)
                result = cursor.fetchone()[0]
                images_no_alt = result if result else 0

                # Recupera URL appena crawlate (ultime 5 non ancora mostrate)
                cursor.execute("""
                    SELECT url, status_code
                    FROM pages
                    WHERE status_code IS NOT NULL
                    ORDER BY crawled_at DESC
                    LIMIT 5
                """)
                recent_pages = cursor.fetchall()

            # Log URL crawlate (solo quelle nuove)
            for url, status_code in recent_pages:
                if url not in self._last_crawled_urls:
                    self._last_crawled_urls.add(url)
                    # Emetti log per mostrare URL crawlata
                    status_emoji = "✅" if 200 <= status_code < 300 else "⚠️"
                    self.log_message.emit("INFO", f"{status_emoji} [{status_code}] {url}")

            # Calcola tempo trascorso e ETA
            elapsed_time = 0
            eta_str = "--"
            if self._start_time:
                elapsed_time = time.time() - self._start_time

                # Calcola velocità e tempo stimato
                if pages_crawled > 0 and elapsed_time > 0:
                    pages_per_sec = pages_crawled / elapsed_time
                    remaining_pages = self.config.max_urls - pages_crawled

                    if remaining_pages > 0 and pages_per_sec > 0:
                        eta_seconds = remaining_pages / pages_per_sec
                        eta_minutes = int(eta_seconds / 60)
                        eta_secs = int(eta_seconds % 60)
                        eta_str = f"{eta_minutes}m {eta_secs}s"

            # Emetti segnali sempre (non solo se cambiato)
            self._pages_crawled = pages_crawled
            self.progress_updated.emit(
                pages_crawled,
                self.config.max_urls,
                f"Scansionate {pages_crawled}/{self.config.max_urls} pagine"
            )

            # Aggiorna statistiche (include elapsed_time e eta)
            self.stats_updated.emit({
                'pages_crawled': pages_crawled,
                'pages_failed': 0,
                'total_issues': issues_found,
                'images_no_alt': images_no_alt,
                'elapsed_time': elapsed_time,
                'eta': eta_str
            })

        except Exception as e:
            # Silenzioso - errori progress non critici
            pass

    def stop_crawl(self):
        """Richiede stop del crawling"""
        self._stop_requested = True
        if self.scanner:
            self.scanner.should_stop = True


class ConfigDialog(QDialog):
    """Dialog per configurazione avanzata"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurazione Avanzata")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(15)
        self.timeout_spin.setSuffix(" secondi")
        form_layout.addRow("Timeout HTTP:", self.timeout_spin)
        
        # User Agent
        self.user_agent_edit = QLineEdit()
        self.user_agent_edit.setText("PyPrestaScan/1.0 (+https://github.com/pyprestascan/pyprestascan)")
        form_layout.addRow("User Agent:", self.user_agent_edit)
        
        # Sitemap usage
        self.sitemap_combo = QComboBox()
        self.sitemap_combo.addItems(["auto", "true", "false"])
        form_layout.addRow("Usa Sitemap:", self.sitemap_combo)
        
        # Auth
        auth_group = QGroupBox("Autenticazione (opzionale)")
        auth_layout = QFormLayout(auth_group)
        
        self.auth_user_edit = QLineEdit()
        self.auth_pass_edit = QLineEdit()
        self.auth_pass_edit.setEchoMode(QLineEdit.Password)
        
        auth_layout.addRow("Username:", self.auth_user_edit)
        auth_layout.addRow("Password:", self.auth_pass_edit)
        
        # Filtri URL
        filters_group = QGroupBox("Filtri URL")
        filters_layout = QVBoxLayout(filters_group)
        
        self.include_patterns_edit = QTextEdit()
        self.include_patterns_edit.setMaximumHeight(80)
        self.include_patterns_edit.setPlaceholderText("Pattern regex per includere URL (uno per riga)\nEs: /category/.*")
        
        self.exclude_patterns_edit = QTextEdit()
        self.exclude_patterns_edit.setMaximumHeight(80)
        self.exclude_patterns_edit.setPlaceholderText("Pattern regex per escludere URL (uno per riga)\nEs: \\?.*sort=")
        
        filters_layout.addWidget(QLabel("Includi pattern:"))
        filters_layout.addWidget(self.include_patterns_edit)
        filters_layout.addWidget(QLabel("Escludi pattern:"))
        filters_layout.addWidget(self.exclude_patterns_edit)
        
        # Aggiungi tutto al layout principale
        layout.addLayout(form_layout)
        layout.addWidget(auth_group)
        layout.addWidget(filters_group)
        
        # Bottoni
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_config_updates(self) -> Dict[str, Any]:
        """Restituisce aggiornamenti configurazione"""
        config_updates = {
            'timeout': self.timeout_spin.value(),
            'user_agent': self.user_agent_edit.text().strip(),
            'sitemap': self.sitemap_combo.currentText(),
        }
        
        # Auth se presente
        if self.auth_user_edit.text().strip():
            config_updates['auth_user'] = self.auth_user_edit.text().strip()
            config_updates['auth_pass'] = self.auth_pass_edit.text().strip()
        
        # Pattern filtri
        include_text = self.include_patterns_edit.toPlainText().strip()
        if include_text:
            config_updates['include_patterns'] = [
                line.strip() for line in include_text.split('\n') 
                if line.strip()
            ]
        
        exclude_text = self.exclude_patterns_edit.toPlainText().strip()
        if exclude_text:
            config_updates['exclude_patterns'] = [
                line.strip() for line in exclude_text.split('\n') 
                if line.strip()
            ]
        
        return config_updates


class MainWindow(QMainWindow):
    """Finestra principale PyPrestaScan GUI"""

    def __init__(self, app: QApplication):
        super().__init__()

        # Translation Manager (i18n) - inizializza PRIMA
        self.translation_manager = TranslationManager()

        self.setWindowTitle(self.translation_manager.t("app_title"))
        self.setMinimumSize(900, 700)

        # Theme Manager
        self.app = app
        self.theme_manager = ThemeManager(app)

        # Settings
        self.settings = QSettings("PyPrestaScan", "PyPrestaScanGUI")

        # Worker thread
        self.crawler_thread: Optional[QThread] = None
        self.crawler_worker: Optional[CrawlerWorker] = None

        # Stato applicazione
        self.is_crawling = False
        self.last_export_dir: Optional[Path] = None
        self.all_issues_data = []  # Dati completi per filtraggio
        self.current_project_name: Optional[str] = None  # Nome progetto corrente per database

        # Setup UI
        self._setup_ui()
        self._setup_connections()
        self._load_settings()

        # Applica tema salvato o auto-rilevato
        self.theme_manager.apply_theme(self.theme_manager.get_current_theme())

        # Timer per aggiornamenti
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui_state)
        self.update_timer.start(1000)  # Aggiorna ogni secondo
    
    def _setup_ui(self):
        """Configura interfaccia utente"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QVBoxLayout(central_widget)
        
        # Header con titolo bello
        self._create_header(main_layout)
        
        # Toolbar
        self._create_toolbar()
        
        # Menu bar
        self._create_menu_bar()
        
        # Tab widget principale
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Tab: Configurazione
        self._create_config_tab()
        
        # Tab: Progress & Log
        self._create_progress_tab()
        
        # Tab: Risultati
        self._create_results_tab()

        # Tab: Fixes
        self._create_fixes_tab()

        # Tab: Aiuto
        self._create_help_tab()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto per iniziare analisi SEO")
    
    def _create_header(self, main_layout):
        """Crea header con titolo bello e sfondo blu"""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:0.5 #1976D2, stop:1 #0D47A1);
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Icona
        icon_label = QLabel("🔍")
        icon_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                background: none;
                margin: 0;
            }
        """)
        header_layout.addWidget(icon_label)
        
        # Titolo principale
        title_label = QLabel("PyPrestaScan")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                background: none;
                margin: 0;
                padding-left: 10px;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Sottotitolo
        subtitle_label = QLabel("Analisi SEO PrestaShop")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #E3F2FD;
                font-size: 14px;
                font-weight: normal;
                background: none;
                margin: 0;
                padding-left: 15px;
            }
        """)
        header_layout.addWidget(subtitle_label)
        
        # Spazio elastico
        header_layout.addStretch()
        
        # Badge versione
        version_label = QLabel("v1.5.0")
        version_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                background: rgba(255,255,255,0.2);
                border-radius: 12px;
                padding: 4px 12px;
                margin: 0;
            }
        """)
        header_layout.addWidget(version_label)

        # Toggle Dark/Light mode
        self.theme_toggle_btn = QPushButton(self.theme_manager.get_icon_for_theme())
        self.theme_toggle_btn.setFixedSize(40, 40)
        self.theme_toggle_btn.setToolTip("Cambia tema (Light/Dark)")
        self.theme_toggle_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 20px;
                background: rgba(255,255,255,0.2);
                border-radius: 20px;
                margin: 0;
                margin-left: 10px;
                border: none;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.3);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.4);
            }
        """)
        self.theme_toggle_btn.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self.theme_toggle_btn)

        # Language selector
        self.language_combo = QComboBox()
        self.language_combo.setFixedSize(120, 35)
        self.language_combo.setToolTip("Select language / Seleziona lingua")
        available_langs = self.translation_manager.get_available_languages()
        for lang_code, lang_name in available_langs.items():
            self.language_combo.addItem(lang_name, lang_code)
        # Set current language
        current_lang = self.translation_manager.get_current_language()
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_lang:
                self.language_combo.setCurrentIndex(i)
                break
        self.language_combo.currentIndexChanged.connect(self._change_language)
        self.language_combo.setStyleSheet("""
            QComboBox {
                color: white;
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
                margin-left: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QComboBox:hover {
                background: rgba(255,255,255,0.3);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2D2D2D;
                color: white;
                selection-background-color: #667eea;
                border: 1px solid #667eea;
            }
        """)
        header_layout.addWidget(self.language_combo)

        main_layout.addWidget(header_widget)
    
    def _create_toolbar(self):
        """Crea toolbar con pulsanti grandi"""
        toolbar = QToolBar("Azioni Principali")
        toolbar.setIconSize(QSize(32, 32))  # Icone più grandi
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)  # Testo accanto all'icona

        # Imposta dimensioni e stile toolbar con sfondo scuro come il resto dell'app
        toolbar.setStyleSheet("""
            QToolBar {
                spacing: 10px;
                padding: 8px;
                background-color: #3c3c3c;
                border-bottom: 2px solid #2b2b2b;
            }
            QToolButton {
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                margin: 2px;
                color: #ffffff;
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
            }
            QToolButton:hover {
                background-color: #2196F3;
                border: 1px solid #1976D2;
            }
            QToolButton:pressed {
                background-color: #1976D2;
            }
            QToolButton:disabled {
                color: #808080;
                background-color: #3a3a3a;
            }
        """)

        self.addToolBar(toolbar)

        # Nota: i pulsanti Avvia/Ferma sono nel tab Configurazione per UX migliore
        # Qui mettiamo solo azioni secondarie come export, settings, etc.
    
    def _create_menu_bar(self):
        """Crea menu bar"""
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu("File")
        
        # Nuovo progetto
        new_action = QAction("Nuovo Progetto", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_project)
        file_menu.addAction(new_action)
        
        # Apri progetto
        open_action = QAction("Apri Progetto", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Esci
        exit_action = QAction("Esci", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Strumenti
        tools_menu = menubar.addMenu("Strumenti")
        # Configurazione accessibile dal tab dedicato
        
        # Menu Aiuto
        help_menu = menubar.addMenu("Aiuto")
        
        about_action = QAction("Info su PyPrestaScan", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction("Documentazione Online", self)
        docs_action.triggered.connect(self._open_docs)
        help_menu.addAction(docs_action)
    
    def _create_config_tab(self):
        """Crea tab configurazione"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # Scroll area per contenuto
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Gruppo URL Base
        url_group = QGroupBox("🌐 URL di Base")
        url_layout = QGridLayout(url_group)
        
        url_layout.addWidget(QLabel("URL del sito:"), 0, 0)
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://esempio.com")
        url_layout.addWidget(self.url_edit, 0, 1)
        
        # Bottone test URL
        test_url_btn = QPushButton("🔍 Testa URL")
        test_url_btn.clicked.connect(self._test_url)
        url_layout.addWidget(test_url_btn, 0, 2)
        
        # Include sottodomini
        self.subdomains_check = QCheckBox("Includi sottodomini")
        url_layout.addWidget(self.subdomains_check, 1, 0, 1, 2)
        
        # Modalità PrestaShop
        self.prestashop_check = QCheckBox("Modalità PrestaShop (euristiche specifiche)")
        self.prestashop_check.setChecked(True)
        url_layout.addWidget(self.prestashop_check, 2, 0, 1, 2)
        
        scroll_layout.addWidget(url_group)

        # Gruppo Preset Scansione
        preset_group = QGroupBox("🎯 Modalità Scansione")
        preset_layout = QVBoxLayout(preset_group)

        preset_label = QLabel("Seleziona una modalità predefinita o personalizza i parametri sotto:")
        preset_label.setWordWrap(True)
        preset_layout.addWidget(preset_label)

        preset_buttons_layout = QHBoxLayout()

        # Bottone scansione veloce
        self.fast_scan_btn = QPushButton("⚡ Scansione Veloce")
        self.fast_scan_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; }")
        self.fast_scan_btn.setToolTip("500 pagine, 30 worker, delay 100ms - veloce ma sicuro")
        self.fast_scan_btn.clicked.connect(self._apply_fast_preset)
        preset_buttons_layout.addWidget(self.fast_scan_btn)

        # Bottone scansione approfondita
        self.deep_scan_btn = QPushButton("🔍 Scansione Approfondita")
        self.deep_scan_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; font-weight: bold; }")
        self.deep_scan_btn.setToolTip("10000 pagine, 20 worker, delay 200ms - analisi completa e rispettosa")
        self.deep_scan_btn.clicked.connect(self._apply_deep_preset)
        preset_buttons_layout.addWidget(self.deep_scan_btn)

        # Bottone scansione solo ALT immagini
        self.alt_scan_btn = QPushButton("🖼️ Solo ALT Immagini")
        self.alt_scan_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 10px; font-weight: bold; }")
        self.alt_scan_btn.setToolTip("1000 pagine, 25 worker, delay 150ms - focus immagini")
        self.alt_scan_btn.clicked.connect(self._apply_alt_preset)
        preset_buttons_layout.addWidget(self.alt_scan_btn)

        preset_layout.addLayout(preset_buttons_layout)
        scroll_layout.addWidget(preset_group)

        # Gruppo Limiti Crawling
        limits_group = QGroupBox("⚡ Parametri Crawling")
        limits_layout = QGridLayout(limits_group)
        
        # Max URLs
        limits_layout.addWidget(QLabel("Max URL da crawlare:"), 0, 0)
        self.max_urls_spin = QSpinBox()
        self.max_urls_spin.setRange(1, 100000)
        self.max_urls_spin.setValue(10000)
        self.max_urls_spin.setSingleStep(1000)
        limits_layout.addWidget(self.max_urls_spin, 0, 1)
        
        # Concorrenza
        limits_layout.addWidget(QLabel("Richieste parallele:"), 1, 0)
        self.concurrency_spin = QSpinBox()
        self.concurrency_spin.setRange(1, 100)
        self.concurrency_spin.setValue(20)  # Valore sicuro di default
        limits_layout.addWidget(self.concurrency_spin, 1, 1)

        # Delay
        limits_layout.addWidget(QLabel("Delay tra richieste (ms):"), 2, 0)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 5000)
        self.delay_spin.setValue(150)  # Default sicuro: 150ms
        self.delay_spin.setSingleStep(50)
        limits_layout.addWidget(self.delay_spin, 2, 1)
        
        # Profondità
        limits_layout.addWidget(QLabel("Profondità massima:"), 3, 0)
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(0, 20)
        self.depth_spin.setValue(0)  # 0 = unlimited
        self.depth_spin.setSpecialValueText("Illimitata")
        limits_layout.addWidget(self.depth_spin, 3, 1)
        
        scroll_layout.addWidget(limits_group)
        
        # Gruppo Progetto
        project_group = QGroupBox("📁 Gestione Progetto")
        project_layout = QGridLayout(project_group)
        
        project_layout.addWidget(QLabel("Nome progetto:"), 0, 0)
        self.project_edit = QLineEdit()
        # Crea SEMPRE nuovo progetto con timestamp univoco
        self.project_edit.setText(f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        project_layout.addWidget(self.project_edit, 0, 1)
        
        project_layout.addWidget(QLabel("Directory report:"), 1, 0)
        self.export_dir_edit = QLineEdit()
        self.export_dir_edit.setText("./report")
        project_layout.addWidget(self.export_dir_edit, 1, 1)
        
        browse_btn = QPushButton("Sfoglia...")
        browse_btn.clicked.connect(self._browse_export_dir)
        project_layout.addWidget(browse_btn, 1, 2)
        
        # Resume
        self.resume_check = QCheckBox("Riprendi progetto esistente")
        project_layout.addWidget(self.resume_check, 2, 0, 1, 2)
        
        # Include generici
        self.include_generic_check = QCheckBox("Includi ALT generici nel report")
        project_layout.addWidget(self.include_generic_check, 3, 0, 1, 2)
        
        scroll_layout.addWidget(project_group)
        
        # Gruppo Lingue
        lang_group = QGroupBox("🌍 Configurazione Multilingua")
        lang_layout = QVBoxLayout(lang_group)
        
        lang_layout.addWidget(QLabel("Mappatura lingue (formato: it=it,en=en,fr=fr):"))
        self.lang_map_edit = QLineEdit()
        self.lang_map_edit.setPlaceholderText("it=it,en=en,fr=fr")
        lang_layout.addWidget(self.lang_map_edit)
        
        scroll_layout.addWidget(lang_group)

        # Gruppo User Agent
        ua_group = QGroupBox("🕵️ User Agent")
        ua_layout = QVBoxLayout(ua_group)

        ua_layout.addWidget(QLabel("Seleziona User Agent per le richieste HTTP:"))

        self.user_agent_combo = QComboBox()
        self.user_agent_combo.addItem(
            "Chrome Windows (Default)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.user_agent_combo.addItem(
            "Chrome macOS",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.user_agent_combo.addItem(
            "Firefox Windows",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        )
        self.user_agent_combo.addItem(
            "Firefox macOS",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        )
        self.user_agent_combo.addItem(
            "Safari macOS",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        )
        self.user_agent_combo.addItem(
            "Edge Windows",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        )
        self.user_agent_combo.addItem(
            "iPhone Safari",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
        )
        self.user_agent_combo.addItem(
            "Android Chrome",
            "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36"
        )
        self.user_agent_combo.addItem(
            "GoogleBot",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        )
        self.user_agent_combo.addItem(
            "Custom (Personalizzato)",
            ""
        )

        ua_layout.addWidget(self.user_agent_combo)

        # Campo custom user agent (hidden by default)
        self.custom_ua_edit = QLineEdit()
        self.custom_ua_edit.setPlaceholderText("Inserisci User Agent personalizzato...")
        self.custom_ua_edit.setVisible(False)
        ua_layout.addWidget(self.custom_ua_edit)

        # Label info con UA attuale
        self.ua_info_label = QLabel()
        self.ua_info_label.setWordWrap(True)
        self.ua_info_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        ua_layout.addWidget(self.ua_info_label)

        # Connetti cambio selezione
        self.user_agent_combo.currentIndexChanged.connect(self._on_user_agent_changed)
        self._on_user_agent_changed(0)  # Imposta default

        scroll_layout.addWidget(ua_group)

        # Debug options
        debug_group = QGroupBox("🐛 Opzioni Debug")
        debug_layout = QVBoxLayout(debug_group)

        self.debug_check = QCheckBox("Abilita output debug dettagliato")
        self.quiet_check = QCheckBox("Modalità silenziosa (solo errori)")
        self.no_color_check = QCheckBox("Disabilita colori nel log")

        debug_layout.addWidget(self.debug_check)
        debug_layout.addWidget(self.quiet_check)
        debug_layout.addWidget(self.no_color_check)

        scroll_layout.addWidget(debug_group)

        # AI Fix Avanzati (STESSO STILE ALTRE SEZIONI)
        ai_group = QGroupBox("🤖 AI Fix Avanzati (Opzionale)")
        ai_layout = QVBoxLayout(ai_group)

        # Enable AI checkbox
        self.ai_enabled_check = QCheckBox("✨ Abilita generazione AI per Fix Suggeriti")
        ai_layout.addWidget(self.ai_enabled_check)

        # Grid per campi
        ai_grid = QGridLayout()

        # Provider selection
        ai_grid.addWidget(QLabel("Provider AI:"), 0, 0)
        self.ai_provider_combo = QComboBox()
        self.ai_provider_combo.addItem("🏆 DeepSeek (Raccomandato - $0.14/1M)", "deepseek")
        self.ai_provider_combo.addItem("OpenAI GPT-4o-mini ($0.15/1M)", "openai")
        self.ai_provider_combo.addItem("Claude Haiku ($0.80/1M)", "claude")
        self.ai_provider_combo.setEnabled(False)
        ai_grid.addWidget(self.ai_provider_combo, 0, 1)

        # API Key input
        ai_grid.addWidget(QLabel("API Key:"), 1, 0)

        key_container = QHBoxLayout()
        self.ai_api_key_edit = QLineEdit()
        self.ai_api_key_edit.setPlaceholderText("sk-... (inserisci chiave)")
        self.ai_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.ai_api_key_edit.setEnabled(False)
        key_container.addWidget(self.ai_api_key_edit)

        self.ai_show_key_btn = QPushButton("👁️")
        self.ai_show_key_btn.setMaximumWidth(35)
        self.ai_show_key_btn.setEnabled(False)
        self.ai_show_key_btn.clicked.connect(self._toggle_ai_key_visibility)
        key_container.addWidget(self.ai_show_key_btn)

        ai_grid.addLayout(key_container, 1, 1)

        ai_layout.addLayout(ai_grid)

        # Info label (STILE COERENTE)
        info_label = QLabel(
            "💡 <b>AI genera meta description contestuali</b> invece di template generici. "
            "Batch processing (20/chiamata) = risparmio 30% token. "
            "Costo: ~$0.02 per 500 prodotti (DeepSeek). "
            "Registrati: <a href='https://platform.deepseek.com'>DeepSeek</a> ($5 gratis) | "
            "<a href='https://platform.openai.com'>OpenAI</a> | "
            "<a href='https://console.anthropic.com'>Claude</a>"
        )
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)
        info_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 10px;
                border-radius: 4px;
                border-left: 3px solid #667eea;
                margin-top: 5px;
            }
        """)
        ai_layout.addWidget(info_label)

        # Connect checkbox to enable/disable fields
        self.ai_enabled_check.toggled.connect(self._on_ai_enabled_changed)

        scroll_layout.addWidget(ai_group)

        # Finalizza scroll area
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Bottoni azione
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.start_btn = QPushButton(self.translation_manager.t("btn_start_scan"))
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        self.start_btn.clicked.connect(self._start_crawl)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton(self.translation_manager.t("btn_stop_scan"))
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 10px; }")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_crawl)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(config_widget, self.translation_manager.t("tab_config"))
    
    def _create_progress_tab(self):
        """Crea tab progress e log"""
        progress_widget = QWidget()
        layout = QVBoxLayout(progress_widget)
        
        # Progress section
        progress_group = QGroupBox("📊 Avanzamento Scansione")
        progress_layout = QVBoxLayout(progress_group)
        
        # Progress bar principale
        self.main_progress = QProgressBar()
        self.main_progress.setTextVisible(True)
        progress_layout.addWidget(self.main_progress)
        
        # Stats grid
        stats_layout = QGridLayout()
        
        # Labels per statistiche
        self.pages_crawled_label = QLabel("Pagine scansionate: 0")
        self.pages_failed_label = QLabel("Pagine fallite: 0")
        self.issues_found_label = QLabel("Issues trovati: 0")
        self.images_no_alt_label = QLabel("Immagini senza ALT: 0")
        
        stats_layout.addWidget(self.pages_crawled_label, 0, 0)
        stats_layout.addWidget(self.pages_failed_label, 0, 1)
        stats_layout.addWidget(self.issues_found_label, 1, 0)
        stats_layout.addWidget(self.images_no_alt_label, 1, 1)
        
        progress_layout.addLayout(stats_layout)

        # Timer e tempo stimato
        timer_layout = QHBoxLayout()
        self.elapsed_label = QLabel("⏱️ Tempo trascorso: 0m 0s")
        self.eta_label = QLabel("⏳ Tempo stimato: --")
        timer_layout.addWidget(self.elapsed_label)
        timer_layout.addWidget(self.eta_label)
        progress_layout.addLayout(timer_layout)
        
        layout.addWidget(progress_group)
        
        # Log section
        log_group = QGroupBox("📝 Log Attività")
        log_layout = QVBoxLayout(log_group)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Monaco", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        clear_log_btn = QPushButton("🗑️ Pulisci Log")
        clear_log_btn.clicked.connect(self.log_text.clear)
        log_controls.addWidget(clear_log_btn)
        
        save_log_btn = QPushButton("💾 Salva Log")
        save_log_btn.clicked.connect(self._save_log)
        log_controls.addWidget(save_log_btn)
        
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(progress_widget, self.translation_manager.t("tab_progress"))
    
    def _create_results_tab(self):
        """Crea tab risultati - SEMPLIFICATO con solo KPI e Report HTML"""
        results_widget = QWidget()
        layout = QVBoxLayout(results_widget)

        # Messaggio informativo
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                padding: 20px;
                margin: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)

        info_title = QLabel("📊 Risultati Scansione")
        info_title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background: transparent;")
        info_layout.addWidget(info_title)

        info_text = QLabel(
            "Visualizza i risultati completi della scansione nel <b>Report HTML interattivo</b><br>"
            "con grafici, tabelle ordinabili e analisi dettagliate."
        )
        info_text.setStyleSheet("color: #E3F2FD; font-size: 14px; background: transparent;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        layout.addWidget(info_frame)

        # Summary KPI
        summary_group = QGroupBox("📋 Riepilogo Statistiche")
        summary_layout = QGridLayout(summary_group)
        summary_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding: 20px;
            }
        """)

        # KPI labels con stile migliorato
        self.total_pages_label = QLabel("📄 Pagine totali: --")
        self.total_pages_label.setStyleSheet("font-size: 16px; padding: 10px;")

        self.success_rate_label = QLabel("✅ Tasso successo: --%")
        self.success_rate_label.setStyleSheet("font-size: 16px; padding: 10px;")

        self.avg_score_label = QLabel("⭐ Score medio: --")
        self.avg_score_label.setStyleSheet("font-size: 16px; padding: 10px;")

        self.critical_issues_label = QLabel("🔴 Issues critici: --")
        self.critical_issues_label.setStyleSheet("font-size: 16px; padding: 10px;")

        summary_layout.addWidget(self.total_pages_label, 0, 0)
        summary_layout.addWidget(self.success_rate_label, 0, 1)
        summary_layout.addWidget(self.avg_score_label, 1, 0)
        summary_layout.addWidget(self.critical_issues_label, 1, 1)

        layout.addWidget(summary_group)

        # Spacer
        layout.addStretch()

        # Action buttons - GRANDI e VISIBILI
        actions_group = QGroupBox("🎯 Azioni Disponibili")
        actions_layout = QVBoxLayout(actions_group)
        actions_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding: 20px;
            }
        """)

        # Bottone report HTML - PRINCIPALE
        self.view_report_btn = QPushButton(self.translation_manager.t("btn_view_report"))
        self.view_report_btn.setEnabled(False)
        self.view_report_btn.clicked.connect(self._open_report)
        self.view_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #764ba2;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #AAAAAA;
            }
        """)
        actions_layout.addWidget(self.view_report_btn)

        # Bottoni secondari
        secondary_layout = QHBoxLayout()

        self.open_export_dir_btn = QPushButton(self.translation_manager.t("btn_open_folder"))
        self.open_export_dir_btn.setEnabled(False)
        self.open_export_dir_btn.clicked.connect(self._open_export_dir)
        self.open_export_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: #FFFFFF;
                font-size: 14px;
                padding: 15px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #AAAAAA;
            }
        """)
        secondary_layout.addWidget(self.open_export_dir_btn)

        export_csv_btn = QPushButton(self.translation_manager.t("btn_export_csv"))
        export_csv_btn.clicked.connect(self._export_issues_csv)
        export_csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 15px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        secondary_layout.addWidget(export_csv_btn)

        self.export_excel_btn = QPushButton(self.translation_manager.t("btn_export_excel"))
        self.export_excel_btn.setEnabled(False)
        self.export_excel_btn.clicked.connect(self._export_excel)
        self.export_excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: #FFFFFF;
                font-size: 14px;
                padding: 15px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #EE5A5A;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #AAAAAA;
            }
        """)
        secondary_layout.addWidget(self.export_excel_btn)

        actions_layout.addLayout(secondary_layout)

        layout.addWidget(actions_group)

        # Spacer finale
        layout.addStretch()

        self.tab_widget.addTab(results_widget, self.translation_manager.t("tab_results"))

    def _create_fixes_tab(self):
        """Crea tab per gestione fix"""
        fixes_widget = QWidget()
        layout = QVBoxLayout(fixes_widget)

        # Header con pulsanti azione
        actions_layout = QHBoxLayout()

        generate_fixes_btn = QPushButton(self.translation_manager.t("btn_generate_fixes"))
        generate_fixes_btn.setToolTip("Analizza gli issues e genera suggerimenti automatici per risolverli")
        generate_fixes_btn.clicked.connect(self._generate_fixes)
        actions_layout.addWidget(generate_fixes_btn)

        actions_layout.addStretch()

        refresh_fixes_btn = QPushButton("🔄 Aggiorna")
        refresh_fixes_btn.clicked.connect(self._load_fixes)
        actions_layout.addWidget(refresh_fixes_btn)

        export_fixes_btn = QPushButton("📥 Esporta CSV")
        export_fixes_btn.clicked.connect(self._export_fixes_csv)
        actions_layout.addWidget(export_fixes_btn)

        export_sql_btn = QPushButton("📥 Esporta SQL")
        export_sql_btn.clicked.connect(self._export_fixes_sql)
        actions_layout.addWidget(export_sql_btn)

        layout.addLayout(actions_layout)

        # Statistiche fix
        stats_group = QGroupBox("📊 Statistiche Fix")
        stats_layout = QGridLayout(stats_group)

        self.total_fixes_label = QLabel("Totale fix: --")
        self.pending_fixes_label = QLabel("Pending: --")
        self.automated_fixes_label = QLabel("Automatizzabili: --")
        self.avg_confidence_label = QLabel("Confidence media: --%")

        stats_layout.addWidget(self.total_fixes_label, 0, 0)
        stats_layout.addWidget(self.pending_fixes_label, 0, 1)
        stats_layout.addWidget(self.automated_fixes_label, 1, 0)
        stats_layout.addWidget(self.avg_confidence_label, 1, 1)

        layout.addWidget(stats_group)

        # Filtri
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Filtra per status:"))

        self.fix_status_combo = QComboBox()
        self.fix_status_combo.addItems(["Tutti", "PENDING", "APPLIED", "REJECTED", "FAILED"])
        self.fix_status_combo.currentTextChanged.connect(self._filter_fixes_table)
        filters_layout.addWidget(self.fix_status_combo)

        filters_layout.addWidget(QLabel("Filtra per tipo:"))

        self.fix_type_combo = QComboBox()
        self.fix_type_combo.addItems(["Tutti", "meta_description", "title", "alt_text", "canonical", "h1", "hreflang"])
        self.fix_type_combo.currentTextChanged.connect(self._filter_fixes_table)
        filters_layout.addWidget(self.fix_type_combo)

        self.show_automated_only = QCheckBox("Solo automatizzabili")
        self.show_automated_only.stateChanged.connect(self._filter_fixes_table)
        filters_layout.addWidget(self.show_automated_only)

        filters_layout.addStretch()

        layout.addLayout(filters_layout)

        # Tabella fix
        self.fixes_table = QTableWidget()
        self.fixes_table.setColumnCount(9)
        self.fixes_table.setHorizontalHeaderLabels([
            "ID", "Pagina", "Tipo", "Severity", "Valore Attuale", "Valore Suggerito",
            "Confidence", "Auto", "Azioni"
        ])

        # Ridimensionamento colonne - TUTTE ridimensionabili manualmente con mouse
        header = self.fixes_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # Tutte le colonne ridimensionabili
        header.setStretchLastSection(False)

        # Larghezze iniziali ottimali (px)
        header.resizeSection(0, 80)   # ID
        header.resizeSection(1, 300)  # Pagina
        header.resizeSection(2, 150)  # Tipo
        header.resizeSection(3, 120)  # Severity
        header.resizeSection(4, 250)  # Valore Attuale
        header.resizeSection(5, 250)  # Valore Suggerito
        header.resizeSection(6, 100)  # Confidence
        header.resizeSection(7, 80)   # Auto
        header.resizeSection(8, 100)  # Azioni

        self.fixes_table.setAlternatingRowColors(True)
        self.fixes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.fixes_table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.fixes_table)

        # Info box in basso
        info_label = QLabel(
            "💡 <b>Suggerimento:</b> Clicca 'Genera Fix Suggeriti' dopo aver completato una scansione per "
            "ottenere suggerimenti automatici su come risolvere gli issues rilevati."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                color: #1565C0;
                border-left: 4px solid #2196F3;
                padding: 12px;
                border-radius: 4px;
                margin-top: 8px;
                font-size: 13px;
            }
        """)
        layout.addWidget(info_label)

        self.tab_widget.addTab(fixes_widget, self.translation_manager.t("tab_fixes"))

    def _create_help_tab(self):
        """Crea tab aiuto con istruzioni"""
        help_widget = QWidget()
        layout = QVBoxLayout(help_widget)

        # Scroll area per contenuto lungo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Header con gradiente moderno
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb);
                border-radius: 12px;
                padding: 30px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(12)

        title_label = QLabel("🔍 PyPrestaScan")
        title_label.setStyleSheet("color: white; font-size: 36px; font-weight: bold; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        subtitle_label = QLabel("Scanner SEO Professionale per PrestaShop")
        subtitle_label.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 500; background: transparent;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)

        # Badge versione con stile moderno
        version_container = QWidget()
        version_container.setStyleSheet("background: transparent;")
        version_layout = QHBoxLayout(version_container)
        version_layout.setContentsMargins(0, 10, 0, 0)
        version_layout.addStretch()

        version_label = QLabel("v1.5.0")
        version_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: 600;
            background: rgba(255,255,255,0.25);
            border-radius: 14px;
            padding: 6px 18px;
        """)
        version_layout.addWidget(version_label)
        version_layout.addStretch()

        header_layout.addWidget(version_container)
        scroll_layout.addWidget(header_frame)

        # Sezione Come Usare
        usage_group = QGroupBox("Come Usare PyPrestaScan")
        usage_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2b2b2b;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background-color: white;
            }
        """)
        usage_layout = QVBoxLayout(usage_group)

        usage_text = QLabel(
            "<h3 style='color: #667eea;'>1. Tab Configurazione</h3>"
            "<ul style='line-height: 1.8;'>"
            "<li><b>URL Sito:</b> Inserisci l'URL completo del tuo PrestaShop (es: https://tuosito.com)</li>"
            "<li><b>Nome Progetto:</b> Identificativo univoco per la scansione (autogenerato con timestamp)</li>"
            "<li><b>Directory Export:</b> Cartella dove salvare i report HTML/CSV/JSON</li>"
            "<li><b>Preset Scansione:</b> Menu dropdown con configurazioni predefinite"
            "<ul style='margin: 8px 0;'>"
            "<li><b>Veloce (50 pagine)</b>: Test rapido, 10 connessioni, 0.1s delay</li>"
            "<li><b>Media (500 pagine)</b>: Analisi bilanciata, 10 connessioni, 0.2s delay</li>"
            "<li><b>Approfondita (10000 pagine)</b>: Scansione completa, 15 connessioni, 0.3s delay</li>"
            "<li><b>Solo Immagini ALT (1000 pagine)</b>: Focus su tag ALT, 10 connessioni</li>"
            "<li><b>Personalizzato</b>: Configura manualmente tutti i parametri</li>"
            "</ul>"
            "</li>"
            "<li><b>Max Pagine:</b> Numero massimo di URL da scansionare (0 = illimitato)</li>"
            "<li><b>Concorrenza:</b> Numero di richieste HTTP parallele (5-20 consigliato)</li>"
            "<li><b>Delay (secondi):</b> Pausa tra richieste per non sovraccaricare il server</li>"
            "<li><b>Profondità Crawling:</b> Livello massimo di link da seguire (0 = nessun limite)</li>"
            "<li><b>Modalità PrestaShop:</b> Abilita regole SEO specifiche per PrestaShop</li>"
            "<li><b>Includi Sottodomini:</b> Scansiona anche sottodomini (es: blog.tuosito.com)</li>"
            "<li><b>Resume:</b> Riprendi scansione interrotta usando stesso progetto</li>"
            "<li><b>Includi Generic Issues:</b> Mostra anche problemi SEO generici (non PrestaShop)</li>"
            "<li><b>User Agent:</b> Scegli browser da simulare (Desktop/Mobile/Bot/Custom)</li>"
            "<li><b>Mappa Lingue:</b> Associa URL multilingua (es: /it=/en,/fr=/en)</li>"
            "<li><b>🤖 AI Fix Avanzati (Opzionale - v1.5.0+):</b> Genera fix SEO intelligenti con AI"
            "<ul style='margin: 8px 0;'>"
            "<li><b>✨ Abilita AI:</b> Attiva generazione AI per Fix Suggeriti invece di template</li>"
            "<li><b>Provider AI:</b> Scegli tra DeepSeek (raccomandato, $0.14/1M token), OpenAI GPT-4o-mini ($0.15/1M), Claude Haiku ($0.80/1M)</li>"
            "<li><b>API Key:</b> Inserisci chiave API ottenuta dal provider (registrazione gratuita disponibile)</li>"
            "<li><b>💰 Costo:</b> ~$0.02 per 500 prodotti (DeepSeek) vs $240 lavoro manuale = 99.99% risparmio</li>"
            "<li><b>🎯 Risultato:</b> Meta description contestuali con benefici prodotto e CTA naturali</li>"
            "<li><b>🔒 Sicurezza:</b> Connessione diretta app→provider, zero dati a server PyPrestaScan</li>"
            "<li><b>📖 Guida:</b> Vedi <a href='https://github.com/andreapianidev/pyprestascan/blob/main/AI_INTEGRATION.md'>AI_INTEGRATION.md</a> per setup dettagliato</li>"
            "</ul>"
            "</li>"
            "</ul>"

            "<h3 style='color: #764ba2; margin-top: 20px;'>2. Tab Progress & Log</h3>"
            "<ul style='line-height: 1.8;'>"
            "<li><b>Statistiche Real-Time:</b> Contatori live di pagine, issues, immagini senza ALT</li>"
            "<li><b>Timer Elapsed:</b> Tempo trascorso dall'inizio della scansione</li>"
            "<li><b>Barra Progresso:</b> Avanzamento percentuale rispetto a Max Pagine</li>"
            "<li><b>Lista URL Scansionati:</b> Elenco in tempo reale delle ultime 100 pagine crawlate</li>"
            "<li><b>Log Dettagliato:</b> Tutti gli eventi con timestamp e livelli (DEBUG/INFO/WARNING/ERROR)</li>"
            "<li><b>Pulsante Ferma:</b> Interrompi scansione in corso (salvataggio automatico dati)</li>"
            "<li><b>Salva Log:</b> Esporta log completo in file TXT per analisi offline</li>"
            "</ul>"

            "<h3 style='color: #667eea; margin-top: 20px;'>3. Tab Risultati</h3>"
            "<ul style='line-height: 1.8;'>"
            "<li><b>KPI Dashboard:</b> Pannello con metriche chiave"
            "<ul style='margin: 8px 0;'>"
            "<li>Pagine Totali scansionate</li>"
            "<li>Tasso Successo (% pagine 2xx)</li>"
            "<li>Score Medio SEO (0-100)</li>"
            "<li>Issues Critici totali</li>"
            "</ul>"
            "</li>"
            "<li><b>Tabella Issues:</b> Elenco completo problemi SEO rilevati con:"
            "<ul style='margin: 8px 0;'>"
            "<li><b>Severity</b>: CRITICAL (rosso), WARNING (arancione), INFO (blu)</li>"
            "<li><b>Codice</b>: Identificatore univoco issue (es: MISSING_H1, DUPLICATE_TITLE)</li>"
            "<li><b>Descrizione</b>: Spiegazione dettagliata del problema</li>"
            "<li><b>Occorrenze</b>: Numero totale di volte che appare</li>"
            "<li><b>Pagine Coinvolte</b>: Quante pagine diverse hanno questo issue</li>"
            "</ul>"
            "</li>"
            "<li><b>Filtri Severity:</b> Pulsanti per filtrare CRITICAL/WARNING/INFO</li>"
            "<li><b>Barra Ricerca:</b> Cerca per codice o descrizione issue</li>"
            "<li><b>Click su Issue:</b> Doppio click per vedere lista pagine coinvolte</li>"
            "<li><b>Esporta CSV:</b> Salva tutti gli issues in formato CSV per Excel/Google Sheets</li>"
            "<li><b>Visualizza Report HTML:</b> Apri report interattivo con grafici e tabelle</li>"
            "<li><b>Apri Directory Export:</b> Accesso rapido alla cartella con tutti i file generati</li>"
            "</ul>"

            "<h3 style='color: #f093fb; margin-top: 20px;'>4. Tab Fix Suggeriti</h3>"
            "<ul style='line-height: 1.8;'>"
            "<li><b>Genera Fix Suggeriti:</b> Analizza issues e crea correzioni automatiche intelligenti</li>"
            "<li><b>Tabella Fix:</b> Elenco modifiche proposte con:"
            "<ul style='margin: 8px 0;'>"
            "<li><b>Issue Code</b>: Problema da risolvere</li>"
            "<li><b>Pagina</b>: URL interessato</li>"
            "<li><b>Campo</b>: Elemento da modificare (title, h1, meta_description, alt)</li>"
            "<li><b>Valore Attuale</b>: Contenuto esistente (problematico)</li>"
            "<li><b>Valore Suggerito</b>: Nuova proposta corretta</li>"
            "<li><b>Confidence</b>: Punteggio affidabilità (0-100%)</li>"
            "</ul>"
            "</li>"
            "<li><b>Filtro Confidence:</b> Slider per mostrare solo fix con confidence >= X%</li>"
            "<li><b>Statistiche Fix:</b> Contatori totali e per tipologia (title, h1, meta, alt)</li>"
            "<li><b>Esporta CSV Fix:</b> Salva suggerimenti in CSV per revisione manuale</li>"
            "<li><b>Esporta SQL Fix:</b> Genera query SQL UPDATE per applicare modifiche al DB PrestaShop"
            "<ul style='margin: 8px 0;'>"
            "<li style='color: #ff6b6b;'><b>ATTENZIONE:</b> Fai SEMPRE backup database prima di eseguire SQL!</li>"
            "<li>Le query UPDATE sono generate automaticamente per tabelle ps_meta/ps_product_lang</li>"
            "<li>Testa su ambiente staging prima di applicare in produzione</li>"
            "</ul>"
            "</li>"
            "</ul>"

            "<h3 style='color: #28a745; margin-top: 20px;'>5. Funzionalità Avanzate</h3>"
            "<ul style='line-height: 1.8;'>"
            "<li><b>Nuovo Progetto:</b> Crea nuova scansione con nome progetto timestamp autogenerato</li>"
            "<li><b>Carica Progetto:</b> Apri database esistente per vedere risultati passati</li>"
            "<li><b>Cancella Progetto:</b> Elimina database e report di un progetto</li>"
            "<li><b>Resume Scansione:</b> Riprendi scansione interrotta dal punto esatto di stop</li>"
            "<li><b>Export Multipli:</b> Report disponibili in HTML, CSV, JSON per ogni scansione</li>"
            "<li><b>Database SQLite:</b> Tutti i dati salvati in ~/.pyprestascan/[progetto]/crawl.db</li>"
            "<li><b>Log Colorati:</b> Livelli visivi per identificare rapidamente problemi</li>"
            "<li><b>Autosave:</b> Salvataggio automatico progressivo durante crawling</li>"
            "</ul>"
        )
        usage_text.setWordWrap(True)
        usage_text.setTextFormat(Qt.RichText)
        usage_layout.addWidget(usage_text)

        scroll_layout.addWidget(usage_group)

        # Sezione Sviluppatore
        dev_group = QGroupBox("Sviluppatore")
        dev_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2b2b2b;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background-color: white;
            }
        """)
        dev_layout = QVBoxLayout(dev_group)

        dev_frame = QFrame()
        dev_frame.setStyleSheet("QFrame { background-color: #F5F5F5; border-radius: 8px; padding: 15px; }")
        dev_inner_layout = QVBoxLayout(dev_frame)

        dev_name = QLabel("<h2 style='color: #2b2b2b;'>Andrea Piani</h2>")
        dev_name.setTextFormat(Qt.RichText)
        dev_inner_layout.addWidget(dev_name)

        dev_title = QLabel("Full-Stack Developer & SEO Specialist")
        dev_title.setStyleSheet("color: #666; font-size: 14px;")
        dev_inner_layout.addWidget(dev_title)

        dev_website = QLabel('<a href="https://www.andreapiani.com" style="color: #667eea; font-size: 14px; text-decoration: none; font-weight: 600;">www.andreapiani.com</a>')
        dev_website.setTextFormat(Qt.RichText)
        dev_website.setOpenExternalLinks(True)
        dev_inner_layout.addWidget(dev_website)

        dev_layout.addWidget(dev_frame)
        scroll_layout.addWidget(dev_group)

        # Sezione Open Source
        opensource_group = QGroupBox("Progetto Open Source")
        opensource_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2b2b2b;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background-color: white;
            }
        """)
        opensource_layout = QVBoxLayout(opensource_group)

        opensource_text = QLabel(
            "<p style='font-size: 14px; line-height: 1.6;'>"
            "PyPrestaScan è un progetto <b>open-source gratuito</b> rilasciato su GitHub.</p>"
            "<p style='font-size: 14px; line-height: 1.6;'>"
            "<b>Contributi, feedback e segnalazioni sono sempre benvenuti!</b></p>"
            "<br>"
            "<p style='font-size: 14px;'>"
            "<b>Repository GitHub:</b><br>"
            '<a href="https://github.com/andreapianidev/pyprestascan" style="color: #667eea; text-decoration: none; font-weight: 600;">'
            'github.com/andreapianidev/pyprestascan</a>'
            "</p>"
            "<br>"
            "<p style='font-size: 14px;'>"
            "<b>Segnala bug o richiedi funzionalità:</b><br>"
            '<a href="https://github.com/andreapianidev/pyprestascan/issues" style="color: #764ba2; text-decoration: none; font-weight: 600;">'
            'github.com/andreapianidev/pyprestascan/issues</a>'
            "</p>"
            "<br>"
            "<p style='font-size: 12px; color: #999;'>"
            "Licenza: MIT - Libero per uso commerciale e personale"
            "</p>"
        )
        opensource_text.setTextFormat(Qt.RichText)
        opensource_text.setWordWrap(True)
        opensource_text.setOpenExternalLinks(True)
        opensource_layout.addWidget(opensource_text)

        scroll_layout.addWidget(opensource_group)

        # Footer
        footer_label = QLabel(
            "<p style='text-align: center; color: #999; font-size: 11px;'>"
            "Made with ❤️ by Andrea Piani for the PrestaShop Community<br>"
            "Progetto open-source in continuo miglioramento"
            "</p>"
        )
        footer_label.setTextFormat(Qt.RichText)
        footer_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(footer_label)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        self.tab_widget.addTab(help_widget, self.translation_manager.t("tab_help"))

    def _setup_connections(self):
        """Configura connessioni segnali"""
        # Connetti segnali UI
        self.url_edit.textChanged.connect(self._validate_form)
        self.quiet_check.stateChanged.connect(self._handle_quiet_mode)
    
    def _load_settings(self):
        """Carica impostazioni salvate"""
        # Ripristina geometria finestra
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Ripristina valori form
        self.url_edit.setText(self.settings.value("url", ""))
        self.max_urls_spin.setValue(int(self.settings.value("max_urls", 10000)))
        self.concurrency_spin.setValue(int(self.settings.value("concurrency", 20)))
        # NON caricare project name - deve essere sempre nuovo con timestamp

        # Ripristina export directory
        export_dir = self.settings.value("export_dir", "./report")
        self.export_dir_edit.setText(export_dir)

        # Ripristina impostazioni AI
        ai_enabled = self.settings.value("ai_enabled", False, type=bool)
        self.ai_enabled_check.setChecked(ai_enabled)

        ai_provider = self.settings.value("ai_provider", "deepseek")
        # Trova index del provider
        for i in range(self.ai_provider_combo.count()):
            if self.ai_provider_combo.itemData(i) == ai_provider:
                self.ai_provider_combo.setCurrentIndex(i)
                break

        # API key (se salvata - per sicurezza potremmo non salvarla)
        ai_api_key = self.settings.value("ai_api_key", "")
        self.ai_api_key_edit.setText(ai_api_key)

    def _save_settings(self):
        """Salva impostazioni"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("url", self.url_edit.text())
        self.settings.setValue("max_urls", self.max_urls_spin.value())
        self.settings.setValue("concurrency", self.concurrency_spin.value())
        # NON salvare project name - deve essere sempre nuovo
        self.settings.setValue("export_dir", self.export_dir_edit.text())

        # Salva impostazioni AI
        self.settings.setValue("ai_enabled", self.ai_enabled_check.isChecked())
        self.settings.setValue("ai_provider", self.ai_provider_combo.currentData())
        # Salva API key (ATTENZIONE: in chiaro nel file settings!)
        # In futuro si potrebbe usare keyring per sicurezza
        self.settings.setValue("ai_api_key", self.ai_api_key_edit.text())
    
    def _validate_form(self):
        """Valida form e abilita/disabilita bottoni"""
        url_valid = bool(self.url_edit.text().strip())

        self.start_btn.setEnabled(url_valid and not self.is_crawling)
    
    def _handle_quiet_mode(self, state):
        """Gestisce modalità quiet"""
        if state == Qt.Checked:
            self.debug_check.setChecked(False)
            self.debug_check.setEnabled(False)
        else:
            self.debug_check.setEnabled(True)
    
    def _update_ui_state(self):
        """Aggiorna stato UI periodicamente"""
        # Aggiorna stato bottoni
        self._validate_form()
    
    def _test_url(self):
        """Testa accessibilità URL"""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Errore", "Inserisci un URL valido")
            return
        
        # Qui si potrebbe fare un test HTTP preliminare
        QMessageBox.information(self, "Test URL", f"URL sembra valido: {url}")
    
    def _browse_export_dir(self):
        """Sfoglia directory export"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Directory Report",
            self.export_dir_edit.text()
        )

        if dir_path:
            self.export_dir_edit.setText(dir_path)

    def _apply_fast_preset(self):
        """Applica preset scansione veloce"""
        self.max_urls_spin.setValue(500)
        self.concurrency_spin.setValue(30)
        self.delay_spin.setValue(100)
        self.depth_spin.setValue(0)
        QMessageBox.information(
            self,
            "Preset Applicato",
            "⚡ Scansione Veloce attivata!\n\n"
            "• 500 pagine massime\n"
            "• 30 richieste parallele\n"
            "• 100ms delay (sicuro)\n"
            "• Profondità illimitata\n\n"
            "Ideale per test rapidi e preview del sito."
        )

    def _apply_deep_preset(self):
        """Applica preset scansione approfondita"""
        self.max_urls_spin.setValue(10000)
        self.concurrency_spin.setValue(20)
        self.delay_spin.setValue(200)
        self.depth_spin.setValue(0)
        QMessageBox.information(
            self,
            "Preset Applicato",
            "🔍 Scansione Approfondita attivata!\n\n"
            "• 10000 pagine massime\n"
            "• 20 richieste parallele\n"
            "• 200ms delay (molto sicuro)\n"
            "• Profondità illimitata\n\n"
            "Analisi completa e accurata, rispetta i limiti del server."
        )

    def _apply_alt_preset(self):
        """Applica preset scansione ALT immagini"""
        self.max_urls_spin.setValue(1000)
        self.concurrency_spin.setValue(25)
        self.delay_spin.setValue(150)
        self.depth_spin.setValue(0)
        QMessageBox.information(
            self,
            "Preset Applicato",
            "🖼️ Scansione ALT Immagini attivata!\n\n"
            "• 1000 pagine massime\n"
            "• 25 richieste parallele\n"
            "• 150ms delay (bilanciato)\n"
            "• Profondità illimitata\n\n"
            "Focus su immagini senza attributo ALT.\n"
            "Controlla i risultati nella sezione 'Immagini senza ALT'."
        )
    
    def _open_config_dialog(self):
        """Apre dialog configurazione avanzata"""
        dialog = ConfigDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Applica configurazione avanzata
            # (implementazione futura)
            pass
    
    def _start_crawl(self):
        """Avvia crawling"""
        try:
            # Valida URL
            url = self.url_edit.text().strip()
            if not url:
                QMessageBox.warning(self, "Errore", "Inserisci un URL valido")
                return

            if not url.startswith(('http://', 'https://')):
                QMessageBox.warning(self, "Errore", "L'URL deve iniziare con http:// o https://")
                return

            # Valida configurazione
            config = self._build_config()
            cli_context = self._build_cli_context()

            # Salva project name per _load_results()
            self.current_project_name = config.project

            # Aggiorna UI
            self.is_crawling = True
            self._update_crawling_ui(True)
            
            # Passa a tab progress
            self.tab_widget.setCurrentIndex(1)
            
            # Crea worker thread
            self.crawler_thread = QThread()
            self.crawler_worker = CrawlerWorker(config, cli_context)
            self.crawler_worker.moveToThread(self.crawler_thread)
            
            # Connetti segnali
            self.crawler_thread.started.connect(self.crawler_worker.run_crawl)
            self.crawler_worker.progress_updated.connect(self._on_progress_updated)
            self.crawler_worker.log_message.connect(self._on_log_message)
            self.crawler_worker.crawl_finished.connect(self._on_crawl_finished)
            self.crawler_worker.stats_updated.connect(self._on_stats_updated)
            
            # Avvia thread
            self.crawler_thread.start()
            
            self._log_message("INFO", "🚀 Scansione avviata...")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'avvio: {str(e)}")
            self.is_crawling = False
            self._update_crawling_ui(False)
    
    def _stop_crawl(self):
        """Ferma crawling"""
        if self.crawler_worker:
            self.crawler_worker.stop_crawl()
            self._log_message("WARNING", "🛑 Richiesta di stop inviata...")

    def _on_user_agent_changed(self, index: int):
        """Gestisce cambio User Agent"""
        # Mostra/nascondi campo custom
        is_custom = self.user_agent_combo.currentText().startswith("Custom")
        self.custom_ua_edit.setVisible(is_custom)

        # Aggiorna label info
        if is_custom:
            self.ua_info_label.setText("💡 Inserisci un User Agent personalizzato nel campo sopra")
        else:
            ua_string = self.user_agent_combo.currentData()
            if ua_string:
                # Mostra solo prime 80 caratteri
                display_ua = ua_string[:80] + "..." if len(ua_string) > 80 else ua_string
                self.ua_info_label.setText(f"UA: {display_ua}")

    def _on_ai_enabled_changed(self, checked: bool):
        """Abilita/disabilita campi AI"""
        self.ai_provider_combo.setEnabled(checked)
        self.ai_api_key_edit.setEnabled(checked)
        self.ai_show_key_btn.setEnabled(checked)

    def _toggle_ai_key_visibility(self):
        """Mostra/nascondi API key"""
        if self.ai_api_key_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.ai_api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ai_show_key_btn.setText("🙈")
        else:
            self.ai_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.ai_show_key_btn.setText("👁️")

    def _build_config(self) -> CrawlConfig:
        """Costruisce configurazione da UI"""
        # Parsing lang_map
        lang_map = {}
        lang_map_text = self.lang_map_edit.text().strip()
        if lang_map_text:
            for pair in lang_map_text.split(','):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    lang_map[key.strip()] = value.strip()

        # Depth (0 = unlimited -> None)
        depth = self.depth_spin.value() if self.depth_spin.value() > 0 else None

        # User Agent
        user_agent = None
        if self.user_agent_combo.currentText().startswith("Custom"):
            # User agent personalizzato
            custom_ua = self.custom_ua_edit.text().strip()
            if custom_ua:
                user_agent = custom_ua
        else:
            # User agent dal combo
            user_agent = self.user_agent_combo.currentData()

        config = CrawlConfig(
            url=self.url_edit.text().strip(),
            max_urls=self.max_urls_spin.value(),
            concurrency=self.concurrency_spin.value(),
            delay=self.delay_spin.value(),
            include_subdomains=self.subdomains_check.isChecked(),
            prestashop_mode=self.prestashop_check.isChecked(),
            resume=self.resume_check.isChecked(),
            project=self.project_edit.text().strip(),
            export_dir=Path(self.export_dir_edit.text().strip()),
            include_generic=self.include_generic_check.isChecked(),
            lang_map=lang_map,
            depth=depth,
            user_agent=user_agent
        )

        return config
    
    def _build_cli_context(self) -> CliContext:
        """Costruisce contesto CLI da UI"""
        config = self._build_config()  # Needed for CliContext
        
        context = CliContext(
            config=config,
            debug=self.debug_check.isChecked(),
            quiet=self.quiet_check.isChecked(),
            no_color=self.no_color_check.isChecked()
        )
        
        return context
    
    def _update_crawling_ui(self, is_crawling: bool):
        """Aggiorna UI per stato crawling"""
        # Bottoni
        self.start_btn.setEnabled(not is_crawling)
        self.stop_btn.setEnabled(is_crawling)
        
        # Status bar
        if is_crawling:
            self.status_bar.showMessage("🔍 Scansione in corso...")
        else:
            self.status_bar.showMessage("Pronto per nuova scansione")
    
    def _on_progress_updated(self, current: int, total: int, status: str):
        """Gestisce aggiornamento progress"""
        if total > 0:
            progress = int((current / total) * 100)
            self.main_progress.setValue(progress)
            self.main_progress.setFormat(f"{current}/{total} ({progress}%) - {status}")
        
        # Aggiorna statistiche
        self.pages_crawled_label.setText(f"Pagine scansionate: {current}")
    
    def _on_log_message(self, level: str, message: str):
        """Gestisce messaggi di log"""
        self._log_message(level, message)
    
    def _on_stats_updated(self, stats: Dict[str, Any]):
        """Gestisce aggiornamento statistiche"""
        self.pages_failed_label.setText(f"Pagine fallite: {stats.get('pages_failed', 0)}")
        self.issues_found_label.setText(f"Issues trovati: {stats.get('total_issues', 0)}")
        self.images_no_alt_label.setText(f"Immagini senza ALT: {stats.get('images_no_alt', 0)}")

        # Aggiorna timer elapsed e ETA
        elapsed_time = stats.get('elapsed_time', 0)
        if elapsed_time > 0:
            elapsed_minutes = int(elapsed_time / 60)
            elapsed_secs = int(elapsed_time % 60)
            self.elapsed_label.setText(f"⏱️ Tempo trascorso: {elapsed_minutes}m {elapsed_secs}s")

        eta = stats.get('eta', '--')
        self.eta_label.setText(f"⏳ Tempo stimato: {eta}")
    
    def _on_crawl_finished(self, success: bool, message: str):
        """Gestisce fine crawling"""
        self.is_crawling = False
        self._update_crawling_ui(False)
        
        # Cleanup thread
        if self.crawler_thread:
            self.crawler_thread.quit()
            self.crawler_thread.wait()
            self.crawler_thread = None
            self.crawler_worker = None
        
        # Log finale
        level = "INFO" if success else "ERROR"
        self._log_message(level, f"✅ {message}" if success else f"❌ {message}")
        
        if success:
            # Abilita bottoni report
            self.view_report_btn.setEnabled(True)
            self.open_export_dir_btn.setEnabled(True)
            self.export_excel_btn.setEnabled(True)

            # Passa a tab risultati
            self.tab_widget.setCurrentIndex(2)

            # Mostra notifica successo
            QMessageBox.information(self, "Completato", "Scansione completata con successo!")

            # Carica risultati DOPO il dialog per evitare problemi UI
            self._load_results()
        else:
            QMessageBox.warning(self, "Errore", f"Scansione terminata con errori:\n{message}")
    
    def _log_message(self, level: str, message: str):
        """Aggiunge messaggio al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Colore per livello
        color_map = {
            "DEBUG": "#888888",
            "INFO": "#00D4FF",  # Cyan chiaro per INFO
            "WARNING": "#FF8C00",
            "ERROR": "#FF0000",
            "SUCCESS": "#00FF00"
        }
        
        color = color_map.get(level, "#000000")
        
        formatted_message = f'<span style="color: {color};">[{timestamp}] {level}: {message}</span>'
        
        self.log_text.append(formatted_message)
        
        # Auto-scroll
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def _load_results(self):
        """Carica risultati nella tab risultati"""
        try:
            from ..core.storage import CrawlDatabase
            from pathlib import Path
            import asyncio
            import traceback

            self._log_message("DEBUG", "🔍 Inizio caricamento risultati...")

            # Path database dal progetto corrente (usa nome progetto salvato durante scan)
            project_name = getattr(self, 'current_project_name', None) or self.project_edit.text()
            db_path = Path.home() / ".pyprestascan" / project_name / "crawl.db"

            self._log_message("DEBUG", f"📂 Cerco database in: {db_path}")

            # Se non esiste, cerca il database più recente in .pyprestascan
            if not db_path.exists():
                self._log_message("DEBUG", "⚠️ Database non trovato, cerco il più recente...")
                base_dir = Path.home() / ".pyprestascan"
                if base_dir.exists():
                    # Trova tutti i database esistenti
                    all_dbs = list(base_dir.glob("*/crawl.db"))
                    if all_dbs:
                        # Ordina per data modifica (più recente prima)
                        db_path = max(all_dbs, key=lambda p: p.stat().st_mtime)
                        self.current_project_name = db_path.parent.name
                        self._log_message("INFO", f"✅ Carico database più recente: {db_path.parent.name}")
                    else:
                        self._log_message("WARNING", f"❌ Nessun database trovato - esegui prima una scansione")
                        return
                else:
                    self._log_message("WARNING", f"❌ Directory .pyprestascan non trovata - esegui prima una scansione")
                    return
            else:
                self._log_message("DEBUG", f"✅ Database trovato: {db_path}")

            # Carica risultati reali dal database
            self._log_message("DEBUG", "📊 Apertura database...")
            db = CrawlDatabase(db_path)

            # Crea nuovo event loop dedicato per evitare conflitti
            self._log_message("DEBUG", "🔄 Creo event loop...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Esegui queries async in modo sincrono per GUI
                self._log_message("DEBUG", "📈 Carico statistiche...")
                stats = loop.run_until_complete(db.get_crawl_stats())
                self._log_message("DEBUG", "📄 Carico pagine...")
                pages = loop.run_until_complete(db.export_pages())
                self._log_message("DEBUG", "🐛 Carico issues...")
                issues = loop.run_until_complete(db.export_issues())
                self._log_message("DEBUG", f"✅ Caricate {len(issues)} issues dal database")
            finally:
                loop.close()

            # Aggiorna KPI
            self._log_message("DEBUG", "📊 Aggiorno KPI...")
            general = stats.get('general', {})
            status_stats = stats.get('status', {})
            issue_stats = stats.get('issues', {})

            total_pages = general.get('total_pages', 0)
            success_pages = status_stats.get('2xx', 0)
            success_rate = round((success_pages / total_pages * 100) if total_pages > 0 else 0, 1)
            avg_score = round(general.get('avg_score', 0) or 0, 1)
            critical_issues = issue_stats.get('CRITICAL', 0)

            self.total_pages_label.setText(f"Pagine totali: {total_pages}")
            self.success_rate_label.setText(f"Tasso successo: {success_rate}%")
            self.avg_score_label.setText(f"Score medio: {avg_score}")
            self.critical_issues_label.setText(f"Issues critici: {critical_issues}")

            # Raggruppa issues per criticità
            self._log_message("DEBUG", "📋 Raggruppo issues per severity...")
            issues_by_severity = self._group_issues_by_severity(issues)
            self._log_message("DEBUG", f"✅ Raggruppati {len(issues_by_severity)} issues unici")

            # Popola tabella con issues reali
            self._log_message("DEBUG", "📝 Popolo tabella issues...")
            self._populate_issues_table(issues_by_severity)
            self._log_message("INFO", f"✅ Caricamento completato: {len(issues_by_severity)} issues visualizzati")

        except Exception as e:
            self._log_message("ERROR", f"❌ Errore caricamento risultati: {str(e)}")
            self._log_message("DEBUG", f"Stack trace: {traceback.format_exc()}")
    
    def _group_issues_by_severity(self, issues):
        """Raggruppa issues per severity e codice"""
        from collections import defaultdict
        
        grouped = defaultdict(lambda: {'count': 0, 'pages': set(), 'message': '', 'severity': ''})
        
        for issue in issues:
            code = issue.get('code', 'UNKNOWN')
            severity = issue.get('severity', 'INFO')
            message = issue.get('message', 'Nessuna descrizione')
            page_url = issue.get('page_url', '')
            
            grouped[code]['count'] += 1
            grouped[code]['pages'].add(page_url)
            grouped[code]['message'] = message
            grouped[code]['severity'] = severity
        
        # Converte in lista ordinata per severity (CRITICAL > WARNING > INFO)
        severity_order = {'CRITICAL': 0, 'WARNING': 1, 'INFO': 2}
        
        result = []
        for code, data in grouped.items():
            result.append({
                'code': code,
                'severity': data['severity'],
                'message': data['message'],
                'count': data['count'],
                'affected_pages': len(data['pages']),
                'sort_key': severity_order.get(data['severity'], 3)
            })
        
        # Ordina per severity e poi per count
        result.sort(key=lambda x: (x['sort_key'], -x['count']))
        return result
    
    def _populate_issues_table(self, issues_data, save_to_all=True):
        """Popola tabella con issues categorizzati per criticità"""
        self._log_message("DEBUG", f"📝 Popolo tabella con {len(issues_data)} issues...")

        self.results_table.setRowCount(len(issues_data))

        for row, issue in enumerate(issues_data):
            severity = issue['severity']
            code = issue.get('code', 'UNKNOWN')
            message = issue.get('message', 'Nessuna descrizione')
            count = issue.get('count', 0)
            affected_pages = issue.get('affected_pages', 0)

            self._log_message("DEBUG", f"  Row {row}: {severity} - {code} - {count} occorrenze")

            # Severity con colori
            severity_item = QTableWidgetItem(severity)
            if severity == "CRITICAL":
                severity_item.setBackground(QColor("#ffebee"))
                severity_item.setForeground(QColor("#c62828"))
                severity_item.setText("🔴 CRITICAL")
            elif severity == "WARNING":
                severity_item.setBackground(QColor("#fff3e0"))
                severity_item.setForeground(QColor("#ef6c00"))
                severity_item.setText("🟡 WARNING")
            else:  # INFO
                severity_item.setBackground(QColor("#e3f2fd"))
                severity_item.setForeground(QColor("#1976d2"))
                severity_item.setText("🔵 INFO")

            # Code item
            code_item = QTableWidgetItem(code)
            code_item.setFont(QFont("Monaco", 9))

            # Altri item
            desc_item = QTableWidgetItem(message)
            count_item = QTableWidgetItem(str(count))
            pages_item = QTableWidgetItem(str(affected_pages))

            # Evidenzia conteggi alti
            if count >= 10:
                count_item.setBackground(QColor("#ffebee"))
                count_item.setForeground(QColor("#c62828"))
            elif count >= 5:
                count_item.setBackground(QColor("#fff3e0"))
                count_item.setForeground(QColor("#ef6c00"))

            self.results_table.setItem(row, 0, severity_item)
            self.results_table.setItem(row, 1, code_item)
            self.results_table.setItem(row, 2, desc_item)
            self.results_table.setItem(row, 3, count_item)
            self.results_table.setItem(row, 4, pages_item)

        # Ridimensiona colonne
        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setStretchLastSection(True)

        # Salva dati per filtraggio solo se richiesto (non quando si filtra)
        if save_to_all:
            self.all_issues_data = issues_data
            self._log_message("DEBUG", f"✅ Salvati {len(issues_data)} issues in all_issues_data")

        self._log_message("DEBUG", f"✅ Tabella popolata con {len(issues_data)} righe")
    
    def _filter_issues_table(self):
        """Filtra tabella issues per severity"""
        if not hasattr(self, 'all_issues_data'):
            return

        # Ottieni severity selezionate
        show_critical = self.show_critical_check.isChecked()
        show_warning = self.show_warning_check.isChecked()
        show_info = self.show_info_check.isChecked()

        # Filtra dati
        filtered_data = []
        for issue in self.all_issues_data:
            severity = issue['severity']
            if ((severity == 'CRITICAL' and show_critical) or
                (severity == 'WARNING' and show_warning) or
                (severity == 'INFO' and show_info)):
                filtered_data.append(issue)

        # Ripopola tabella SENZA sovrascrivere all_issues_data
        self._populate_issues_table(filtered_data, save_to_all=False)
    
    def _export_issues_csv(self):
        """Esporta issues correnti in CSV"""
        if not hasattr(self, 'all_issues_data') or not self.all_issues_data:
            QMessageBox.information(self, "Nessun dato", "Non ci sono issues da esportare")
            return
        
        # Scegli file di destinazione
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Esporta Issues CSV",
            f"issues_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "File CSV (*.csv)"
        )
        
        if not filename:
            return
        
        try:
            import csv
            
            # Ottieni issues filtrati correnti
            show_critical = self.show_critical_check.isChecked()
            show_warning = self.show_warning_check.isChecked()
            show_info = self.show_info_check.isChecked()
            
            filtered_data = []
            for issue in self.all_issues_data:
                severity = issue['severity']
                if ((severity == 'CRITICAL' and show_critical) or
                    (severity == 'WARNING' and show_warning) or
                    (severity == 'INFO' and show_info)):
                    filtered_data.append(issue)
            
            # Scrivi CSV
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow(['Severity', 'Codice', 'Descrizione', 'Occorrenze', 'Pagine Coinvolte'])
                
                # Dati
                for issue in filtered_data:
                    writer.writerow([
                        issue['severity'],
                        issue['code'],
                        issue['message'],
                        issue['count'],
                        issue['affected_pages']
                    ])
            
            QMessageBox.information(self, "Export completato", f"Issues esportati in: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Errore export", f"Errore durante l'export: {str(e)}")

    def _export_excel(self):
        """Esporta report completo in formato Excel"""
        try:
            from ..core.storage import CrawlDatabase
            from pathlib import Path
            import asyncio

            # Path database
            project_name = getattr(self, 'current_project_name', None) or self.project_edit.text()
            db_path = Path.home() / ".pyprestascan" / project_name / "crawl.db"

            if not db_path.exists():
                QMessageBox.warning(self, "Database non trovato", "Esegui prima una scansione")
                return

            # Scegli file di destinazione
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Esporta Report Excel",
                f"report_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "File Excel (*.xlsx)"
            )

            if not filename:
                return

            # Carica dati dal database
            db = CrawlDatabase(db_path)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                stats = loop.run_until_complete(db.get_crawl_stats())
                pages = loop.run_until_complete(db.export_pages())
                issues = loop.run_until_complete(db.export_issues())

                # Carica fix se disponibili
                fixes = []
                try:
                    fixes = loop.run_until_complete(db.get_all_fixes())
                except:
                    pass

            finally:
                loop.close()

            # Prepara dati per exporter
            scan_results = {
                'stats': stats,
                'pages': pages,
                'issues': issues,
                'fixes': fixes,
                'project_name': project_name,
                'scan_date': datetime.now().isoformat()
            }

            # Crea report Excel
            exporter = ExcelReportExporter(scan_results)
            output_path = exporter.export(Path(filename))

            # Conferma e apri
            reply = QMessageBox.question(
                self,
                "Export completato",
                f"Report Excel creato:\n{output_path}\n\nVuoi aprirlo ora?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                QDesktopServices.openUrl(f"file://{output_path}")

        except Exception as e:
            import traceback
            error_msg = f"Errore durante l'export Excel:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Errore export", error_msg)

    def _show_issue_details(self, item):
        """Mostra dettagli di un issue selezionato"""
        row = item.row()
        if row < 0 or not hasattr(self, 'all_issues_data'):
            return
        
        # Ottieni dati issue dalla tabella filtrata
        code_item = self.results_table.item(row, 1)
        if not code_item:
            return
        
        code = code_item.text()
        
        # Trova issue nei dati completi
        issue_data = None
        for issue in self.all_issues_data:
            if issue['code'] == code:
                issue_data = issue
                break
        
        if not issue_data:
            return
        
        # Carica pagine coinvolte dal database
        try:
            from ..core.storage import CrawlDatabase
            from pathlib import Path
            import asyncio

            # Path database dal progetto corrente (usa la stessa logica di ProjectManager)
            project_name = self.project_edit.text()
            db_path = Path.home() / ".pyprestascan" / project_name / "crawl.db"

            if not db_path.exists():
                QMessageBox.information(self, "Database non trovato", f"Database del progetto non disponibile in:\n{db_path}")
                return
            
            db = CrawlDatabase(db_path)
            
            # Crea evento loop se necessario
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Query per pagine con questo issue
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT DISTINCT i.page_url, p.title, p.status_code, p.score
                    FROM issues i
                    LEFT JOIN pages p ON i.page_url = p.url
                    WHERE i.code = ?
                    ORDER BY p.score ASC, i.page_url
                    LIMIT 20
                """, (code,))
                
                affected_pages = cursor.fetchall()
            
            # Mostra dialog con dettagli
            self._show_issue_details_dialog(issue_data, affected_pages)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel caricamento dettagli: {str(e)}")
    
    def _show_issue_details_dialog(self, issue_data, affected_pages):
        """Mostra dialog con dettagli issue"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Dettagli Issue: {issue_data['code']}")
        dialog.setModal(True)
        dialog.resize(800, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Header issue
        header_layout = QHBoxLayout()
        
        severity = issue_data['severity']
        if severity == "CRITICAL":
            severity_label = QLabel("🔴 CRITICAL")
            severity_label.setStyleSheet("color: #c62828; font-weight: bold; font-size: 14px;")
        elif severity == "WARNING":
            severity_label = QLabel("🟡 WARNING")
            severity_label.setStyleSheet("color: #ef6c00; font-weight: bold; font-size: 14px;")
        else:
            severity_label = QLabel("🔵 INFO")
            severity_label.setStyleSheet("color: #1976d2; font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(severity_label)
        header_layout.addStretch()
        
        stats_label = QLabel(f"Occorrenze: {issue_data['count']} | Pagine: {issue_data['affected_pages']}")
        stats_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(stats_label)
        
        layout.addLayout(header_layout)
        
        # Descrizione
        desc_group = QGroupBox(f"Codice: {issue_data['code']}")
        desc_layout = QVBoxLayout(desc_group)
        
        desc_label = QLabel(issue_data['message'])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("padding: 10px; background-color: #f5f5f5; border-radius: 5px;")
        desc_layout.addWidget(desc_label)
        
        # Suggerimenti di risoluzione
        suggestion = self._get_issue_suggestion(issue_data['code'])
        if suggestion:
            suggestion_label = QLabel(f"💡 Suggerimento: {suggestion}")
            suggestion_label.setWordWrap(True)
            suggestion_label.setStyleSheet("padding: 10px; background-color: #e8f5e8; border-radius: 5px; color: #2e7d32;")
            desc_layout.addWidget(suggestion_label)
        
        layout.addWidget(desc_group)
        
        # Tabella pagine coinvolte
        pages_group = QGroupBox("Pagine Coinvolte (max 20)")
        pages_layout = QVBoxLayout(pages_group)
        
        pages_table = QTableWidget(len(affected_pages), 4)
        pages_table.setHorizontalHeaderLabels(["URL", "Title", "Status", "Score"])
        
        for row, (url, title, status_code, score) in enumerate(affected_pages):
            # URL (cliccabile)
            url_item = QTableWidgetItem(url)
            url_item.setToolTip(f"Clicca per aprire: {url}")
            url_item.setForeground(QColor("#1976d2"))
            url_item.setData(Qt.UserRole, url)  # Salva URL per apertura
            
            # Title
            title_item = QTableWidgetItem(title or "N/A")
            title_item.setToolTip(title or "Nessun titolo")
            
            # Status
            status_item = QTableWidgetItem(str(status_code or "N/A"))
            if status_code and status_code >= 400:
                status_item.setForeground(QColor("#c62828"))
            elif status_code and status_code >= 300:
                status_item.setForeground(QColor("#ef6c00"))
            else:
                status_item.setForeground(QColor("#2e7d32"))
            
            # Score
            score_item = QTableWidgetItem(str(score or "N/A"))
            if score is not None:
                if score < 40:
                    score_item.setForeground(QColor("#c62828"))
                elif score < 60:
                    score_item.setForeground(QColor("#ef6c00"))
                else:
                    score_item.setForeground(QColor("#2e7d32"))
            
            pages_table.setItem(row, 0, url_item)
            pages_table.setItem(row, 1, title_item)
            pages_table.setItem(row, 2, status_item)
            pages_table.setItem(row, 3, score_item)
        
        pages_table.resizeColumnsToContents()
        pages_table.horizontalHeader().setStretchLastSection(True)
        pages_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Double-click per aprire URL
        def open_url(item):
            if item.column() == 0:  # Solo colonna URL
                url = item.data(Qt.UserRole)
                if url:
                    import webbrowser
                    webbrowser.open(url)
        
        pages_table.itemDoubleClicked.connect(open_url)
        
        pages_layout.addWidget(pages_table)
        
        # Hint
        hint = QLabel("💡 Doppio click su un URL per aprirlo nel browser")
        hint.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        pages_layout.addWidget(hint)
        
        layout.addWidget(pages_group)
        
        # Bottoni
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("📥 Esporta Pagine CSV")
        export_btn.clicked.connect(lambda: self._export_affected_pages_csv(issue_data['code'], affected_pages))
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Chiudi")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _export_affected_pages_csv(self, issue_code, affected_pages):
        """Esporta pagine coinvolte in CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            f"Esporta pagine con issue {issue_code}",
            f"pages_{issue_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "File CSV (*.csv)"
        )
        
        if not filename:
            return
        
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow(['URL', 'Title', 'Status Code', 'Score SEO'])
                
                # Dati
                for url, title, status_code, score in affected_pages:
                    writer.writerow([url, title or '', status_code or '', score or ''])
            
            QMessageBox.information(self, "Export completato", f"Pagine esportate in: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore export", f"Errore durante l'export: {str(e)}")
    
    def _get_issue_suggestion(self, issue_code):
        """Restituisce suggerimenti di risoluzione per un issue"""
        suggestions = {
            'TITLE_MISSING': 'Aggiungi un tag <title> a ogni pagina. È fondamentale per SEO.',
            'TITLE_TOO_LONG': 'Riduci il title a massimo 60 caratteri per evitare troncamenti in SERP.',
            'TITLE_TOO_SHORT': 'Espandi il title ad almeno 10 caratteri per fornire informazioni sufficienti.',
            'TITLE_DUPLICATE': 'Rendi unico ogni title. Ogni pagina dovrebbe avere un titolo specifico.',
            'H1_MISSING': 'Aggiungi un tag <h1> a ogni pagina per definire l\'argomento principale.',
            'H1_MULTIPLE': 'Usa un solo <h1> per pagina. Converti H1 aggiuntivi in H2 o H3.',
            'META_DESCRIPTION_MISSING': 'Aggiungi una meta description di 120-160 caratteri per ogni pagina.',
            'META_DESCRIPTION_TOO_LONG': 'Riduci la meta description a massimo 160 caratteri.',
            'META_DESCRIPTION_TOO_SHORT': 'Espandi la meta description ad almeno 50 caratteri.',
            'CANONICAL_MISSING': 'Aggiungi link canonical per evitare contenuti duplicati.',
            'CANONICAL_MISSING_PRODUCT': 'Aggiungi canonical URL ai prodotti per evitare duplicati da filtri e varianti.',
            'IMAGES_MISSING_ALT': 'Aggiungi attributi ALT descrittivi a tutte le immagini per accessibilità.',
            'CART_INDEXABLE': 'Aggiungi meta robots="noindex" alle pagine carrello/checkout.',
            'FACETED_NO_CANONICAL': 'Usa canonical per puntare alla versione non filtrata della categoria.',
            'PRODUCT_NO_JSONLD': 'Implementa JSON-LD Schema.org Product per rich snippet.',
            'CATEGORY_NO_PAGINATION': 'Aggiungi rel="prev" e rel="next" alle pagine paginati.',
            'HREFLANG_MISSING': 'Implementa hreflang per siti multilingua.',
            'OG_TITLE_MISSING': 'Aggiungi og:title per migliorare condivisioni social.',
            'OG_DESCRIPTION_MISSING': 'Aggiungi og:description per condivisioni social accattivanti.',
            'OG_IMAGE_MISSING': 'Aggiungi og:image (min 1200x630px) per preview social.',
            'HEADINGS_HIERARCHY': 'Segui gerarchia logica: H1 → H2 → H3, senza saltare livelli.',
            'IMAGES_NO_LAZY_LOADING': 'Implementa loading="lazy" per immagini below-the-fold.'
        }
        
        return suggestions.get(issue_code, '')
    
    def _save_log(self):
        """Salva log su file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Salva Log",
            f"pyprestascan_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "File di testo (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, "Salvato", f"Log salvato in: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore nel salvataggio: {str(e)}")
    
    def _open_report(self):
        """Apre report HTML"""
        report_path = Path(self.export_dir_edit.text()) / "report.html"
        
        if report_path.exists():
            # Apri nel browser
            webbrowser.open(f"file://{report_path.absolute()}")
        else:
            QMessageBox.warning(self, "File non trovato", f"Report non trovato in: {report_path}")
    
    def _open_export_dir(self):
        """Apre directory export"""
        export_dir = Path(self.export_dir_edit.text())
        
        if export_dir.exists():
            # Apri nella finestra del sistema
            QDesktopServices.openUrl(f"file://{export_dir.absolute()}")
        else:
            QMessageBox.warning(self, "Directory non trovata", f"Directory non trovata: {export_dir}")
    
    def _new_project(self):
        """Crea nuovo progetto"""
        self.project_edit.clear()
        self.project_edit.setText(f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.resume_check.setChecked(False)
    
    def _open_project(self):
        """Apri progetto esistente"""
        # Per ora semplice dialog
        project_name, ok = QInputDialog.getText(
            self, 
            "Apri Progetto", 
            "Nome progetto:"
        )
        
        if ok and project_name:
            self.project_edit.setText(project_name)
            self.resume_check.setChecked(True)
    
    def _generate_fixes(self):
        """Genera fix suggeriti per gli issues rilevati"""
        try:
            # Verifica che ci sia un database (usa stesso path di _load_results)
            project_name = getattr(self, 'current_project_name', None) or self.project_edit.text()
            db_path = Path.home() / ".pyprestascan" / project_name / "crawl.db"

            # Se non esiste, cerca il più recente
            if not db_path.exists():
                base_dir = Path.home() / ".pyprestascan"
                if base_dir.exists():
                    all_dbs = list(base_dir.glob("*/crawl.db"))
                    if all_dbs:
                        db_path = max(all_dbs, key=lambda p: p.stat().st_mtime)
                        self.current_project_name = db_path.parent.name
                    else:
                        QMessageBox.warning(self, "Errore", "Nessun database trovato. Esegui prima una scansione.")
                        return
                else:
                    QMessageBox.warning(self, "Errore", "Nessun database trovato. Esegui prima una scansione.")
                    return

            # Ottieni parametri AI se abilitati
            ai_provider = None
            ai_api_key = None
            if self.ai_enabled_check.isChecked():
                ai_provider = self.ai_provider_combo.currentData()
                ai_api_key = self.ai_api_key_edit.text().strip()

                if not ai_api_key:
                    QMessageBox.warning(
                        self, "API Key Mancante",
                        "Hai abilitato l'AI ma non hai inserito la API Key.\n"
                        "Verrà usata la generazione template standard."
                    )
                    ai_provider = None
                    ai_api_key = None
                else:
                    self._log_message("INFO", f"🤖 Generazione AI attivata con provider: {ai_provider}")

            # Crea dialog progress con cancel
            from PySide6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Generazione fix in corso...", "Annulla", 0, 0, self)
            progress.setWindowTitle("Generazione Fix Suggeriti")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)

            # Thread per generazione asincrona
            from PySide6.QtCore import QThread

            class FixGeneratorThread(QThread):
                def __init__(self, db_path, ai_provider, ai_api_key):
                    super().__init__()
                    self.db_path = db_path
                    self.ai_provider = ai_provider
                    self.ai_api_key = ai_api_key
                    self.fixes = []
                    self.error = None

                def run(self):
                    try:
                        from ..core.fixer import SEOFixer
                        import asyncio

                        fixer = SEOFixer(self.db_path, ai_provider=self.ai_provider, ai_api_key=self.ai_api_key)

                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            self.fixes = loop.run_until_complete(fixer.generate_all_fixes())
                            loop.run_until_complete(fixer.save_fixes_to_db(self.fixes))
                        finally:
                            loop.close()
                    except Exception as e:
                        self.error = str(e)

            thread = FixGeneratorThread(db_path, ai_provider, ai_api_key)

            # Update progress message periodically
            def update_progress():
                if thread.isRunning():
                    dots = "." * ((progress.value() % 3) + 1)
                    progress.setLabelText(f"Generazione fix in corso{dots}\n\n"
                                        f"Questa operazione può richiedere alcuni secondi...")
                    progress.setValue(progress.value() + 1)

            from PySide6.QtCore import QTimer
            timer = QTimer()
            timer.timeout.connect(update_progress)
            timer.start(500)  # Update ogni 500ms

            thread.start()

            # Wait for thread con progress
            while thread.isRunning():
                QApplication.processEvents()
                if progress.wasCanceled():
                    thread.terminate()
                    thread.wait()
                    timer.stop()
                    return

            timer.stop()
            progress.close()

            # Check errori
            if thread.error:
                QMessageBox.critical(self, "Errore", f"Errore durante generazione fix: {thread.error}")
                return

            fixes = thread.fixes

            # Messaggio con info AI se usata
            ai_msg = ""
            if ai_provider and fixes:
                # Conta token totali se disponibile
                total_tokens = sum(
                    int(f.explanation.split('(')[-1].split(' token')[0])
                    for f in fixes
                    if 'token' in f.explanation
                )
                if total_tokens > 0:
                    ai_msg = f"\n\n🤖 AI usata: {ai_provider}\n💰 Token consumati: ~{total_tokens}"

            QMessageBox.information(
                self, "Completato",
                f"✅ Generati {len(fixes)} fix suggeriti!{ai_msg}\n\nVisualizza la tabella nella tab 'Fix Suggeriti'."
            )

            # Carica fix nella tabella
            self._load_fixes()

            # Switch to fixes tab
            self.tab_widget.setCurrentIndex(3)  # Tab Fix Suggeriti

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante generazione fix: {str(e)}")

    def _load_fixes(self):
        """Carica fix dal database e popola tabella"""
        try:
            # Usa stesso path di _generate_fixes
            project_name = getattr(self, 'current_project_name', None) or self.project_edit.text()
            db_path = Path.home() / ".pyprestascan" / project_name / "crawl.db"

            # Se non esiste, cerca il più recente
            if not db_path.exists():
                base_dir = Path.home() / ".pyprestascan"
                if base_dir.exists():
                    all_dbs = list(base_dir.glob("*/crawl.db"))
                    if all_dbs:
                        db_path = max(all_dbs, key=lambda p: p.stat().st_mtime)
                    else:
                        return
                else:
                    return

            from ..core.storage import CrawlDatabase
            import asyncio

            db = CrawlDatabase(db_path)

            # Carica fix
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                fixes = loop.run_until_complete(db.get_all_fixes())
                stats = loop.run_until_complete(db.get_fix_stats())
            finally:
                loop.close()

            # Salva per filtraggio
            self.all_fixes_data = fixes

            # Aggiorna statistiche
            self.total_fixes_label.setText(f"Totale fix: {len(fixes)}")
            self.pending_fixes_label.setText(f"Pending: {stats['by_status'].get('PENDING', 0)}")
            self.automated_fixes_label.setText(f"Automatizzabili: {stats['automated_pending']}")
            self.avg_confidence_label.setText(f"Confidence media: {stats['avg_confidence']*100:.1f}%")

            # Popola tabella
            self._populate_fixes_table(fixes)

        except Exception as e:
            self._log_message("ERROR", f"Errore caricamento fix: {e}")

    def _populate_fixes_table(self, fixes):
        """Popola tabella fix"""
        self.fixes_table.setRowCount(0)

        for fix in fixes:
            row = self.fixes_table.rowCount()
            self.fixes_table.insertRow(row)

            # ID (abbreviato)
            self.fixes_table.setItem(row, 0, QTableWidgetItem(fix.fix_id[:8]))

            # Pagina (accorcia URL)
            page_url = fix.page_url
            if len(page_url) > 50:
                page_url = page_url[:47] + "..."
            self.fixes_table.setItem(row, 1, QTableWidgetItem(page_url))

            # Tipo
            self.fixes_table.setItem(row, 2, QTableWidgetItem(fix.fix_type))

            # Severity con emoji
            severity_map = {
                'CRITICAL': '🔴 CRITICAL',
                'WARNING': '🟡 WARNING',
                'INFO': '🔵 INFO'
            }
            severity_item = QTableWidgetItem(severity_map.get(fix.severity, fix.severity))
            self.fixes_table.setItem(row, 3, severity_item)

            # Valore attuale (troncato)
            current = fix.current_value[:50] if fix.current_value else "(vuoto)"
            self.fixes_table.setItem(row, 4, QTableWidgetItem(current))

            # Valore suggerito (troncato)
            suggested = fix.suggested_value[:50]
            self.fixes_table.setItem(row, 5, QTableWidgetItem(suggested))

            # Confidence con colore
            confidence_pct = f"{fix.confidence*100:.0f}%"
            confidence_item = QTableWidgetItem(confidence_pct)

            # Colora based on confidence
            if fix.confidence >= 0.8:
                confidence_item.setForeground(QColor("#4CAF50"))  # Verde
            elif fix.confidence >= 0.6:
                confidence_item.setForeground(QColor("#FF9800"))  # Arancione
            else:
                confidence_item.setForeground(QColor("#F44336"))  # Rosso

            self.fixes_table.setItem(row, 6, confidence_item)

            # Automatizzabile
            auto_text = "✅ Sì" if fix.automated else "⚠️ No"
            self.fixes_table.setItem(row, 7, QTableWidgetItem(auto_text))

            # Bottone azioni
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)

            view_btn = QPushButton("👁️")
            view_btn.setToolTip("Visualizza dettagli")
            view_btn.setMaximumWidth(40)
            view_btn.clicked.connect(lambda checked, f=fix: self._show_fix_details(f))
            actions_layout.addWidget(view_btn)

            self.fixes_table.setCellWidget(row, 8, actions_widget)

    def _filter_fixes_table(self):
        """Filtra tabella fix in base a filtri selezionati"""
        if not hasattr(self, 'all_fixes_data'):
            return

        status_filter = self.fix_status_combo.currentText()
        type_filter = self.fix_type_combo.currentText()
        automated_only = self.show_automated_only.isChecked()

        filtered_fixes = []
        for fix in self.all_fixes_data:
            # Filtro status
            if status_filter != "Tutti" and fix.status != status_filter:
                continue

            # Filtro tipo
            if type_filter != "Tutti" and fix.fix_type != type_filter:
                continue

            # Filtro automatizzabili
            if automated_only and not fix.automated:
                continue

            filtered_fixes.append(fix)

        self._populate_fixes_table(filtered_fixes)

    def _show_fix_details(self, fix):
        """Mostra dialog con dettagli del fix"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Dettagli Fix - {fix.fix_id[:8]}")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(500)

        layout = QVBoxLayout(dialog)

        # Form con dettagli
        form_layout = QFormLayout()

        form_layout.addRow("Fix ID:", QLabel(fix.fix_id))
        form_layout.addRow("Issue Code:", QLabel(fix.issue_code))
        form_layout.addRow("Pagina URL:", QLabel(fix.page_url))
        form_layout.addRow("Tipo Fix:", QLabel(fix.fix_type))
        form_layout.addRow("Severity:", QLabel(fix.severity))
        form_layout.addRow("Confidence:", QLabel(f"{fix.confidence*100:.1f}%"))
        form_layout.addRow("Automatizzabile:", QLabel("Sì" if fix.automated else "No"))
        form_layout.addRow("Status:", QLabel(fix.status))

        layout.addLayout(form_layout)

        # Valore attuale
        current_group = QGroupBox("Valore Attuale")
        current_layout = QVBoxLayout(current_group)
        current_text = QTextEdit()
        current_text.setPlainText(fix.current_value or "(vuoto)")
        current_text.setReadOnly(True)
        current_text.setMaximumHeight(100)
        current_layout.addWidget(current_text)
        layout.addWidget(current_group)

        # Valore suggerito
        suggested_group = QGroupBox("Valore Suggerito")
        suggested_layout = QVBoxLayout(suggested_group)
        suggested_text = QTextEdit()
        suggested_text.setPlainText(fix.suggested_value)
        suggested_text.setReadOnly(True)
        suggested_text.setMaximumHeight(100)
        suggested_layout.addWidget(suggested_text)
        layout.addWidget(suggested_group)

        # Spiegazione
        explanation_group = QGroupBox("Spiegazione")
        explanation_layout = QVBoxLayout(explanation_group)
        explanation_text = QTextEdit()
        explanation_text.setPlainText(fix.explanation)
        explanation_text.setReadOnly(True)
        explanation_text.setMaximumHeight(80)
        explanation_layout.addWidget(explanation_text)
        layout.addWidget(explanation_group)

        # SQL Query (se presente)
        if fix.sql_query:
            sql_group = QGroupBox("Query SQL")
            sql_layout = QVBoxLayout(sql_group)
            sql_text = QTextEdit()
            sql_text.setPlainText(fix.sql_query)
            sql_text.setReadOnly(True)
            sql_text.setMaximumHeight(120)
            sql_layout.addWidget(sql_text)
            layout.addWidget(sql_group)

        # Bottoni
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec()

    def _export_fixes_csv(self):
        """Esporta fix in formato CSV"""
        if not hasattr(self, 'all_fixes_data') or not self.all_fixes_data:
            QMessageBox.information(self, "Nessun dato", "Non ci sono fix da esportare")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Esporta Fix CSV",
            f"fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "File CSV (*.csv)"
        )

        if not filename:
            return

        try:
            import csv

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow([
                    'Fix ID', 'Issue Code', 'Page URL', 'Fix Type', 'Severity',
                    'Current Value', 'Suggested Value', 'Confidence', 'Automated',
                    'Status', 'Explanation'
                ])

                # Data
                for fix in self.all_fixes_data:
                    writer.writerow([
                        fix.fix_id,
                        fix.issue_code,
                        fix.page_url,
                        fix.fix_type,
                        fix.severity,
                        fix.current_value or "",
                        fix.suggested_value,
                        f"{fix.confidence:.2f}",
                        "Yes" if fix.automated else "No",
                        fix.status,
                        fix.explanation
                    ])

            QMessageBox.information(
                self, "Completato",
                f"Fix esportati con successo in:\n{filename}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante export CSV: {str(e)}")

    def _export_fixes_sql(self):
        """Esporta fix in formato SQL"""
        if not hasattr(self, 'all_fixes_data') or not self.all_fixes_data:
            QMessageBox.information(self, "Nessun dato", "Non ci sono fix da esportare")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Esporta Fix SQL",
            f"fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
            "File SQL (*.sql)"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("-- SQL Fix Script generato da PyPrestaScan\n")
                f.write(f"-- Generato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- Totale fix: {len(self.all_fixes_data)}\n\n")
                f.write("-- IMPORTANTE: Fai backup del database prima di eseguire!\n\n")

                count = 0
                for fix in self.all_fixes_data:
                    if fix.sql_query and fix.automated and fix.status == 'PENDING':
                        f.write(f"\n-- Fix ID: {fix.fix_id}\n")
                        f.write(f"-- Pagina: {fix.page_url}\n")
                        f.write(f"-- Tipo: {fix.fix_type}\n")
                        f.write(f"-- Confidence: {fix.confidence:.2f}\n")
                        f.write(fix.sql_query)
                        f.write("\n")
                        count += 1

            QMessageBox.information(
                self, "Completato",
                f"{count} fix automatizzabili esportati in SQL:\n{filename}\n\n"
                "⚠️ ATTENZIONE: Esegui SEMPRE un backup prima di applicare queste query!"
            )

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante export SQL: {str(e)}")

    def _show_about(self):
        """Mostra dialog about"""
        QMessageBox.about(self, "Info su PyPrestaScan",
            """
            <h2>PyPrestaScan v1.5.0</h2>
            <p>CLI per analisi SEO specializzata di e-commerce PrestaShop con AI-powered fix</p>

            <p><b>Caratteristiche:</b></p>
            <ul>
            <li>🚀 Crawling asincrono scalabile</li>
            <li>🤖 Fix AI con DeepSeek/GPT/Claude</li>
            <li>🎯 Euristiche PrestaShop specifiche</li>
            <li>📊 Report CSV, JSON e HTML</li>
            <li>🔄 Resume per sessioni lunghe</li>
            <li>🌐 Supporto multilingua</li>
            </ul>
            
            <p><b>Sviluppato con:</b><br>
            Python 3.11+, PySide6, asyncio, httpx</p>
            
            <p><b>Licenza:</b> MIT</p>
            """)
    
    def _open_docs(self):
        """Apre documentazione online"""
        webbrowser.open("https://github.com/pyprestascan/pyprestascan")

    def _toggle_theme(self):
        """Toggle tra Light e Dark mode"""
        new_theme = self.theme_manager.toggle_theme()
        self.theme_toggle_btn.setText(self.theme_manager.get_icon_for_theme())
        self._log_message("INFO", f"🎨 Tema cambiato in: {new_theme.capitalize()} Mode")

    def _change_language(self, index):
        """Cambia lingua interfaccia"""
        if index < 0:
            return

        lang_code = self.language_combo.itemData(index)
        if lang_code == self.translation_manager.get_current_language():
            return  # Stessa lingua, non fare nulla

        # Cambia lingua
        self.translation_manager.set_language(lang_code)

        # Log cambio lingua
        lang_name = self.translation_manager.get_language_name(lang_code)
        self._log_message("INFO", f"🌐 Language changed to: {lang_name}")

        # Mostra dialog per riavvio
        QMessageBox.information(
            self,
            "Language Changed / Lingua Cambiata",
            "Please restart the application to apply the new language.\n"
            "Riavvia l'applicazione per applicare la nuova lingua.\n\n"
            "Por favor, reinicia la aplicación para aplicar el nuevo idioma."
        )

    def closeEvent(self, event):
        """Gestisce chiusura applicazione"""
        # Ferma crawling se in corso
        if self.is_crawling:
            reply = QMessageBox.question(
                self, 
                "Conferma chiusura",
                "Scansione in corso. Vuoi interromperla e chiudere?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
            
            # Ferma crawling
            self._stop_crawl()
        
        # Salva impostazioni
        self._save_settings()
        
        # Chiude
        event.accept()


def main():
    """Entry point GUI"""
    app = QApplication(sys.argv)
    
    # Configura applicazione
    app.setApplicationName("PyPrestaScan")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PyPrestaScan")
    
    # Stile applicazione
    app.setStyle("Fusion")

    # Crea e mostra finestra principale
    window = MainWindow(app)
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())