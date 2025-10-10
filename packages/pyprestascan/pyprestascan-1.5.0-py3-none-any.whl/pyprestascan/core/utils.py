"""
Utilities per PyPrestaScan
"""
import re
import hashlib
import logging
from typing import Optional, List, Dict, Set, Tuple
from urllib.parse import urlparse, urlunparse, urljoin, parse_qs, urlencode
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn


# Pattern URL rumorosi PrestaShop
PRESTASHOP_NOISY_PARAMS = {
    'orderby', 'orderway', 'n', 'page', 'q', 'search_query', 
    'id_lang', 'selected_filters', 'from-xhr', 'live_configurator_token',
    'p', 'controller', 'fc', 'module', 'id_cms', 'id_category',
    'isolang', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'fbclid', 'gclid', '_ga', '_gid', 'srsltid'
}

# Pattern URL PrestaShop tipici
PRESTASHOP_URL_PATTERNS = [
    r'/category/',
    r'/content/',
    r'/manufacturer/',
    r'/supplier/',
    r'/module/',
    r'-c\d+\.html',  # categoria con ID
    r'-p\d+\.html',  # prodotto con ID
    r'\?id_product=',
    r'\?id_category=',
    r'\?id_cms=',
    r'/cart\?',
    r'/order',
    r'/my-account',
    r'/authentication',
    r'/checkout'
]

# ALT text considerati generici
GENERIC_ALT_PATTERNS = [
    r'^(image|immagine|foto|banner|placeholder|logo|default|picture|pic)$',
    r'^\s*$',  # vuoto o solo spazi
    r'^(untitled|senza[\s\-_]*titolo)$',
    r'^(home|homepage)$',
    r'^(product|prodotto)$',
    r'^(category|categoria)$'
]

# Compilazione pattern per performance
GENERIC_ALT_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in GENERIC_ALT_PATTERNS]
PRESTASHOP_URL_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in PRESTASHOP_URL_PATTERNS]


class URLNormalizer:
    """Normalizzatore URL con logiche specifiche per PrestaShop"""
    
    def __init__(self, base_domain: str, include_subdomains: bool = False):
        self.include_subdomains = include_subdomains
        # Parse per estrarre solo il dominio
        if base_domain.startswith(('http://', 'https://')):
            self._parsed_base = urlparse(base_domain)
            self.base_domain = self._parsed_base.netloc.lower()
        else:
            self.base_domain = base_domain.lower()
            self._parsed_base = urlparse(f"https://{self.base_domain}")
    
    def normalize(self, url: str, remove_noisy_params: bool = True) -> str:
        """Normalizza URL rimuovendo fragment, parametri rumorosi, etc."""
        if not url or not url.strip():
            return ""
        
        # Parse URL
        parsed = urlparse(url.strip())
        
        # Normalizza scheme (forza HTTPS se possibile)
        scheme = parsed.scheme.lower()
        if not scheme:
            scheme = 'https'
        elif scheme == 'http':
            # Mantieni HTTP se specificato esplicitamente
            pass
        
        # Normalizza host
        netloc = parsed.netloc.lower()
        if not netloc:
            return ""
        
        # Normalizza path
        path = parsed.path
        if not path or path == '/':
            path = '/'
        else:
            # Rimuovi trailing slash tranne per root
            if path.endswith('/') and len(path) > 1:
                path = path.rstrip('/')
            # Normalizza doppi slash
            path = re.sub(r'/+', '/', path)
        
        # Gestione parametri query
        query = ""
        if parsed.query and not remove_noisy_params:
            query = parsed.query
        elif parsed.query and remove_noisy_params:
            # Filtra parametri rumorosi
            params = parse_qs(parsed.query, keep_blank_values=True)
            clean_params = {}
            for key, values in params.items():
                if key.lower() not in PRESTASHOP_NOISY_PARAMS:
                    clean_params[key] = values
            
            if clean_params:
                query = urlencode(clean_params, doseq=True)
        
        # Ricostruisci URL (senza fragment)
        normalized = urlunparse((scheme, netloc, path, '', query, ''))
        
        return normalized
    
    def is_same_domain(self, url: str) -> bool:
        """Verifica se URL appartiene allo stesso dominio base"""
        if not url:
            return False
        
        # Escludi schemi non HTTP
        if url.startswith(('javascript:', 'mailto:', 'tel:', '#')):
            return False
        
        # URL relativi sono sempre dello stesso dominio
        if url.startswith('/'):
            return True
        
        parsed = urlparse(url)
        if not parsed.netloc:
            # URL relativo senza / (es: "page.html")
            return not parsed.scheme  # True solo se non ha schema
        
        host = parsed.netloc.lower()
        
        if self.include_subdomains:
            # Accetta sottodomini
            return host == self.base_domain or host.endswith('.' + self.base_domain)
        else:
            # Solo stesso host esatto
            return host == self.base_domain
    
    def resolve_relative(self, base_url: str, relative_url: str) -> str:
        """Risolve URL relativi"""
        if not relative_url:
            return ""
        
        # Se è già assoluto, normalizza e restituisci
        if relative_url.startswith(('http://', 'https://')):
            return self.normalize(relative_url)
        
        # Risolvi relativo
        absolute = urljoin(base_url, relative_url)
        return self.normalize(absolute)


