"""
Analizzatore SEO con regole specifiche per PrestaShop e sistema di scoring
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
import re

from .storage import PageData, ImageData, IssueData
from .parser import ParsedData


@dataclass
class SEORule:
    """Definizione di una regola SEO"""
    code: str
    name: str
    description: str
    severity: str  # CRITICAL, WARNING, INFO
    weight: float  # Peso per scoring (0-1)
    prestashop_specific: bool = False


class SEORuleEngine:
    """Motore regole SEO con euristiche PrestaShop"""
    
    def __init__(self, prestashop_mode: bool = True):
        self.prestashop_mode = prestashop_mode
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict[str, SEORule]:
        """Inizializza regole SEO"""
        
        rules = {
            # Regole CRITICAL
            'title_missing': SEORule(
                code='TITLE_MISSING',
                name='Title mancante',
                description='La pagina non ha un tag <title>',
                severity='CRITICAL',
                weight=0.15
            ),
            'title_duplicate': SEORule(
                code='TITLE_DUPLICATE',
                name='Title duplicato',
                description='Il title è identico ad altre pagine',
                severity='CRITICAL',
                weight=0.1
            ),
            'h1_missing': SEORule(
                code='H1_MISSING',
                name='H1 mancante',
                description='La pagina non ha tag H1',
                severity='CRITICAL',
                weight=0.12
            ),
            'h1_multiple': SEORule(
                code='H1_MULTIPLE',
                name='H1 multipli',
                description='La pagina ha più di un tag H1',
                severity='WARNING',
                weight=0.05
            ),
            'canonical_missing_product': SEORule(
                code='CANONICAL_MISSING_PRODUCT',
                name='Canonical mancante su prodotto',
                description='Pagina prodotto senza canonical URL',
                severity='CRITICAL',
                weight=0.15,
                prestashop_specific=True
            ),
            'cart_indexable': SEORule(
                code='CART_INDEXABLE',
                name='Pagina cart indicizzabile',
                description='Pagina cart/checkout senza noindex',
                severity='CRITICAL',
                weight=0.1,
                prestashop_specific=True
            ),
            
            # Regole WARNING
            'meta_description_missing': SEORule(
                code='META_DESCRIPTION_MISSING',
                name='Meta description mancante',
                description='La pagina non ha meta description',
                severity='WARNING',
                weight=0.08
            ),
            'title_too_long': SEORule(
                code='TITLE_TOO_LONG',
                name='Title troppo lungo',
                description='Title superiore a 60 caratteri',
                severity='WARNING',
                weight=0.03
            ),
            'title_too_short': SEORule(
                code='TITLE_TOO_SHORT',
                name='Title troppo corto',
                description='Title inferiore a 10 caratteri',
                severity='WARNING',
                weight=0.04
            ),
            'meta_description_too_long': SEORule(
                code='META_DESCRIPTION_TOO_LONG',
                name='Meta description troppo lunga',
                description='Meta description superiore a 160 caratteri',
                severity='WARNING',
                weight=0.02
            ),
            'meta_description_too_short': SEORule(
                code='META_DESCRIPTION_TOO_SHORT',
                name='Meta description troppo corta',
                description='Meta description inferiore a 50 caratteri',
                severity='WARNING',
                weight=0.02
            ),
            'images_missing_alt': SEORule(
                code='IMAGES_MISSING_ALT',
                name='Immagini senza ALT',
                description='Immagini senza attributo ALT',
                severity='WARNING',
                weight=0.06
            ),
            'canonical_missing': SEORule(
                code='CANONICAL_MISSING',
                name='Canonical URL mancante',
                description='Pagina senza canonical URL',
                severity='WARNING',
                weight=0.05
            ),
            'faceted_no_canonical': SEORule(
                code='FACETED_NO_CANONICAL',
                name='Filtri senza canonical',
                description='Pagina con filtri faceted senza canonical',
                severity='WARNING',
                weight=0.08,
                prestashop_specific=True
            ),
            'product_no_jsonld': SEORule(
                code='PRODUCT_NO_JSONLD',
                name='Prodotto senza JSON-LD',
                description='Pagina prodotto senza structured data Product',
                severity='WARNING',
                weight=0.07,
                prestashop_specific=True
            ),
            'category_no_pagination': SEORule(
                code='CATEGORY_NO_PAGINATION',
                name='Categoria senza rel prev/next',
                description='Categoria paginata senza rel="prev/next"',
                severity='WARNING',
                weight=0.04,
                prestashop_specific=True
            ),
            'hreflang_missing': SEORule(
                code='HREFLANG_MISSING',
                name='Hreflang mancante',
                description='Sito multilingua senza hreflang',
                severity='WARNING',
                weight=0.05,
                prestashop_specific=True
            ),
            
            # Regole INFO
            'og_title_missing': SEORule(
                code='OG_TITLE_MISSING',
                name='OpenGraph title mancante',
                description='Pagina senza og:title',
                severity='INFO',
                weight=0.02
            ),
            'og_description_missing': SEORule(
                code='OG_DESCRIPTION_MISSING',
                name='OpenGraph description mancante',
                description='Pagina senza og:description',
                severity='INFO',
                weight=0.02
            ),
            'og_image_missing': SEORule(
                code='OG_IMAGE_MISSING',
                name='OpenGraph image mancante',
                description='Pagina senza og:image',
                severity='INFO',
                weight=0.02
            ),
            'headings_hierarchy': SEORule(
                code='HEADINGS_HIERARCHY',
                name='Gerarchia heading non corretta',
                description='Salti nella gerarchia dei heading',
                severity='INFO',
                weight=0.02
            ),
            'images_no_lazy_loading': SEORule(
                code='IMAGES_NO_LAZY_LOADING',
                name='Immagini senza lazy loading',
                description='Immagini senza attributo loading="lazy"',
                severity='INFO',
                weight=0.01
            )
        }
        
        return rules
    
    def analyze_page(self, parsed_data: ParsedData) -> Tuple[List[IssueData], float]:
        """Analizza una pagina e restituisce issues + score"""
        issues = []
        page = parsed_data.page
        images = parsed_data.images
        
        # Applica tutte le regole
        for rule_code, rule in self.rules.items():
            # Salta regole PrestaShop se modalità disabilitata
            if rule.prestashop_specific and not self.prestashop_mode:
                continue
            
            rule_issues = self._apply_rule(rule, page, images)
            issues.extend(rule_issues)
        
        # Calcola score complessivo
        score = self._calculate_score(issues, page)
        
        return issues, score
    
    def _apply_rule(self, rule: SEORule, page: PageData, images: List[ImageData]) -> List[IssueData]:
        """Applica una singola regola"""
        issues = []
        
        # Dispatcher per regole specifiche
        method_name = f"_check_{rule.code.lower()}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            rule_issues = method(page, images)
            
            # Converte a IssueData se necessario
            for issue in rule_issues:
                if isinstance(issue, dict):
                    issues.append(IssueData(
                        page_url=page.url,
                        severity=rule.severity,
                        code=rule.code,
                        message=rule.description,
                        meta=issue
                    ))
                elif isinstance(issue, IssueData):
                    issues.append(issue)
        
        return issues
    
    def _calculate_score(self, issues: List[IssueData], page: PageData) -> float:
        """Calcola score SEO della pagina (0-100)"""
        base_score = 100.0
        
        # Raggruppa issues per severity
        critical_count = sum(1 for i in issues if i.severity == 'CRITICAL')
        warning_count = sum(1 for i in issues if i.severity == 'WARNING')
        info_count = sum(1 for i in issues if i.severity == 'INFO')
        
        # Penalità per severity
        score_penalty = (critical_count * 15) + (warning_count * 5) + (info_count * 1)
        
        # Bonus per caratteristiche positive
        if page.title and len(page.title) > 10:
            base_score += 5
        
        if page.meta_description and 50 <= len(page.meta_description) <= 160:
            base_score += 3
        
        if page.canonical:
            base_score += 3
        
        if page.h1_count == 1:
            base_score += 5
        
        # Bonus PrestaShop specifici
        if self.prestashop_mode:
            if page.is_product and 'Product' in page.jsonld_types:
                base_score += 5
            
            if page.is_cart_or_checkout and 'noindex' in page.meta_robots:
                base_score += 3
        
        final_score = max(0.0, min(100.0, base_score - score_penalty))
        return round(final_score, 1)
    
    # Implementazione regole specifiche
    
    def _check_title_missing(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica title mancante"""
        if not page.title or not page.title.strip():
            return [{'field': 'title', 'value': page.title}]
        return []
    
    def _check_title_too_long(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica title troppo lungo"""
        if page.title and len(page.title) > 60:
            return [{'field': 'title', 'length': len(page.title), 'max': 60}]
        return []
    
    def _check_title_too_short(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica title troppo corto"""
        if page.title and len(page.title) < 10:
            return [{'field': 'title', 'length': len(page.title), 'min': 10}]
        return []
    
    def _check_h1_missing(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica H1 mancante"""
        if page.h1_count == 0:
            return [{'field': 'h1', 'count': page.h1_count}]
        return []
    
    def _check_h1_multiple(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica H1 multipli"""
        if page.h1_count > 1:
            return [{'field': 'h1', 'count': page.h1_count}]
        return []
    
    def _check_meta_description_missing(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica meta description mancante"""
        if not page.meta_description or not page.meta_description.strip():
            return [{'field': 'meta_description', 'value': page.meta_description}]
        return []
    
    def _check_meta_description_too_long(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica meta description troppo lunga"""
        if page.meta_description and len(page.meta_description) > 160:
            return [{'field': 'meta_description', 'length': len(page.meta_description), 'max': 160}]
        return []
    
    def _check_meta_description_too_short(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica meta description troppo corta"""
        # Segnala solo se MOLTO corta (<30 caratteri) o su pagine importanti
        if page.meta_description:
            if len(page.meta_description) < 30:
                return [{'field': 'meta_description', 'length': len(page.meta_description), 'min': 50}]
            elif (page.is_product or page.is_category) and len(page.meta_description) < 50:
                return [{'field': 'meta_description', 'length': len(page.meta_description), 'min': 50}]
        return []
    
    def _check_canonical_missing(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica canonical mancante (solo su pagine importanti)"""
        # Segnala solo su pagine prodotto/categoria/filtri
        if (page.is_product or page.is_category or page.is_faceted_filter) and (not page.canonical or not page.canonical.strip()):
            return [{'field': 'canonical', 'value': page.canonical}]
        return []
    
    def _check_canonical_missing_product(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica canonical mancante su pagina prodotto"""
        if page.is_product and (not page.canonical or not page.canonical.strip()):
            return [{'field': 'canonical', 'page_type': 'product'}]
        return []
    
    def _check_images_missing_alt(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica immagini senza ALT"""
        if page.images_missing_alt > 0 or page.images_empty_alt > 0:
            return [{
                'field': 'images_alt',
                'missing': page.images_missing_alt,
                'empty': page.images_empty_alt,
                'total': page.images_total
            }]
        return []
    
    def _check_cart_indexable(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica pagine cart/checkout indicizzabili"""
        if page.is_cart_or_checkout and 'noindex' not in page.meta_robots.lower():
            return [{'field': 'robots', 'page_type': 'cart_checkout', 'current': page.meta_robots}]
        return []
    
    def _check_faceted_no_canonical(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica filtri faceted senza canonical"""
        if page.is_faceted_filter and (not page.canonical or page.canonical == page.url):
            # Parse URL per trovare parametri filtro
            parsed_url = urlparse(page.url)
            query_params = parse_qs(parsed_url.query)
            
            filter_params = []
            for param in ['selected_filters', 'facets', 'q']:
                if param in query_params:
                    filter_params.append(param)
            
            return [{
                'field': 'canonical',
                'page_type': 'faceted_filter',
                'filter_params': filter_params
            }]
        return []
    
    def _check_product_no_jsonld(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica prodotto senza JSON-LD Product"""
        if page.is_product and 'Product' not in page.jsonld_types:
            return [{'field': 'jsonld', 'page_type': 'product', 'types': page.jsonld_types}]
        return []
    
    def _check_category_no_pagination(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica categoria senza rel prev/next"""
        if page.is_category:
            # Verifica presenza di parametro page nell'URL
            parsed_url = urlparse(page.url)
            query_params = parse_qs(parsed_url.query)
            
            if 'page' in query_params or 'p' in query_params:
                # È una pagina paginata, dovrebbe avere rel prev/next
                # Questa verifica richiederebbe accesso ai tag <link rel="prev/next">
                # che non sono estratti nel parser base - si potrebbe estendere
                return [{'field': 'pagination', 'page_type': 'category'}]
        return []
    
    def _check_hreflang_missing(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica hreflang mancante - SOLO su prodotti/categorie multilingua"""
        # Segnala solo su pagine importanti (prodotto/categoria) in siti multilingua
        if not (page.is_product or page.is_category):
            return []

        url_lower = page.url.lower()
        has_lang_indicators = any([
            '/it/' in url_lower, '/en/' in url_lower, '/fr/' in url_lower,
            '/es/' in url_lower, '/de/' in url_lower,
            'id_lang=' in url_lower
        ])

        if has_lang_indicators and not page.hreflang_map:
            return [{'field': 'hreflang', 'detected_multilang': True}]
        return []
    
    def _check_og_title_missing(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica OpenGraph title mancante (solo su prodotti)"""
        # Segnala SOLO su prodotti (categoria troppo generico)
        if page.is_product and (not page.og_title or not page.og_title.strip()):
            return [{'field': 'og_title', 'value': page.og_title}]
        return []

    def _check_og_description_missing(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica OpenGraph description mancante (solo su prodotti)"""
        # Segnala SOLO su prodotti (categoria troppo generico)
        if page.is_product and (not page.og_description or not page.og_description.strip()):
            return [{'field': 'og_description', 'value': page.og_description}]
        return []

    def _check_og_image_missing(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica OpenGraph image mancante (solo su prodotti)"""
        # Segnala SOLO su prodotti
        if page.is_product and (not page.og_image or not page.og_image.strip()):
            return [{'field': 'og_image', 'value': page.og_image}]
        return []
    
    def _check_headings_hierarchy(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica gerarchia heading corretta"""
        # Solo su pagine prodotto/categoria dove è più importante
        if not (page.is_product or page.is_category):
            return []

        headings = page.headings_map
        if not headings:
            return []

        # Verifica sequenza logica H1->H2->H3...
        hierarchy_issues = []

        # Dovrebbe sempre iniziare con H1
        if 'h1' not in headings and any(f'h{i}' in headings for i in range(2, 7)):
            hierarchy_issues.append('missing_h1')

        # Verifica salti gravi (es. H1->H4 senza H2, H3)
        for level in range(1, 5):  # h1 to h4
            current = f'h{level}'
            skip_level = f'h{level + 2}'  # Salto di 2 livelli

            if current in headings and skip_level in headings and f'h{level + 1}' not in headings:
                hierarchy_issues.append(f'skip_{current}_to_{skip_level}')

        if hierarchy_issues:
            return [{'field': 'headings_hierarchy', 'issues': hierarchy_issues}]
        return []
    
    def _check_images_no_lazy_loading(self, page: PageData, images: List[ImageData]) -> List[dict]:
        """Verifica immagini senza lazy loading - DISABILITATO (troppo rumoroso)"""
        # DISABILITATO: lazy loading è nice-to-have ma non critico per SEO
        # e genera troppi falsi positivi su siti legacy
        return []


class DuplicateDetector:
    """Rilevatore contenuti duplicati"""
    
    def __init__(self):
        self.content_hashes: Dict[str, List[str]] = {}  # hash -> [urls]
    
    def add_page(self, page: PageData) -> List[str]:
        """Aggiunge pagina e restituisce URL duplicati rilevati"""
        content_hash = page.content_hash
        if not content_hash:
            return []
        
        if content_hash not in self.content_hashes:
            self.content_hashes[content_hash] = []
        
        # Controlla duplicati esistenti
        duplicates = self.content_hashes[content_hash].copy()
        
        # Aggiungi URL corrente
        self.content_hashes[content_hash].append(page.normalized_url)
        
        return duplicates
    
    def get_all_duplicates(self) -> List[Tuple[str, List[str]]]:
        """Restituisce tutti i gruppi di duplicati"""
        duplicates = []
        
        for content_hash, urls in self.content_hashes.items():
            if len(urls) > 1:
                duplicates.append((content_hash, urls))
        
        return duplicates
    
    def clear(self) -> None:
        """Pulisce cache duplicati"""
        self.content_hashes.clear()