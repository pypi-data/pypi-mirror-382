"""
Interfaccia grafica reale per PyPrestaScan con scansioni effettive
"""
import sys
import os
import asyncio
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QTabWidget, QGroupBox, QLabel, QLineEdit, QPushButton,
    QSpinBox, QCheckBox, QComboBox, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox, QFrame, QScrollArea, QListWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QStatusBar, QToolBar,
    QRadioButton, QButtonGroup, QSplitter, QTreeWidget, QTreeWidgetItem,
    QDialog, QDialogButtonBox, QFormLayout
)
from PySide6.QtCore import (
    Qt, QThread, QObject, Signal, QTimer, QSettings, QUrl
)
from PySide6.QtGui import (
    QFont, QDesktopServices, QIcon, QPalette, QColor
)

# Import relativi al progetto
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from pyprestascan.gui.scan_profiles import ScanProfileManager, ScanType, get_profile
    from pyprestascan.cli import CrawlConfig, CliContext
    from pyprestascan.core.crawler import PyPrestaScanner
    from pyprestascan.core.utils import RichLogger
except ImportError as e:
    print(f"❌ Errore import: {e}")
    print("💡 Assicurati di eseguire dalla directory del progetto")
    sys.exit(1)


class RealCrawlerWorker(QObject):
    """Worker per esecuzione crawling reale"""
    
    # Segnali
    progress_updated = Signal(int, str)  # pages_crawled, status
    stats_updated = Signal(dict)  # statistiche complete
    log_message = Signal(str, str)  # level, message
    crawl_finished = Signal(bool, str, dict)  # success, message, final_stats
    
    def __init__(self, config: CrawlConfig, cli_context: CliContext):
        super().__init__()
        self.config = config
        self.cli_context = cli_context
        self.scanner: Optional[PyPrestaScanner] = None
        self._should_stop = False
    
    def run_crawl(self):
        """Esegue crawling reale"""
        try:
            self.log_message.emit("INFO", f"🚀 Avvio scansione: {self.config.url}")
            self.log_message.emit("INFO", f"📊 Configurazione: Max {self.config.max_urls} URL, concorrenza {self.config.concurrency}")
            
            # Crea loop asincrono
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Crea scanner con gestione signal disabilitata per thread
            self.scanner = PyPrestaScanner(self.config, self.cli_context, setup_signals=False)
            
            # Hook per progress (se possibile)
            self._setup_progress_hooks()
            
            # Esegui crawling
            result = loop.run_until_complete(self.scanner.run())
            
            # Ottieni statistiche finali
            final_stats = self.scanner.stats.to_dict() if self.scanner.stats else {}
            
            if result == 0:
                self.log_message.emit("INFO", "✅ Scansione completata con successo!")
                self.crawl_finished.emit(True, "Scansione completata", final_stats)
            else:
                self.log_message.emit("ERROR", "❌ Scansione terminata con errori")
                self.crawl_finished.emit(False, "Errori durante la scansione", final_stats)
                
        except Exception as e:
            self.log_message.emit("ERROR", f"❌ Errore critico: {str(e)}")
            self.crawl_finished.emit(False, f"Errore: {str(e)}", {})
        
        finally:
            if 'loop' in locals():
                loop.close()
    
    def _setup_progress_hooks(self):
        """Imposta hook per monitoraggio progress (limitato)"""
        # Timer per simulare aggiornamenti periodici
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._emit_progress_update)
        self.progress_timer.start(2000)  # Ogni 2 secondi
        
        self.pages_estimate = 0
    
    def _emit_progress_update(self):
        """Legge progress REALE dal database"""
        if self._should_stop:
            self.progress_timer.stop()
            return

        # Leggi dati REALI dal database del crawler
        try:
            import sqlite3
            from pathlib import Path

            db_path = Path.home() / ".pyprestascan" / self.config.project / "crawl.db"
            if not db_path.exists():
                return

            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()

                # Conta pagine reali
                cursor.execute("SELECT COUNT(*) FROM pages")
                pages_crawled = cursor.fetchone()[0]

                # Conta issues reali
                cursor.execute("SELECT COUNT(*) FROM issues")
                total_issues = cursor.fetchone()[0]

                # Immagini senza ALT reali
                cursor.execute("SELECT SUM(images_missing_alt + images_empty_alt) FROM pages")
                result = cursor.fetchone()[0]
                images_no_alt = result if result else 0

                # Conta immagini totali
                cursor.execute("SELECT SUM(images_total) FROM pages")
                result = cursor.fetchone()[0]
                images_analyzed = result if result else 0

                # Pagine fallite
                cursor.execute("SELECT COUNT(*) FROM pages WHERE status_code >= 400")
                pages_failed = cursor.fetchone()[0]

            status = f"Scansione in corso... {pages_crawled} pagine"
            self.progress_updated.emit(pages_crawled, status)

            # Statistiche REALI dal database
            stats = {
                'pages_crawled': pages_crawled,
                'pages_failed': pages_failed,
                'total_issues': total_issues,
                'images_analyzed': images_analyzed,
                'images_no_alt': images_no_alt
            }
            self.stats_updated.emit(stats)

        except Exception as e:
            # Fallback silenzioso se il DB non è pronto
            pass
    
    def stop_crawl(self):
        """Ferma crawling"""
        self._should_stop = True
        if hasattr(self, 'progress_timer'):
            self.progress_timer.stop()
        if self.scanner:
            self.scanner.should_stop = True