class PrestaShopDetector:
    """Rilevatore caratteristiche PrestaShop"""
    
    @staticmethod
    def is_prestashop_url(url: str) -> bool:
        """Verifica se URL sembra di PrestaShop basandosi su pattern"""
        for pattern in PRESTASHOP_URL_REGEX:
            if pattern.search(url):
                return True
        return False
    
    @staticmethod
    def detect_page_type(url: str, html_content: str = "") -> Dict[str, bool]:
        """Rileva tipo di pagina PrestaShop"""
        result = {
            'is_product': False,
            'is_category': False,
            'is_cms': False,
            'is_faceted_filter': False,
            'is_cart_or_checkout': False,
            'is_account': False
        }
        
        url_lower = url.lower()
        
        # Rilevamento da URL
        if re.search(r'-p\d+\.html|\?id_product=', url_lower):
            result['is_product'] = True
        elif re.search(r'-c\d+\.html|\?id_category=|/category/', url_lower):
            result['is_category'] = True
        elif re.search(r'\?id_cms=|/content/', url_lower):
            result['is_cms'] = True
        elif 'selected_filters=' in url_lower or 'facets=' in url_lower:
            result['is_faceted_filter'] = True
        elif re.search(r'/cart|/order|/checkout', url_lower):
            result['is_cart_or_checkout'] = True
        elif re.search(r'/my-account|/authentication|/login', url_lower):
            result['is_account'] = True
        
        # Rilevamento da contenuto HTML se disponibile
        if html_content:
            content_lower = html_content.lower()
            
            # Cerca meta generator
            if 'prestashop' in content_lower:
                # Affina rilevamento basandosi su classi/ID tipici
                if 'id="product"' in content_lower or 'class="product"' in content_lower:
                    result['is_product'] = True
                elif 'id="category"' in content_lower or 'class="category"' in content_lower:
                    result['is_category'] = True
        
        return result


