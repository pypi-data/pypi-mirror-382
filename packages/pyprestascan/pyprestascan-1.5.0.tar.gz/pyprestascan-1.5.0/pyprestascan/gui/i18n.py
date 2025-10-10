"""
Sistema di internazionalizzazione (i18n) per PyPrestaScan GUI
Supporto per Italiano, Inglese, Spagnolo
"""
from typing import Dict
from PySide6.QtCore import QSettings
import locale


class TranslationManager:
    """Gestione traduzioni multi-lingua"""

    # Dizionario completo traduzioni IT/EN/ES
    TRANSLATIONS = {
        # === HEADER ===
        "app_title": {
            "it": "PyPrestaScan - Analisi SEO PrestaShop",
            "en": "PyPrestaScan - PrestaShop SEO Analysis",
            "es": "PyPrestaScan - Análisis SEO PrestaShop"
        },
        "app_subtitle": {
            "it": "Analisi SEO PrestaShop",
            "en": "PrestaShop SEO Analysis",
            "es": "Análisis SEO PrestaShop"
        },

        # === TABS ===
        "tab_config": {
            "it": "⚙️ Configurazione",
            "en": "⚙️ Configuration",
            "es": "⚙️ Configuración"
        },
        "tab_progress": {
            "it": "📈 Progress & Log",
            "en": "📈 Progress & Log",
            "es": "📈 Progreso & Log"
        },
        "tab_results": {
            "it": "📊 Risultati",
            "en": "📊 Results",
            "es": "📊 Resultados"
        },
        "tab_fixes": {
            "it": "🔧 Fix Suggeriti",
            "en": "🔧 Suggested Fixes",
            "es": "🔧 Correcciones Sugeridas"
        },
        "tab_help": {
            "it": "❓ Aiuto",
            "en": "❓ Help",
            "es": "❓ Ayuda"
        },

        # === BUTTONS ===
        "btn_start_scan": {
            "it": "▶️ Avvia Scansione",
            "en": "▶️ Start Scan",
            "es": "▶️ Iniciar Escaneo"
        },
        "btn_stop_scan": {
            "it": "⏹️ Ferma Scansione",
            "en": "⏹️ Stop Scan",
            "es": "⏹️ Detener Escaneo"
        },
        "btn_export_excel": {
            "it": "📊 Esporta Report Excel",
            "en": "📊 Export Excel Report",
            "es": "📊 Exportar Informe Excel"
        },
        "btn_export_csv": {
            "it": "📥 Esporta Issues CSV",
            "en": "📥 Export Issues CSV",
            "es": "📥 Exportar Issues CSV"
        },
        "btn_view_report": {
            "it": "📊 Visualizza Report HTML Completo",
            "en": "📊 View Full HTML Report",
            "es": "📊 Ver Informe HTML Completo"
        },
        "btn_open_folder": {
            "it": "📁 Apri Cartella Report",
            "en": "📁 Open Report Folder",
            "es": "📁 Abrir Carpeta Informes"
        },
        "btn_generate_fixes": {
            "it": "🔧 Genera Fix Suggeriti",
            "en": "🔧 Generate Suggested Fixes",
            "es": "🔧 Generar Correcciones Sugeridas"
        },

        # === LABELS ===
        "label_url": {
            "it": "URL Target:",
            "en": "Target URL:",
            "es": "URL Objetivo:"
        },
        "label_project": {
            "it": "Nome Progetto:",
            "en": "Project Name:",
            "es": "Nombre del Proyecto:"
        },
        "label_max_pages": {
            "it": "Max Pagine:",
            "en": "Max Pages:",
            "es": "Páginas Máx:"
        },
        "label_max_depth": {
            "it": "Profondità Max:",
            "en": "Max Depth:",
            "es": "Profundidad Máx:"
        },
        "label_concurrency": {
            "it": "Concorrenza:",
            "en": "Concurrency:",
            "es": "Concurrencia:"
        },
        "label_delay": {
            "it": "Delay (ms):",
            "en": "Delay (ms):",
            "es": "Retraso (ms):"
        },
        "label_language": {
            "it": "🌐 Lingua:",
            "en": "🌐 Language:",
            "es": "🌐 Idioma:"
        },

        # === GROUPS ===
        "group_basic": {
            "it": "Configurazione Base",
            "en": "Basic Configuration",
            "es": "Configuración Básica"
        },
        "group_advanced": {
            "it": "Opzioni Avanzate",
            "en": "Advanced Options",
            "es": "Opciones Avanzadas"
        },
        "group_ai": {
            "it": "🤖 AI Fix Avanzati (Opzionale)",
            "en": "🤖 Advanced AI Fixes (Optional)",
            "es": "🤖 Correcciones IA Avanzadas (Opcional)"
        },
        "group_progress": {
            "it": "📊 Progresso Scansione",
            "en": "📊 Scan Progress",
            "es": "📊 Progreso del Escaneo"
        },
        "group_log": {
            "it": "📝 Log Attività",
            "en": "📝 Activity Log",
            "es": "📝 Registro de Actividad"
        },
        "group_stats": {
            "it": "📋 Riepilogo Statistiche",
            "en": "📋 Statistics Summary",
            "es": "📋 Resumen Estadístico"
        },
        "group_actions": {
            "it": "🎯 Azioni Disponibili",
            "en": "🎯 Available Actions",
            "es": "🎯 Acciones Disponibles"
        },

        # === CHECKBOXES ===
        "check_sitemap": {
            "it": "Usa sitemap.xml",
            "en": "Use sitemap.xml",
            "es": "Usar sitemap.xml"
        },
        "check_robots": {
            "it": "Rispetta robots.txt",
            "en": "Respect robots.txt",
            "es": "Respetar robots.txt"
        },
        "check_external": {
            "it": "Segui link esterni",
            "en": "Follow external links",
            "es": "Seguir enlaces externos"
        },
        "check_javascript": {
            "it": "Esegui JavaScript",
            "en": "Execute JavaScript",
            "es": "Ejecutar JavaScript"
        },
        "check_ai_enable": {
            "it": "✨ Abilita AI",
            "en": "✨ Enable AI",
            "es": "✨ Activar IA"
        },

        # === STATUS MESSAGES ===
        "status_ready": {
            "it": "Pronto per la scansione",
            "en": "Ready to scan",
            "es": "Listo para escanear"
        },
        "status_scanning": {
            "it": "Scansione in corso...",
            "en": "Scanning in progress...",
            "es": "Escaneo en progreso..."
        },
        "status_completed": {
            "it": "Scansione completata",
            "en": "Scan completed",
            "es": "Escaneo completado"
        },
        "status_error": {
            "it": "Errore durante la scansione",
            "en": "Error during scan",
            "es": "Error durante el escaneo"
        },

        # === STATISTICS ===
        "stat_pages_scanned": {
            "it": "Pagine scansionate:",
            "en": "Pages scanned:",
            "es": "Páginas escaneadas:"
        },
        "stat_pages_failed": {
            "it": "Pagine fallite:",
            "en": "Failed pages:",
            "es": "Páginas fallidas:"
        },
        "stat_issues_found": {
            "it": "Issues trovati:",
            "en": "Issues found:",
            "es": "Issues encontrados:"
        },
        "stat_images_no_alt": {
            "it": "Immagini senza ALT:",
            "en": "Images without ALT:",
            "es": "Imágenes sin ALT:"
        },
        "stat_total_pages": {
            "it": "📄 Pagine totali:",
            "en": "📄 Total pages:",
            "es": "📄 Páginas totales:"
        },
        "stat_success_rate": {
            "it": "✅ Tasso successo:",
            "en": "✅ Success rate:",
            "es": "✅ Tasa de éxito:"
        },
        "stat_avg_score": {
            "it": "⭐ Score medio:",
            "en": "⭐ Average score:",
            "es": "⭐ Puntuación media:"
        },
        "stat_critical_issues": {
            "it": "🔴 Issues critici:",
            "en": "🔴 Critical issues:",
            "es": "🔴 Issues críticos:"
        },

        # === MESSAGES ===
        "msg_scan_success": {
            "it": "Scansione completata con successo!",
            "en": "Scan completed successfully!",
            "es": "¡Escaneo completado con éxito!"
        },
        "msg_export_success": {
            "it": "Export completato",
            "en": "Export completed",
            "es": "Exportación completada"
        },
        "msg_no_data": {
            "it": "Nessun dato",
            "en": "No data",
            "es": "Sin datos"
        },
        "msg_confirm_close": {
            "it": "Conferma chiusura",
            "en": "Confirm close",
            "es": "Confirmar cierre"
        },
        "msg_scan_running": {
            "it": "La scansione è in corso. Vuoi interromperla?",
            "en": "A scan is running. Do you want to stop it?",
            "es": "Hay un escaneo en progreso. ¿Quieres detenerlo?"
        },

        # === TOOLTIPS ===
        "tooltip_theme_toggle": {
            "it": "Cambia tema (Light/Dark)",
            "en": "Change theme (Light/Dark)",
            "es": "Cambiar tema (Claro/Oscuro)"
        },
        "tooltip_language": {
            "it": "Seleziona lingua interfaccia",
            "en": "Select interface language",
            "es": "Seleccionar idioma de interfaz"
        },

        # === AI SECTION ===
        "ai_provider": {
            "it": "Provider AI:",
            "en": "AI Provider:",
            "es": "Proveedor IA:"
        },
        "ai_api_key": {
            "it": "API Key:",
            "en": "API Key:",
            "es": "Clave API:"
        },
        "ai_model": {
            "it": "Modello:",
            "en": "Model:",
            "es": "Modelo:"
        },

        # === THEME ===
        "theme_changed": {
            "it": "🎨 Tema cambiato in:",
            "en": "🎨 Theme changed to:",
            "es": "🎨 Tema cambiado a:"
        },
        "theme_light": {
            "it": "Light Mode",
            "en": "Light Mode",
            "es": "Modo Claro"
        },
        "theme_dark": {
            "it": "Dark Mode",
            "en": "Dark Mode",
            "es": "Modo Oscuro"
        },

        # === LANGUAGE ===
        "language_changed": {
            "it": "🌐 Lingua cambiata in: Italiano",
            "en": "🌐 Language changed to: English",
            "es": "🌐 Idioma cambiado a: Español"
        },
        "language_restart": {
            "it": "Riavvia l'app per applicare la nuova lingua",
            "en": "Restart the app to apply new language",
            "es": "Reinicia la aplicación para aplicar el nuevo idioma"
        },
    }

    def __init__(self):
        self.settings = QSettings("PyPrestaScan", "GUI")
        self.current_language = self._load_saved_language()

    def _load_saved_language(self) -> str:
        """Carica lingua salvata o rileva lingua di sistema"""
        saved_lang = self.settings.value("language", None)

        if saved_lang:
            return saved_lang

        # Auto-detect system language
        return self._detect_system_language()

    def _detect_system_language(self) -> str:
        """Rileva lingua di sistema"""
        try:
            system_locale = locale.getdefaultlocale()[0]

            if system_locale:
                lang_code = system_locale.split('_')[0].lower()

                # Mappa codici lingua
                if lang_code == 'it':
                    return 'it'
                elif lang_code == 'es':
                    return 'es'
                else:
                    return 'en'  # Default English
        except:
            pass

        return 'en'  # Default fallback

    def get_current_language(self) -> str:
        """Restituisce lingua corrente"""
        return self.current_language

    def set_language(self, language: str):
        """Imposta nuova lingua"""
        if language not in ['it', 'en', 'es']:
            raise ValueError(f"Lingua non supportata: {language}")

        self.current_language = language
        self.save_preference(language)

    def save_preference(self, language: str):
        """Salva preferenza lingua"""
        self.settings.setValue("language", language)
        self.settings.sync()

    def t(self, key: str) -> str:
        """
        Translate - ottieni traduzione per chiave

        Args:
            key: Chiave traduzione (es. "app_title")

        Returns:
            str: Stringa tradotta nella lingua corrente
        """
        if key not in self.TRANSLATIONS:
            return f"[{key}]"  # Fallback se chiave non esiste

        translations = self.TRANSLATIONS[key]
        return translations.get(self.current_language, translations.get('en', key))

    def get_language_name(self, lang_code: str) -> str:
        """Ottieni nome lingua da codice"""
        names = {
            'it': 'Italiano',
            'en': 'English',
            'es': 'Español'
        }
        return names.get(lang_code, lang_code)

    def get_available_languages(self) -> Dict[str, str]:
        """Ottieni dizionario lingue disponibili {codice: nome}"""
        return {
            'it': 'Italiano 🇮🇹',
            'en': 'English 🇬🇧',
            'es': 'Español 🇪🇸'
        }


# Istanza globale singleton
_translation_manager = None


def get_translation_manager() -> TranslationManager:
    """Ottieni istanza globale TranslationManager (singleton)"""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager()
    return _translation_manager


def t(key: str) -> str:
    """
    Shortcut per traduzione rapida

    Usage:
        from pyprestascan.gui.i18n import t
        label = QLabel(t("app_title"))
    """
    return get_translation_manager().t(key)