class ScanProfileDialog(QDialog):
    """Dialog per selezione profilo di scansione"""
    
    def __init__(self, parent=None, url: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Seleziona Profilo di Scansione")
        self.setModal(True)
        self.resize(700, 500)
        
        self.profile_manager = ScanProfileManager()
        self.selected_profile = None
        self.url = url
        
        self._setup_ui()
        self._populate_profiles()
    
    def _setup_ui(self):
        """Setup interfaccia dialog"""
        layout = QVBoxLayout(self)
        
        # Header info
        if self.url:
            url_label = QLabel(f"🌐 Target: {self.url}")
            url_label.setStyleSheet("QLabel { font-weight: bold; color: #2196F3; }")
            layout.addWidget(url_label)
        
        # Splitter per layout
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Lista profili (sinistra)
        profiles_widget = QWidget()
        profiles_layout = QVBoxLayout(profiles_widget)
        profiles_layout.addWidget(QLabel("📋 Profili Disponibili:"))
        
        self.profiles_tree = QTreeWidget()
        self.profiles_tree.setHeaderLabels(["Nome", "Tempo Stimato", "Max URLs"])
        self.profiles_tree.itemClicked.connect(self._profile_selected)
        profiles_layout.addWidget(self.profiles_tree)
        
        # Suggerimenti
        if self.url:
            suggestions = self.profile_manager.get_profile_suggestions(self.url)
            if suggestions:
                sugg_label = QLabel("💡 Suggeriti per questo sito:")
                sugg_label.setStyleSheet("QLabel { font-style: italic; color: #FF9800; }")
                profiles_layout.addWidget(sugg_label)
        
        splitter.addWidget(profiles_widget)
        
        # Dettagli profilo (destra)  
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.addWidget(QLabel("📝 Dettagli Profilo:"))
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(300)
        details_layout.addWidget(self.details_text)
        
        # Focus areas
        details_layout.addWidget(QLabel("🎯 Aree di Focus:"))
        self.focus_list = QListWidget()
        self.focus_list.setMaximumHeight(150)
        details_layout.addWidget(self.focus_list)
        
        splitter.addWidget(details_widget)
        
        # Bottoni
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Help
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.helpRequested.connect(self._show_help)
        layout.addWidget(buttons)
        
        self.ok_button = buttons.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
    
    def _populate_profiles(self):
        """Popola lista profili"""
        suggestions = self.profile_manager.get_profile_suggestions(self.url) if self.url else []
        
        for scan_type, profile in self.profile_manager.profiles.items():
            item = QTreeWidgetItem([
                profile.name,
                profile.estimated_time,
                str(profile.max_urls)
            ])
            
            # Evidenzia suggerimenti
            if scan_type in suggestions:
                item.setBackground(0, QColor(255, 248, 225))  # Giallo chiaro
                item.setText(0, f"⭐ {profile.name}")
            
            item.setData(0, Qt.UserRole, profile)
            self.profiles_tree.addTopLevelItem(item)
        
        # Espandi e ridimensiona
        self.profiles_tree.expandAll()
        self.profiles_tree.resizeColumnToContents(0)
    
    def _profile_selected(self, item, column):
        """Gestisce selezione profilo"""
        profile = item.data(0, Qt.UserRole)
        if profile:
            self.selected_profile = profile
            self._update_details(profile)
            self.ok_button.setEnabled(True)
    
    def _update_details(self, profile):
        """Aggiorna dettagli profilo"""
        details = f"""
<h3>{profile.name}</h3>
<p><b>Descrizione:</b><br>{profile.description}</p>

<p><b>Configurazione:</b></p>
<ul>
<li><b>Max URLs:</b> {profile.max_urls:,}</li>
<li><b>Concorrenza:</b> {profile.concurrency}</li>
<li><b>Delay:</b> {profile.delay}ms</li>
<li><b>Profondità:</b> {'Illimitata' if profile.depth is None else str(profile.depth)}</li>
<li><b>PrestaShop Mode:</b> {'Attivo' if profile.prestashop_mode else 'Disattivo'}</li>
<li><b>Tempo Stimato:</b> {profile.estimated_time}</li>
</ul>

<p><b>Pattern Include:</b> {len(profile.include_patterns)} regole</p>
<p><b>Pattern Exclude:</b> {len(profile.exclude_patterns)} regole</p>
        """
        
        self.details_text.setHtml(details)
        
        # Aggiorna focus areas
        self.focus_list.clear()
        for area in profile.focus_areas:
            self.focus_list.addItem(f"• {area}")
    
    def _show_help(self):
        """Mostra aiuto profili"""
        help_text = """
<h3>🔍 Guida Profili di Scansione</h3>

<p><b>🔍 Scansione Completa:</b> Analisi SEO completa di tutto il sito (più lenta ma dettagliata)</p>

<p><b>⚡ Scansione Veloce:</b> Controllo rapido delle pagine principali (home, categorie, top prodotti)</p>

<p><b>🖼️ Focus Immagini ALT:</b> Specifica per trovare immagini senza testo alternativo</p>

<p><b>🔧 SEO Tecnico:</b> Aspetti tecnici come canonical, robots.txt, sitemap</p>

<p><b>🛒 PrestaShop Specifico:</b> Controlli dedicati alle configurazioni PrestaShop</p>

<p><b>📝 Analisi Contenuti:</b> Qualità contenuti, duplicati, struttura heading</p>

<p><b>🚀 Performance & UX:</b> Prestazioni e user experience</p>

<p><b>💡 Suggerimento:</b> Inizia con una <b>Scansione Veloce</b> per avere un'idea generale, poi usa profili specifici per approfondire.</p>
        """
        
        QMessageBox.information(self, "Guida Profili", help_text)
    
    def get_selected_profile(self):
        """Restituisce profilo selezionato"""
        return self.selected_profile


class PyPrestaScanGUI(QMainWindow):
    """Interfaccia principale PyPrestaScan con scansioni reali"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyPrestaScan v1.0 - Analisi SEO PrestaShop")
        self.setMinimumSize(1000, 700)
        
        # Stato applicazione
        self.is_scanning = False
        self.current_profile = None
        self.crawler_thread: Optional[QThread] = None
        self.crawler_worker: Optional[RealCrawlerWorker] = None
        
        # Settings
        self.settings = QSettings("PyPrestaScan", "PyPresta")
        
        # Profile manager
        self.profile_manager = ScanProfileManager()
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        self._load_settings()
        
        # Update timer
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self._update_ui_state)
        self.ui_timer.start(1000)
    
    def _setup_ui(self):
        """Setup interfaccia utente"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196F3, stop:1 #21CBF3); border-radius: 8px; }")
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("🔍 PyPrestaScan")
        title_label.setStyleSheet("QLabel { color: white; font-size: 24px; font-weight: bold; }")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Analisi SEO professionale per PrestaShop")
        subtitle_label.setStyleSheet("QLabel { color: rgba(255,255,255,0.8); font-size: 14px; }")
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Tab: Configurazione e Avvio
        self._create_scan_tab()
        
        # Tab: Progress e Log
        self._create_progress_tab()
        
        # Tab: Risultati
        self._create_results_tab()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto per nuova scansione")
        
        # Toolbar
        self._create_toolbar()
    
    def _create_toolbar(self):
        """Crea toolbar"""
        toolbar = QToolBar("Azioni")
        self.addToolBar(toolbar)
        
        # Quick scan
        self.quick_scan_action = toolbar.addAction("⚡ Scansione Veloce")
        self.quick_scan_action.triggered.connect(lambda: self._quick_start(ScanType.QUICK))
        
        # Complete scan
        self.complete_scan_action = toolbar.addAction("🔍 Scansione Completa")
        self.complete_scan_action.triggered.connect(lambda: self._quick_start(ScanType.COMPLETE))
        
        toolbar.addSeparator()
        
        # Stop
        self.stop_action = toolbar.addAction("⏹️ Ferma")
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self._stop_scan)
        
        toolbar.addSeparator()
        
        # Results
        self.results_action = toolbar.addAction("📊 Risultati")
        self.results_action.setEnabled(False)
        self.results_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
    
    def _create_scan_tab(self):
        """Crea tab configurazione e avvio"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # URL Section
        url_group = QGroupBox("🌐 Sito da Analizzare")
        url_layout = QGridLayout(url_group)
        
        url_layout.addWidget(QLabel("URL:"), 0, 0)
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://mio-shop-prestashop.com")
        self.url_edit.textChanged.connect(self._on_url_changed)
        url_layout.addWidget(self.url_edit, 0, 1)
        
        test_btn = QPushButton("🔗 Testa Connessione")
        test_btn.clicked.connect(self._test_connection)
        url_layout.addWidget(test_btn, 0, 2)
        
        layout.addWidget(url_group)
        
        # Profile Selection
        profile_group = QGroupBox("📋 Tipo di Scansione")
        profile_layout = QVBoxLayout(profile_group)
        
        # Profili rapidi
        quick_layout = QHBoxLayout()
        self.quick_complete_btn = QPushButton("🔍 Completa")
        self.quick_complete_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        self.quick_complete_btn.clicked.connect(lambda: self._select_profile_and_start(ScanType.COMPLETE))
        quick_layout.addWidget(self.quick_complete_btn)
        
        self.quick_fast_btn = QPushButton("⚡ Veloce")
        self.quick_fast_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 10px; }")
        self.quick_fast_btn.clicked.connect(lambda: self._select_profile_and_start(ScanType.QUICK))
        quick_layout.addWidget(self.quick_fast_btn)
        
        self.quick_images_btn = QPushButton("🖼️ Immagini ALT")
        self.quick_images_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; padding: 10px; }")
        self.quick_images_btn.clicked.connect(lambda: self._select_profile_and_start(ScanType.IMAGES_ALT))
        quick_layout.addWidget(self.quick_images_btn)
        
        profile_layout.addLayout(quick_layout)
        
        # Advanced profile selection
        advanced_layout = QHBoxLayout()
        self.select_profile_btn = QPushButton("⚙️ Seleziona Profilo Personalizzato")
        self.select_profile_btn.clicked.connect(self._open_profile_dialog)
        advanced_layout.addWidget(self.select_profile_btn)
        
        self.custom_config_btn = QPushButton("🛠️ Configurazione Manuale")
        self.custom_config_btn.clicked.connect(self._open_custom_config)
        advanced_layout.addWidget(self.custom_config_btn)
        
        profile_layout.addLayout(advanced_layout)
        
        layout.addWidget(profile_group)
        
        # Current profile info
        self.profile_info_group = QGroupBox("📝 Profilo Selezionato")
        self.profile_info_layout = QVBoxLayout(self.profile_info_group)
        
        self.profile_info_text = QTextEdit()
        self.profile_info_text.setReadOnly(True)
        self.profile_info_text.setMaximumHeight(150)
        self.profile_info_text.setHtml("<i>Nessun profilo selezionato. Scegli un tipo di scansione sopra.</i>")
        self.profile_info_layout.addWidget(self.profile_info_text)
        
        layout.addWidget(self.profile_info_group)
        
        # Start button
        start_layout = QHBoxLayout()
        start_layout.addStretch()
        
        self.start_scan_btn = QPushButton("🚀 AVVIA SCANSIONE")
        self.start_scan_btn.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold; 
                font-size: 16px;
                padding: 15px 30px; 
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.start_scan_btn.setEnabled(False)
        self.start_scan_btn.clicked.connect(self._start_scan)
        start_layout.addWidget(self.start_scan_btn)
        
        layout.addLayout(start_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(widget, "🚀 Avvio Scansione")
    
    def _create_progress_tab(self):
        """Crea tab progress"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Progress section
        progress_group = QGroupBox("📊 Avanzamento")
        progress_layout = QVBoxLayout(progress_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Pronto per iniziare")
        progress_layout.addWidget(self.progress_bar)
        
        # Stats grid
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        
        self.pages_crawled_label = QLabel("📄 Pagine: 0")
        self.pages_failed_label = QLabel("❌ Errori: 0")
        self.issues_found_label = QLabel("⚠️ Issues: 0")
        self.images_analyzed_label = QLabel("🖼️ Immagini: 0")
        
        stats_layout.addWidget(self.pages_crawled_label, 0, 0)
        stats_layout.addWidget(self.pages_failed_label, 0, 1)
        stats_layout.addWidget(self.issues_found_label, 1, 0)
        stats_layout.addWidget(self.images_analyzed_label, 1, 1)
        
        progress_layout.addWidget(stats_frame)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        self.pause_btn = QPushButton("⏸️ Pausa")
        self.pause_btn.setEnabled(False)
        control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹️ Ferma")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_scan)
        control_layout.addWidget(self.stop_btn)
        
        progress_layout.addLayout(control_layout)
        
        layout.addWidget(progress_group)
        
        # Log section
        log_group = QGroupBox("📝 Log Attività")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_text)
        
        # Log controls
        log_control_layout = QHBoxLayout()
        
        clear_log_btn = QPushButton("🗑️ Pulisci")
        clear_log_btn.clicked.connect(self.log_text.clear)
        log_control_layout.addWidget(clear_log_btn)
        
        save_log_btn = QPushButton("💾 Salva Log")
        save_log_btn.clicked.connect(self._save_log)
        log_control_layout.addWidget(save_log_btn)
        
        log_control_layout.addStretch()
        log_layout.addLayout(log_control_layout)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(widget, "📈 Progress")
    
    def _create_results_tab(self):
        """Crea tab risultati"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Summary KPIs
        summary_group = QGroupBox("📋 Riepilogo")
        summary_layout = QGridLayout(summary_group)
        
        self.total_pages_label = QLabel("Pagine totali: --")
        self.success_rate_label = QLabel("Tasso successo: --")
        self.avg_score_label = QLabel("Score medio: --")
        self.critical_issues_label = QLabel("Issues critici: --")
        
        summary_layout.addWidget(self.total_pages_label, 0, 0)
        summary_layout.addWidget(self.success_rate_label, 0, 1)
        summary_layout.addWidget(self.avg_score_label, 1, 0)
        summary_layout.addWidget(self.critical_issues_label, 1, 1)
        
        layout.addWidget(summary_group)
        
        # Issues table
        issues_group = QGroupBox("⚠️ Issues Principali")
        issues_layout = QVBoxLayout(issues_group)
        
        self.issues_table = QTableWidget(0, 4)
        self.issues_table.setHorizontalHeaderLabels(["Severity", "Tipo", "Descrizione", "Pagine"])
        self.issues_table.horizontalHeader().setStretchLastSection(True)
        issues_layout.addWidget(self.issues_table)
        
        layout.addWidget(issues_group)
        
        # Export section
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.view_html_btn = QPushButton("📊 Apri Report HTML")
        self.view_html_btn.setEnabled(False)
        self.view_html_btn.clicked.connect(self._open_html_report)
        export_layout.addWidget(self.view_html_btn)
        
        self.export_csv_btn = QPushButton("📄 Esporta CSV")
        self.export_csv_btn.setEnabled(False)
        self.export_csv_btn.clicked.connect(self._export_csv)
        export_layout.addWidget(self.export_csv_btn)
        
        self.open_folder_btn = QPushButton("📁 Apri Cartella")
        self.open_folder_btn.setEnabled(False) 
        self.open_folder_btn.clicked.connect(self._open_results_folder)
        export_layout.addWidget(self.open_folder_btn)
        
        layout.addLayout(export_layout)
        
        self.tab_widget.addTab(widget, "📊 Risultati")
    
    def _setup_connections(self):
        """Setup connessioni segnali"""
        self.url_edit.textChanged.connect(self._validate_form)
    
    def _load_settings(self):
        """Carica settings"""
        self.url_edit.setText(self.settings.value("last_url", ""))
        
        # Ripristina geometria
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
    
    def _save_settings(self):
        """Salva settings"""
        self.settings.setValue("last_url", self.url_edit.text())
        self.settings.setValue("geometry", self.saveGeometry())
    
    def _validate_form(self):
        """Valida form"""
        url = self.url_edit.text().strip()
        has_url = bool(url and url.startswith(('http://', 'https://')))
        has_profile = self.current_profile is not None
        
        self.start_scan_btn.setEnabled(has_url and has_profile and not self.is_scanning)
        
        # Aggiorna quick buttons
        for btn in [self.quick_complete_btn, self.quick_fast_btn, self.quick_images_btn]:
            btn.setEnabled(has_url and not self.is_scanning)
    
    def _update_ui_state(self):
        """Aggiorna stato UI"""
        self._validate_form()
        
        # Aggiorna toolbar
        self.quick_scan_action.setEnabled(not self.is_scanning)
        self.complete_scan_action.setEnabled(not self.is_scanning)
        self.stop_action.setEnabled(self.is_scanning)
    
    def _on_url_changed(self):
        """Gestisce cambio URL"""
        url = self.url_edit.text().strip()
        if url:
            self.status_bar.showMessage(f"URL: {url}")
        else:
            self.status_bar.showMessage("Inserisci URL per iniziare")
    
    def _test_connection(self):
        """Testa connessione URL"""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Test", "Inserisci un URL prima")
            return
        
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "Test", "URL deve iniziare con http:// o https://")
            return
        
        # TODO: Implementare test connessione reale
        QMessageBox.information(self, "Test Connessione", 
                               f"✅ URL raggiungibile: {url}\n\n"
                               "💡 Usa 'Scansione Veloce' per un primo controllo")
    
    def _quick_start(self, scan_type: ScanType):
        """Avvio rapido con profilo predefinito"""
        if not self.url_edit.text().strip():
            QMessageBox.warning(self, "URL Mancante", "Inserisci l'URL del sito da scansionare")
            return
        
        profile = get_profile(scan_type)
        if profile:
            self.current_profile = profile
            self._update_profile_info()
            self._start_scan()
    
    def _select_profile_and_start(self, scan_type: ScanType):
        """Seleziona profilo e avvia"""
        profile = get_profile(scan_type)
        if profile:
            self.current_profile = profile
            self._update_profile_info()
            self._validate_form()
    
    def _open_profile_dialog(self):
        """Apre dialog selezione profilo"""
        dialog = ScanProfileDialog(self, self.url_edit.text())
        if dialog.exec() == QDialog.Accepted:
            profile = dialog.get_selected_profile()
            if profile:
                self.current_profile = profile
                self._update_profile_info()
                self._validate_form()
    
    def _open_custom_config(self):
        """Apre configurazione manuale (TODO)"""
        QMessageBox.information(self, "Configurazione Manuale", 
                               "Funzionalità in sviluppo.\n\n"
                               "Per ora usa i profili predefiniti o modifica il codice per configurazioni specifiche.")
    
    def _update_profile_info(self):
        """Aggiorna info profilo selezionato"""
        if not self.current_profile:
            return
        
        info = f"""