class TextAnalyzer:
    """Analizzatore testi per duplicati e qualità"""
    
    @staticmethod
    def extract_visible_text(html_content: str) -> str:
        """Estrae testo visibile da HTML per analisi duplicati"""
        # Implementazione semplificata - in una versione completa 
        # si userebbe selectolax per parsing più accurato
        
        # Rimuovi script e style
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Rimuovi tag HTML
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Normalizza spazi bianchi
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def calculate_content_hash(text: str) -> str:
        """Calcola hash del contenuto per rilevamento duplicati"""
        # Normalizza testo
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Rimuovi contenuti molto specifici che possono cambiare
        # tra pagine simili (date, prezzi, ecc.)
        normalized = re.sub(r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b', '[DATE]', normalized)
        normalized = re.sub(r'\b\d+[.,]\d{2}\s*€?\s*\b', '[PRICE]', normalized)
        
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    @staticmethod
    def is_generic_alt(alt_text: str) -> bool:
        """Verifica se un testo ALT è considerato generico"""
        if not alt_text or not alt_text.strip():
            return True
        
        alt_clean = alt_text.strip()
        
        for pattern in GENERIC_ALT_REGEX:
            if pattern.match(alt_clean):
                return True
        
        return False
    
    @staticmethod
    def classify_alt_status(alt_text: Optional[str]) -> str:
        """Classifica stato ALT text"""
        if alt_text is None:
            return "MISSING"
        elif not alt_text.strip():
            return "EMPTY"
        elif TextAnalyzer.is_generic_alt(alt_text):
            return "GENERIC"
        else:
            return "OK"


class ProjectManager:
    """Gestore progetti e directory"""
    
    def __init__(self, project_name: str = "default"):
        self.project_name = project_name
        self.base_dir = Path.home() / ".pyprestascan"
        self.project_dir = self.base_dir / project_name
        
        # Crea directory se non esistente
        self.project_dir.mkdir(parents=True, exist_ok=True)
    
    def get_db_path(self) -> Path:
        """Restituisce path database SQLite"""
        return self.project_dir / "crawl.db"
    
    def get_export_dir(self, export_dir: Optional[Path] = None) -> Path:
        """Restituisce directory export (crea se necessario)"""
        if export_dir:
            export_path = Path(export_dir).resolve()
        else:
            export_path = self.project_dir / "reports"
        
        export_path.mkdir(parents=True, exist_ok=True)
        return export_path
    
    def cleanup_old_files(self, keep_days: int = 7) -> None:
        """Pulisce file vecchi del progetto"""
        # Implementazione opzionale per cleanup
        pass


class RichLogger:
    """Logger con Rich per output colorato ed emoji"""
    
    def __init__(self, debug: bool = False, quiet: bool = False, no_color: bool = False):
        self.console = Console(no_color=no_color)
        self.debug_enabled = debug
        self.quiet = quiet
        
        # Configura logging
        level = logging.DEBUG if debug else logging.INFO
        if quiet:
            level = logging.WARNING
        
        # Rich handler
        rich_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_level=True,
            show_path=debug,
            rich_tracebacks=True
        )
        
        # Configura logger root
        logging.basicConfig(
            level=level,
            format="%(message)s",
            handlers=[rich_handler]
        )
        
        self.logger = logging.getLogger("pyprestascan")
    
    def info(self, message: str, emoji: str = "ℹ️") -> None:
        """Log informativo con emoji"""
        if not self.quiet:
            self.logger.info(f"{emoji} {message}")
    
    def success(self, message: str, emoji: str = "✅") -> None:
        """Log successo"""
        if not self.quiet:
            self.logger.info(f"{emoji} {message}")
    
    def warning(self, message: str, emoji: str = "⚠️") -> None:
        """Log warning"""
        self.logger.warning(f"{emoji} {message}")
    
    def error(self, message: str, emoji: str = "❌") -> None:
        """Log errore"""
        self.logger.error(f"{emoji} {message}")
    
    def debug(self, message: str, emoji: str = "🐛") -> None:
        """Log debug"""
        if self.debug_enabled:
            self.logger.debug(f"{emoji} {message}")
    
    def robots_ok(self, url: str) -> None:
        """Log per robots.txt OK"""
        self.debug(f"📥 Robots allow: {url}")
    
    def robots_deny(self, url: str) -> None:
        """Log per robots.txt deny"""
        self.debug(f"🚫 Robots deny: {url}")
    
    def sitemap_found(self, url: str, count: int) -> None:
        """Log per sitemap trovata"""
        self.info(f"🗺️ Sitemap trovata: {count} URL in {url}")
    
    def page_crawled(self, url: str, status: int, ttfb_ms: int) -> None:
        """Log per pagina crawlata"""
        emoji = "🔍" if status == 200 else "⚠️" if status >= 300 else "❌"
        self.debug(f"{emoji} [{status}] {url} ({ttfb_ms}ms)")
    
    def images_analyzed(self, count: int, missing_alt: int) -> None:
        """Log per analisi immagini"""
        self.debug(f"🖼️ Analizzate {count} immagini, {missing_alt} senza ALT")
    
    def print_summary(self, stats: Dict[str, int]) -> None:
        """Stampa riepilogo finale con colori"""
        if self.quiet:
            return
        
        self.console.print("\n🎯 [bold green]Riepilogo Crawling[/bold green]")
        self.console.print(f"• Pagine totali: {stats.get('total_pages', 0)}")
        self.console.print(f"• Pagine 2xx: [green]{stats.get('pages_2xx', 0)}[/green]")
        self.console.print(f"• Pagine 3xx: [yellow]{stats.get('pages_3xx', 0)}[/yellow]")
        self.console.print(f"• Pagine 4xx: [red]{stats.get('pages_4xx', 0)}[/red]")
        self.console.print(f"• Pagine 5xx: [red]{stats.get('pages_5xx', 0)}[/red]")
        self.console.print(f"• Issues totali: [yellow]{stats.get('total_issues', 0)}[/yellow]")
        self.console.print(f"• Immagini senza ALT: [red]{stats.get('images_no_alt', 0)}[/red]")


def create_progress() -> Progress:
    """Crea progress bar Rich per monitoraggio"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=Console(),
        refresh_per_second=4
    )