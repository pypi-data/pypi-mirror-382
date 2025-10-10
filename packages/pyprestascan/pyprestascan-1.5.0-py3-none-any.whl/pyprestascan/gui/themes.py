"""
Gestione temi GUI (Light/Dark Mode) per PyPrestaScan
"""
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from typing import Dict, Optional
import platform


class ThemeManager:
    """Gestione temi applicazione con supporto Light/Dark mode"""

    # Palette Light Theme
    LIGHT_THEME = {
        'background': '#FFFFFF',
        'background_secondary': '#F5F5F5',
        'text': '#000000',
        'text_secondary': '#666666',
        'primary': '#667eea',
        'primary_hover': '#764ba2',
        'secondary': '#4CAF50',
        'secondary_hover': '#45a049',
        'border': '#E0E0E0',
        'border_focus': '#667eea',
        'error': '#FF6B6B',
        'warning': '#FFA500',
        'success': '#4CAF50',
        'info': '#2196F3',
        'card_bg': '#FAFAFA',
        'input_bg': '#FFFFFF',
        'button_bg': '#667eea',
        'button_text': '#FFFFFF',
        'log_bg': '#F5F5F5',
        'log_text': '#333333'
    }

    # Palette Dark Theme
    DARK_THEME = {
        'background': '#1E1E1E',
        'background_secondary': '#2D2D2D',
        'text': '#E0E0E0',
        'text_secondary': '#AAAAAA',
        'primary': '#667eea',
        'primary_hover': '#764ba2',
        'secondary': '#4CAF50',
        'secondary_hover': '#45a049',
        'border': '#3D3D3D',
        'border_focus': '#667eea',
        'error': '#FF6B6B',
        'warning': '#FFA500',
        'success': '#4CAF50',
        'info': '#2196F3',
        'card_bg': '#252525',
        'input_bg': '#2D2D2D',
        'button_bg': '#667eea',
        'button_text': '#FFFFFF',
        'log_bg': '#1A1A1A',
        'log_text': '#E0E0E0'
    }

    def __init__(self, app: QApplication):
        self.app = app
        self.settings = QSettings("PyPrestaScan", "GUI")
        self.current_theme = self._load_saved_theme()

    def _load_saved_theme(self) -> str:
        """Carica tema salvato o rileva tema sistema"""
        saved_theme = self.settings.value("theme", None)

        if saved_theme:
            return saved_theme

        # Auto-detect system theme (macOS/Windows)
        return self._detect_system_theme()

    def _detect_system_theme(self) -> str:
        """Rileva tema di sistema (macOS Dark Mode, Windows Theme)"""
        system = platform.system()

        if system == "Darwin":  # macOS
            try:
                import subprocess
                result = subprocess.run(
                    ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                    capture_output=True,
                    text=True
                )
                # Se restituisce "Dark", usa dark theme
                return "dark" if result.returncode == 0 else "light"
            except:
                return "light"

        elif system == "Windows":
            try:
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
                value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                return "light" if value == 1 else "dark"
            except:
                return "light"

        else:
            return "light"

    def get_current_theme(self) -> str:
        """Restituisce tema corrente ('light' o 'dark')"""
        return self.current_theme

    def get_theme_colors(self, theme: Optional[str] = None) -> Dict[str, str]:
        """Ottieni palette colori per tema specificato"""
        if theme is None:
            theme = self.current_theme

        return self.DARK_THEME if theme == "dark" else self.LIGHT_THEME

    def apply_theme(self, theme: str):
        """Applica tema globalmente all'applicazione"""
        if theme not in ["light", "dark"]:
            raise ValueError(f"Tema non valido: {theme}. Usa 'light' o 'dark'")

        self.current_theme = theme
        colors = self.get_theme_colors(theme)

        # Genera stylesheet globale
        stylesheet = self._generate_stylesheet(colors)
        self.app.setStyleSheet(stylesheet)

        # Salva preferenza
        self.save_preference(theme)

    def toggle_theme(self) -> str:
        """Cambia tra light e dark mode, ritorna nuovo tema"""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        return new_theme

    def save_preference(self, theme: str):
        """Salva preferenza tema in QSettings"""
        self.settings.setValue("theme", theme)
        self.settings.sync()

    def _generate_stylesheet(self, colors: Dict[str, str]) -> str:
        """Genera stylesheet Qt completo dal tema"""
        return f"""
            /* ========== GLOBAL ========== */
            QWidget {{
                background-color: {colors['background']};
                color: {colors['text']};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            }}

            /* ========== MAIN WINDOW ========== */
            QMainWindow {{
                background-color: {colors['background']};
            }}

            /* ========== GROUP BOX ========== */
            QGroupBox {{
                border: 2px solid {colors['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                font-weight: bold;
                color: {colors['text']};
                background-color: {colors['card_bg']};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: {colors['primary']};
            }}

            /* ========== LINE EDIT ========== */
            QLineEdit {{
                padding: 8px 12px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background-color: {colors['input_bg']};
                color: {colors['text']};
                selection-background-color: {colors['primary']};
            }}

            QLineEdit:focus {{
                border-color: {colors['border_focus']};
            }}

            /* ========== SPIN BOX ========== */
            QSpinBox {{
                padding: 8px 12px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background-color: {colors['input_bg']};
                color: {colors['text']};
            }}

            /* ========== COMBO BOX ========== */
            QComboBox {{
                padding: 8px 12px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background-color: {colors['input_bg']};
                color: {colors['text']};
            }}

            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {colors['input_bg']};
                color: {colors['text']};
                selection-background-color: {colors['primary']};
                border: 1px solid {colors['border']};
            }}

            /* ========== PUSH BUTTON ========== */
            QPushButton {{
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                background-color: {colors['button_bg']};
                color: {colors['button_text']};
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}

            QPushButton:pressed {{
                background-color: {colors['primary']};
            }}

            QPushButton:disabled {{
                background-color: {colors['border']};
                color: {colors['text_secondary']};
            }}

            /* ========== CHECK BOX ========== */
            QCheckBox {{
                color: {colors['text']};
                spacing: 8px;
            }}

            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {colors['border']};
                border-radius: 4px;
                background-color: {colors['input_bg']};
            }}

            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
                border-color: {colors['primary']};
            }}

            /* ========== TEXT EDIT ========== */
            QTextEdit {{
                border: 1px solid {colors['border']};
                border-radius: 6px;
                background-color: {colors['log_bg']};
                color: {colors['log_text']};
                padding: 8px;
            }}

            /* ========== PROGRESS BAR ========== */
            QProgressBar {{
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background-color: {colors['input_bg']};
                text-align: center;
                color: {colors['text']};
            }}

            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors['primary']}, stop:1 {colors['primary_hover']});
                border-radius: 4px;
            }}

            /* ========== TAB WIDGET ========== */
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                border-radius: 6px;
                background-color: {colors['background']};
            }}

            QTabBar::tab {{
                background-color: {colors['background_secondary']};
                color: {colors['text_secondary']};
                padding: 10px 20px;
                border: 1px solid {colors['border']};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }}

            QTabBar::tab:selected {{
                background-color: {colors['background']};
                color: {colors['primary']};
                font-weight: bold;
            }}

            QTabBar::tab:hover {{
                background-color: {colors['card_bg']};
            }}

            /* ========== TABLE WIDGET ========== */
            QTableWidget {{
                background-color: {colors['background']};
                alternate-background-color: {colors['background_secondary']};
                gridline-color: {colors['border']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                color: {colors['text']};
            }}

            QTableWidget::item {{
                padding: 5px;
            }}

            QTableWidget::item:selected {{
                background-color: {colors['primary']};
                color: white;
            }}

            QHeaderView::section {{
                background-color: {colors['background_secondary']};
                color: {colors['text']};
                padding: 8px;
                border: none;
                border-bottom: 2px solid {colors['primary']};
                font-weight: bold;
            }}

            /* ========== SCROLL BAR ========== */
            QScrollBar:vertical {{
                background-color: {colors['background_secondary']};
                width: 12px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {colors['border']};
                border-radius: 6px;
                min-height: 30px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {colors['primary']};
            }}

            /* ========== STATUS BAR ========== */
            QStatusBar {{
                background-color: {colors['background_secondary']};
                color: {colors['text']};
                border-top: 1px solid {colors['border']};
            }}

            /* ========== LABELS ========== */
            QLabel {{
                color: {colors['text']};
            }}

            /* ========== SLIDER ========== */
            QSlider::groove:horizontal {{
                border: 1px solid {colors['border']};
                height: 8px;
                background: {colors['input_bg']};
                border-radius: 4px;
            }}

            QSlider::handle:horizontal {{
                background: {colors['primary']};
                border: 2px solid {colors['primary']};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}

            QSlider::handle:horizontal:hover {{
                background: {colors['primary_hover']};
            }}
        """

    def get_icon_for_theme(self, theme: Optional[str] = None) -> str:
        """Restituisce emoji icona per tema corrente"""
        if theme is None:
            theme = self.current_theme
        return "🌙" if theme == "light" else "☀️"