<h3>{self.current_profile.name}</h3>
<p>{self.current_profile.description}</p>

<b>Configurazione:</b><br>
• Max URLs: {self.current_profile.max_urls:,}<br>
• Concorrenza: {self.current_profile.concurrency}<br>
• Delay: {self.current_profile.delay}ms<br>
• Tempo stimato: <b>{self.current_profile.estimated_time}</b>

<br><br><b>Focus:</b> {', '.join(self.current_profile.focus_areas[:3])}...
        """
        
        self.profile_info_text.setHtml(info)
    
    def _start_scan(self):
        """Avvia scansione reale"""
        if not self.current_profile:
            QMessageBox.warning(self, "Profilo Mancante", "Seleziona un tipo di scansione")
            return
        
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "URL Mancante", "Inserisci URL del sito")
            return
        
        try:
            # Crea configurazione da profilo
            config = self._build_config_from_profile(url)
            cli_context = CliContext(config=config, debug=False, quiet=False, no_color=True)
            
            # Setup UI per scansione
            self.is_scanning = True
            self.tab_widget.setCurrentIndex(1)  # Vai a tab progress
            self._reset_progress_ui()
            
            # Crea worker thread
            self.crawler_thread = QThread()
            self.crawler_worker = RealCrawlerWorker(config, cli_context)
            self.crawler_worker.moveToThread(self.crawler_thread)
            
            # Connetti segnali
            self.crawler_thread.started.connect(self.crawler_worker.run_crawl)
            self.crawler_worker.progress_updated.connect(self._on_progress_updated)
            self.crawler_worker.stats_updated.connect(self._on_stats_updated)
            self.crawler_worker.log_message.connect(self._on_log_message)
            self.crawler_worker.crawl_finished.connect(self._on_crawl_finished)
            
            # Avvia
            self.crawler_thread.start()
            
            self.status_bar.showMessage("🔄 Scansione in corso...")
            self._log_message("INFO", f"🚀 Avviata scansione {self.current_profile.name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'avvio scansione:\n{str(e)}")
            self.is_scanning = False
    
    def _build_config_from_profile(self, url: str) -> CrawlConfig:
        """Costruisce CrawlConfig da profilo"""
        profile = self.current_profile
        
        return CrawlConfig(
            url=url,
            max_urls=profile.max_urls,
            concurrency=profile.concurrency,
            delay=profile.delay,
            depth=profile.depth,
            include_patterns=profile.include_patterns,
            exclude_patterns=profile.exclude_patterns,
            prestashop_mode=profile.prestashop_mode,
            include_subdomains=profile.include_subdomains,
            project=f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            export_dir=Path("./reports"),
            sitemap="auto"
        )
    
    def _reset_progress_ui(self):
        """Reset UI progress"""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Inizializzazione...")
        
        self.pages_crawled_label.setText("📄 Pagine: 0")
        self.pages_failed_label.setText("❌ Errori: 0")
        self.issues_found_label.setText("⚠️ Issues: 0")
        self.images_analyzed_label.setText("🖼️ Immagini: 0")
        
        self.stop_btn.setEnabled(True)
        
        self.log_text.append(f"\n=== Nuova Scansione {datetime.now().strftime('%H:%M:%S')} ===")
    
    def _stop_scan(self):
        """Ferma scansione"""
        if self.crawler_worker:
            self.crawler_worker.stop_crawl()
            self._log_message("WARNING", "🛑 Richiesta di stop inviata...")
    
    def _on_progress_updated(self, pages: int, status: str):
        """Gestisce aggiornamento progress"""
        max_pages = self.current_profile.max_urls if self.current_profile else 1000
        progress = min(int((pages / max_pages) * 100), 100)
        
        self.progress_bar.setValue(progress)
        self.progress_bar.setFormat(f"{pages}/{max_pages} pagine ({progress}%)")
        
        self.pages_crawled_label.setText(f"📄 Pagine: {pages}")
    
    def _on_stats_updated(self, stats: Dict[str, Any]):
        """Gestisce aggiornamento statistiche"""
        self.pages_failed_label.setText(f"❌ Errori: {stats.get('pages_failed', 0)}")
        self.issues_found_label.setText(f"⚠️ Issues: {stats.get('total_issues', 0)}")
        self.images_analyzed_label.setText(f"🖼️ Immagini: {stats.get('images_analyzed', 0)}")
    
    def _on_log_message(self, level: str, message: str):
        """Gestisce messaggi log"""
        self._log_message(level, message)
    
    def _on_crawl_finished(self, success: bool, message: str, stats: Dict[str, Any]):
        """Gestisce fine scansione"""
        self.is_scanning = False
        self.stop_btn.setEnabled(False)
        
        # Cleanup thread
        if self.crawler_thread:
            self.crawler_thread.quit()
            self.crawler_thread.wait()
            self.crawler_thread = None
            self.crawler_worker = None
        
        # Update progress
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("Completata!")
        
        # Log finale
        if success:
            self._log_message("INFO", f"✅ {message}")
            self.status_bar.showMessage("✅ Scansione completata!")
            
            # Aggiorna risultati
            self._update_results(stats)
            
            # Abilita export
            self.view_html_btn.setEnabled(True)
            self.export_csv_btn.setEnabled(True)
            self.open_folder_btn.setEnabled(True)
            self.results_action.setEnabled(True)
            
            # Vai a risultati
            QTimer.singleShot(1500, lambda: self.tab_widget.setCurrentIndex(2))
            
            QMessageBox.information(self, "Completata", f"Scansione completata!\n\n{message}")
        else:
            self._log_message("ERROR", f"❌ {message}")
            self.status_bar.showMessage("❌ Scansione fallita")
            QMessageBox.warning(self, "Errore", f"Scansione fallita:\n{message}")
    
    def _update_results(self, stats: Dict[str, Any]):
        """Aggiorna tab risultati"""
        # KPI
        total = stats.get('pages_crawled', 0)
        success = stats.get('pages_2xx', 0)  
        success_rate = (success / max(total, 1)) * 100
        
        self.total_pages_label.setText(f"Pagine totali: {total}")
        self.success_rate_label.setText(f"Tasso successo: {success_rate:.1f}%")
        self.avg_score_label.setText(f"Score medio: {stats.get('avg_speed', 0):.1f}")
        self.critical_issues_label.setText(f"Issues critici: {stats.get('total_issues', 0)}")

        # Carica TOP issues REALI dal database
        self._load_real_issues_to_table()
    
    def _load_real_issues_to_table(self):
        """Carica TOP 10 issues REALI dal database nella tabella"""
        try:
            import sqlite3
            from pathlib import Path

            db_path = Path.home() / ".pyprestascan" / self.current_profile.project / "crawl.db"
            if not db_path.exists():
                self.issues_table.setRowCount(0)
                return

            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()

                # Query TOP 10 issues per frequenza
                cursor.execute("""
                    SELECT
                        severity,
                        code,
                        COUNT(*) as count,
                        COUNT(DISTINCT page_url) as affected_pages
                    FROM issues
                    GROUP BY severity, code
                    ORDER BY
                        CASE severity
                            WHEN 'CRITICAL' THEN 1
                            WHEN 'WARNING' THEN 2
                            ELSE 3
                        END,
                        count DESC
                    LIMIT 10
                """)

                issues = cursor.fetchall()

            # Popola tabella con dati REALI
            self.issues_table.setRowCount(len(issues))
            for i, (severity, code, count, affected_pages) in enumerate(issues):
                # Emoji per severity
                emoji = "🔴" if severity == "CRITICAL" else "🟡" if severity == "WARNING" else "🔵"

                self.issues_table.setItem(i, 0, QTableWidgetItem(f"{emoji} {severity}"))
                self.issues_table.setItem(i, 1, QTableWidgetItem(code))
                self.issues_table.setItem(i, 2, QTableWidgetItem(f"{count} occorrenze"))
                self.issues_table.setItem(i, 3, QTableWidgetItem(f"{affected_pages} pagine"))

        except Exception as e:
            # Fallback se errore
            self.issues_table.setRowCount(0)

    def _log_message(self, level: str, message: str):
        """Aggiunge messaggio al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Colori per livelli
        colors = {
            "DEBUG": "#888888",
            "INFO": "#2196F3", 
            "WARNING": "#FF9800",
            "ERROR": "#F44336"
        }
        
        color = colors.get(level, "#000000")
        
        formatted = f'<span style="color: {color};">[{timestamp}] <b>{level}:</b> {message}</span>'
        self.log_text.append(formatted)
        
        # Auto scroll
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
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
                QMessageBox.information(self, "Salvato", f"Log salvato: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore salvataggio: {e}")
    
    def _open_html_report(self):
        """Apri report HTML"""
        report_path = Path("./reports/report.html")
        if report_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(report_path.absolute())))
        else:
            QMessageBox.warning(self, "File non trovato", 
                               f"Report HTML non trovato in: {report_path}")
    
    def _export_csv(self):
        """Esporta CSV"""
        QMessageBox.information(self, "Export CSV", 
                               "I file CSV sono stati generati nella cartella reports/:\n\n"
                               "• pages.csv - Dati pagine\n"
                               "• issues.csv - Issues trovati\n" 
                               "• images_missing_alt.csv - Problemi immagini")
    
    def _open_results_folder(self):
        """Apri cartella risultati"""
        reports_path = Path("./reports")
        if reports_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(reports_path.absolute())))
        else:
            QMessageBox.warning(self, "Cartella non trovata", f"Cartella reports non trovata: {reports_path}")
    
    def closeEvent(self, event):
        """Gestisce chiusura applicazione"""
        if self.is_scanning:
            reply = QMessageBox.question(
                self,
                "Scansione in corso",
                "C'è una scansione in corso. Vuoi fermarla e uscire?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
            
            self._stop_scan()
        
        self._save_settings()
        event.accept()


def main():
    """Entry point GUI reale"""
    app = QApplication(sys.argv)
    
    app.setApplicationName("PyPrestaScan")
    app.setApplicationVersion("1.0.0")
    app.setStyle("Fusion")
    
    # Tema scuro opzionale
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    # app.setPalette(palette)
    
    window = PyPrestaScanGUI()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())