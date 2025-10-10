"""
Profili di scansione predefiniti per PyPrestaScan
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class ScanType(Enum):
    """Tipi di scansione disponibili"""
    COMPLETE = "complete"
    QUICK = "quick"  
    IMAGES_ALT = "images_alt"
    TECHNICAL_SEO = "technical_seo"
    PRESTASHOP_SPECIFIC = "prestashop_specific"
    CONTENT_ANALYSIS = "content_analysis"
    PERFORMANCE = "performance"
    CUSTOM = "custom"


@dataclass
class ScanProfile:
    """Profilo di scansione con configurazioni specifiche"""
    name: str
    description: str
    scan_type: ScanType
    max_urls: int
    concurrency: int
    delay: int
    depth: Optional[int]
    include_patterns: List[str]
    exclude_patterns: List[str]
    focus_areas: List[str]
    estimated_time: str
    prestashop_mode: bool = True
    include_subdomains: bool = False


# Profili predefiniti
SCAN_PROFILES = {
    ScanType.COMPLETE: ScanProfile(
        name="🔍 Scansione Completa",
        description="Analisi SEO completa di tutto il sito con tutte le regole attive",
        scan_type=ScanType.COMPLETE,
        max_urls=10000,
        concurrency=15,
        delay=200,
        depth=None,
        include_patterns=[],
        exclude_patterns=[
            r"\?.*orderby=",
            r"\?.*selected_filters=", 
            r"\?.*page=\d+",
            r"/admin/.*",
            r"/modules/.*"
        ],
        focus_areas=[
            "Title e Meta Tags",
            "Heading Structure", 
            "Images ALT Text",
            "Internal Linking",
            "Canonical URLs",
            "OpenGraph Tags",
            "JSON-LD Schema",
            "PrestaShop Specifics",
            "Content Duplicates",
            "Technical SEO"
        ],
        estimated_time="30-60 min",
        prestashop_mode=True
    ),
    
    ScanType.QUICK: ScanProfile(
        name="⚡ Scansione Veloce",
        description="Controllo rapido delle pagine principali (home, categorie top, prodotti popolari)",
        scan_type=ScanType.QUICK,
        max_urls=500,
        concurrency=25,
        delay=100,
        depth=2,
        include_patterns=[
            r"^https?://[^/]+/?$",  # Homepage
            r"/category/.*",         # Categorie principali
            r".*-c\d+\.html$",      # Categorie PS
            r".*-p\d+\.html$"       # Prodotti top
        ],
        exclude_patterns=[
            r"\?.*page=",
            r"\?.*orderby=",
            r"\?.*selected_filters=",
            r"/customer/.*",
            r"/order/.*"
        ],
        focus_areas=[
            "Title Tags",
            "Meta Descriptions", 
            "H1 Tags",
            "Canonical URLs",
            "Basic PrestaShop Issues"
        ],
        estimated_time="5-15 min",
        prestashop_mode=True
    ),
    
    ScanType.IMAGES_ALT: ScanProfile(
        name="🖼️ Focus Immagini ALT",
        description="Analisi specifica di tutte le immagini per ALT text mancanti o inadeguati",
        scan_type=ScanType.IMAGES_ALT,
        max_urls=5000,
        concurrency=20,
        delay=150,
        depth=None,
        include_patterns=[
            r".*-p\d+\.html",      # Pagine prodotto
            r"/category/.*",        # Categorie  
            r".*-c\d+\.html",      # Categorie PS
            r"/cms/.*"              # Contenuti CMS
        ],
        exclude_patterns=[
            r"/cart.*",
            r"/order.*",
            r"/customer.*",
            r"\?.*orderby=",
            r"\?.*page="
        ],
        focus_areas=[
            "Images Missing ALT",
            "Images Empty ALT", 
            "Images Generic ALT",
            "Product Images Optimization",
            "Category Images Analysis"
        ],
        estimated_time="15-30 min",
        prestashop_mode=True
    ),
    
    ScanType.TECHNICAL_SEO: ScanProfile(
        name="🔧 SEO Tecnico",
        description="Focus su aspetti tecnici: canonical, robots, sitemap, prestazioni",
        scan_type=ScanType.TECHNICAL_SEO,
        max_urls=3000,
        concurrency=15,
        delay=200,
        depth=None,
        include_patterns=[],
        exclude_patterns=[
            r"\?.*orderby=",
            r"\?.*selected_filters=",
            r"\?.*page=",
            r"/customer/.*",
            r"/modules/.*"
        ],
        focus_areas=[
            "Canonical URLs",
            "Meta Robots Tags",
            "XML Sitemap Analysis",
            "URL Structure",
            "HTTP Status Codes",
            "Redirect Chains",
            "Page Load Performance",
            "Mobile Optimization"
        ],
        estimated_time="20-40 min",
        prestashop_mode=True
    ),
    
    ScanType.PRESTASHOP_SPECIFIC: ScanProfile(
        name="🛒 PrestaShop Specifico", 
        description="Controlli dedicati alle configurazioni tipiche di PrestaShop",
        scan_type=ScanType.PRESTASHOP_SPECIFIC,
        max_urls=2000,
        concurrency=18,
        delay=180,
        depth=None,
        include_patterns=[
            r".*-p\d+\.html",      # Prodotti
            r".*-c\d+\.html",      # Categorie
            r"/cart.*",             # Carrello
            r"/order.*",            # Checkout
            r"/customer.*"          # Area clienti
        ],
        exclude_patterns=[
            r"/admin/.*",
            r"/modules/.*\.css",
            r"/modules/.*\.js"
        ],
        focus_areas=[
            "Product Page SEO",
            "Category Page Structure",
            "Cart/Checkout Noindex",
            "Faceted Search Issues",
            "Multilingual Setup",
            "JSON-LD Product Schema",
            "Friendly URLs vs Parameters",
            "PrestaShop Version Detection"
        ],
        estimated_time="15-35 min",
        prestashop_mode=True
    ),
    
    ScanType.CONTENT_ANALYSIS: ScanProfile(
        name="📝 Analisi Contenuti",
        description="Focus su qualità contenuti, duplicati, struttura heading",
        scan_type=ScanType.CONTENT_ANALYSIS,
        max_urls=4000,
        concurrency=12,
        delay=250,
        depth=None,
        include_patterns=[],
        exclude_patterns=[
            r"\?.*orderby=",
            r"\?.*page=",
            r"/customer/.*",
            r"/cart.*",
            r"/order.*"
        ],
        focus_areas=[
            "Content Duplicates",
            "Heading Hierarchy",
            "Content Length Analysis", 
            "Title Tags Quality",
            "Meta Descriptions Quality",
            "Internal Linking Patterns",
            "Keyword Optimization",
            "Content Structure"
        ],
        estimated_time="25-45 min",
        prestashop_mode=True
    ),
    
    ScanType.PERFORMANCE: ScanProfile(
        name="🚀 Performance & UX",
        description="Analisi orientata alle prestazioni e user experience",
        scan_type=ScanType.PERFORMANCE,
        max_urls=1500,
        concurrency=10,
        delay=300,
        depth=3,
        include_patterns=[
            r".*-p\d+\.html",      # Prodotti principali
            r".*-c\d+\.html",      # Categorie principali
            r"^https?://[^/]+/?$"   # Homepage
        ],
        exclude_patterns=[
            r"\?.*",                # Tutti i parametri
            r"/modules/.*",
            r"/admin/.*"
        ],
        focus_areas=[
            "Page Load Speed",
            "Image Optimization",
            "JavaScript/CSS Issues",
            "Mobile Responsiveness",
            "Core Web Vitals",
            "User Experience",
            "Navigation Structure",
            "Search Functionality"
        ],
        estimated_time="10-25 min",
        prestashop_mode=True
    )
}


def get_profile(scan_type: ScanType) -> ScanProfile:
    """Ottieni profilo per tipo di scansione"""
    return SCAN_PROFILES.get(scan_type)


def get_all_profiles() -> Dict[ScanType, ScanProfile]:
    """Ottieni tutti i profili disponibili"""
    return SCAN_PROFILES


def create_custom_profile(name: str, description: str, **kwargs) -> ScanProfile:
    """Crea profilo personalizzato"""
    defaults = {
        'max_urls': 1000,
        'concurrency': 15,
        'delay': 200,
        'depth': None,
        'include_patterns': [],
        'exclude_patterns': [],
        'focus_areas': ["Personalizzato"],
        'estimated_time': "Variabile",
        'prestashop_mode': True,
        'include_subdomains': False
    }
    
    # Unisci con parametri personalizzati
    config = {**defaults, **kwargs}
    
    return ScanProfile(
        name=name,
        description=description,
        scan_type=ScanType.CUSTOM,
        **config
    )


class ScanProfileManager:
    """Manager per gestione profili di scansione"""
    
    def __init__(self):
        self.profiles = get_all_profiles()
        self.custom_profiles = {}
    
    def add_custom_profile(self, profile: ScanProfile) -> str:
        """Aggiunge profilo personalizzato"""
        profile_id = f"custom_{len(self.custom_profiles)}"
        self.custom_profiles[profile_id] = profile
        return profile_id
    
    def get_profile_by_type(self, scan_type: ScanType) -> ScanProfile:
        """Ottieni profilo per tipo"""
        return self.profiles.get(scan_type)
    
    def get_custom_profile(self, profile_id: str) -> Optional[ScanProfile]:
        """Ottieni profilo personalizzato"""
        return self.custom_profiles.get(profile_id)
    
    def get_all_profile_names(self) -> List[str]:
        """Ottieni nomi di tutti i profili"""
        names = [profile.name for profile in self.profiles.values()]
        names.extend([profile.name for profile in self.custom_profiles.values()])
        return names
    
    def get_profile_suggestions(self, url: str) -> List[ScanType]:
        """Suggerisci profili basati su URL"""
        suggestions = []
        
        url_lower = url.lower()
        
        # Suggerimenti intelligenti basati su URL
        if 'prestashop' in url_lower or any(pattern in url_lower for pattern in ['-p', '-c', '/category/', '/product/']):
            suggestions.extend([
                ScanType.PRESTASHOP_SPECIFIC,
                ScanType.COMPLETE,
                ScanType.IMAGES_ALT
            ])
        
        if 'demo' in url_lower or 'staging' in url_lower:
            suggestions.extend([
                ScanType.QUICK,
                ScanType.TECHNICAL_SEO
            ])
        
        # Default sempre disponibili
        if not suggestions:
            suggestions = [ScanType.QUICK, ScanType.COMPLETE]
        
        return suggestions[:3]  # Max 3 suggerimenti