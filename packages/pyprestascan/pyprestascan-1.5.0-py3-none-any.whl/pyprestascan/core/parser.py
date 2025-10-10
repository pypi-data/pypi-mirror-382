"""
Parser HTML per estrazione dati SEO e analisi PrestaShop
"""
import re
import json
from typing import List, Dict, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

from selectolax.parser import HTMLParser
from selectolax.parser import Node

from .utils import PrestaShopDetector, TextAnalyzer, URLNormalizer
from .storage import PageData, ImageData
from .fetcher import FetchResponse


@dataclass
class ParsedData:
    """Dati estratti da una pagina"""
    page: PageData
    images: List[ImageData]
    links: List[str]  # URL interni da aggiungere alla coda


class SEOParser:
    """Parser SEO con euristiche specifiche PrestaShop"""
    
    def __init__(self, url_normalizer: URLNormalizer, prestashop_mode: bool = True):
        self.url_normalizer = url_normalizer
        self.prestashop_mode = prestashop_mode
        self.ps_detector = PrestaShopDetector()
        self.text_analyzer = TextAnalyzer()
    
    def parse(self, response: FetchResponse, depth: int = 0) -> ParsedData:
        """Parse completo di una response HTTP"""
        # Inizializza dati pagina con valori di default
        page_data = PageData(
            url=response.url,
            normalized_url=self.url_normalizer.normalize(response.url),
            status_code=response.status_code,
            ttfb_ms=response.ttfb_ms,
            content_type=response.content_type,
            content_length=response.content_length,
            title="",
            title_length=0,
            meta_description="",
            meta_description_length=0,
            meta_robots="",
            x_robots_tag="",
            canonical="",
            h1_count=0,
            headings_map={},
            internal_links_count=0,
            external_links_count=0,
            nofollow_links_count=0,
            hreflang_map={},
            og_title="",
            og_description="",
            og_image="",
            jsonld_types=[],
            images_total=0,
            images_missing_alt=0,
            images_empty_alt=0,
            images_generic_alt=0,
            is_product=False,
            is_category=False,
            is_cms=False,
            is_faceted_filter=False,
            is_cart_or_checkout=False,
            is_account=False,
            content_hash="",
            score=0.0,
            crawled_at=None,  # Sarà impostata dal crawler
            depth=depth
        )
        
        images = []
        internal_links = []
        
        # Se non è HTML o c'è errore, restituisci dati base
        if (response.status_code != 200 or 
            not response.text or 
            'text/html' not in response.content_type):
            return ParsedData(page=page_data, images=images, links=internal_links)
        
        try:
            # Parse HTML
            tree = HTMLParser(response.text)
            
            # Estrazione dati base
            page_data = self._extract_basic_seo(tree, page_data, response.url)
            
            # Estrazione links e immagini
            internal_links, page_data = self._extract_links(tree, page_data, response.url)
            images, page_data = self._extract_images(tree, page_data, response.url)
            
            # Rilevamento tipo pagina PrestaShop
            if self.prestashop_mode:
                page_data = self._detect_prestashop_features(tree, page_data, response.text)
            
            # Hash contenuto per duplicati
            visible_text = self.text_analyzer.extract_visible_text(response.text)
            page_data.content_hash = self.text_analyzer.calculate_content_hash(visible_text)
            
        except Exception as e:
            # In caso di errore parsing, mantieni dati base
            pass
        
        return ParsedData(page=page_data, images=images, links=internal_links)
    
    def _extract_basic_seo(self, tree: HTMLParser, page_data: PageData, base_url: str) -> PageData:
        """Estrae dati SEO di base"""
        
        # Title
        title_node = tree.css_first('title')
        if title_node and title_node.text():
            page_data.title = title_node.text().strip()
            page_data.title_length = len(page_data.title)
        
        # Meta description
        meta_desc = tree.css_first('meta[name="description" i]')
        if meta_desc:
            content = meta_desc.attributes.get('content', '')
            if content:
                page_data.meta_description = content.strip()
                page_data.meta_description_length = len(page_data.meta_description)
        
        # Meta robots
        meta_robots = tree.css_first('meta[name="robots" i]')
        if meta_robots:
            page_data.meta_robots = meta_robots.attributes.get('content', '').lower()
        
        # Canonical
        canonical_node = tree.css_first('link[rel="canonical" i]')
        if canonical_node:
            href = canonical_node.attributes.get('href', '')
            if href:
                page_data.canonical = urljoin(base_url, href)
        
        # Headings
        page_data.headings_map = self._extract_headings(tree)
        page_data.h1_count = page_data.headings_map.get('h1', 0)
        
        # OpenGraph
        page_data.og_title = self._extract_meta_property(tree, 'og:title')
        page_data.og_description = self._extract_meta_property(tree, 'og:description')
        page_data.og_image = self._extract_meta_property(tree, 'og:image')
        
        # Hreflang
        page_data.hreflang_map = self._extract_hreflang(tree, base_url)
        
        # JSON-LD
        page_data.jsonld_types = self._extract_jsonld_types(tree)
        
        return page_data
    
    def _extract_headings(self, tree: HTMLParser) -> Dict[str, int]:
        """Estrae conteggio heading per tipo"""
        headings_map = {}
        
        for level in range(1, 7):  # h1-h6
            tag = f'h{level}'
            nodes = tree.css(tag)
            count = len([node for node in nodes if node.text() and node.text().strip()])
            if count > 0:
                headings_map[tag] = count
        
        return headings_map
    
    def _extract_meta_property(self, tree: HTMLParser, property_name: str) -> str:
        """Estrae meta property OpenGraph/Twitter"""
        # Prova property
        node = tree.css_first(f'meta[property="{property_name}" i]')
        if not node:
            # Prova name (per Twitter)
            node = tree.css_first(f'meta[name="{property_name}" i]')
        
        if node:
            return node.attributes.get('content', '').strip()
        
        return ""
    
    def _extract_hreflang(self, tree: HTMLParser, base_url: str) -> Dict[str, str]:
        """Estrae link hreflang"""
        hreflang_map = {}
        
        hreflang_nodes = tree.css('link[rel="alternate"][hreflang]')
        for node in hreflang_nodes:
            hreflang = node.attributes.get('hreflang', '').strip()
            href = node.attributes.get('href', '').strip()
            
            if hreflang and href:
                absolute_url = urljoin(base_url, href)
                hreflang_map[hreflang] = absolute_url
        
        return hreflang_map
    
    def _extract_jsonld_types(self, tree: HTMLParser) -> List[str]:
        """Estrae tipi JSON-LD structured data"""
        types = set()
        
        json_scripts = tree.css('script[type="application/ld+json"]')
        for script in json_scripts:
            if not script.text():
                continue
            
            try:
                data = json.loads(script.text())
                
                # Gestisci sia singoli oggetti che array
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    if isinstance(item, dict) and '@type' in item:
                        schema_type = item['@type']
                        if isinstance(schema_type, str):
                            types.add(schema_type)
                        elif isinstance(schema_type, list):
                            types.update(schema_type)
            
            except (json.JSONDecodeError, TypeError):
                continue
        
        return sorted(list(types))
    
    def _extract_links(self, tree: HTMLParser, page_data: PageData, base_url: str) -> Tuple[List[str], PageData]:
        """Estrae tutti i link e aggiorna contatori"""
        internal_links = []
        internal_count = 0
        external_count = 0
        nofollow_count = 0
        
        links = tree.css('a[href]')
        
        for link in links:
            try:
                href = link.attributes.get('href', '').strip()
                if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    continue
                
                # Risolvi URL assoluto
                absolute_url = urljoin(base_url, href)
                rel = link.attributes.get('rel', '').lower()
                
                # Classifica link
                is_nofollow = 'nofollow' in rel
                is_internal = self.url_normalizer.is_same_domain(absolute_url)
                
                if is_nofollow:
                    nofollow_count += 1
                
                if is_internal:
                    internal_count += 1
                    # Normalizza e aggiungi a coda crawling
                    normalized = self.url_normalizer.normalize(absolute_url)
                    if normalized and normalized not in internal_links:
                        internal_links.append(normalized)
                else:
                    external_count += 1
            except Exception:
                # Skip link malformati
                continue
        
        page_data.internal_links_count = internal_count
        page_data.external_links_count = external_count
        page_data.nofollow_links_count = nofollow_count
        
        return internal_links, page_data
    
    def _extract_images(self, tree: HTMLParser, page_data: PageData, base_url: str) -> Tuple[List[ImageData], PageData]:
        """Estrae dati immagini con classificazione ALT"""
        images = []
        
        img_nodes = tree.css('img[src]')
        
        total_count = 0
        missing_alt = 0
        empty_alt = 0
        generic_alt = 0
        
        for img in img_nodes:
            src = img.attributes.get('src', '').strip()
            if not src:
                continue
            
            # URL assoluto immagine
            absolute_src = urljoin(base_url, src)
            
            # ALT text
            alt_text = img.attributes.get('alt')
            alt_status = self.text_analyzer.classify_alt_status(alt_text)
            
            # Dimensioni (se disponibili)
            width = self._safe_int(img.attributes.get('width'))
            height = self._safe_int(img.attributes.get('height'))
            
            # Attributi loading
            loading = img.attributes.get('loading', '').lower()
            if not loading:
                loading = None
            
            # Crea oggetto immagine
            image_data = ImageData(
                page_url=base_url,
                image_src=absolute_src,
                alt_text=alt_text,
                alt_status=alt_status,
                width=width,
                height=height,
                file_size=None,  # Non rilevabile da HTML
                loading_attr=loading
            )
            
            images.append(image_data)
            
            # Aggiorna contatori
            total_count += 1
            if alt_status == "MISSING":
                missing_alt += 1
            elif alt_status == "EMPTY":
                empty_alt += 1
            elif alt_status == "GENERIC":
                generic_alt += 1
        
        page_data.images_total = total_count
        page_data.images_missing_alt = missing_alt
        page_data.images_empty_alt = empty_alt
        page_data.images_generic_alt = generic_alt
        
        return images, page_data
    
    def _detect_prestashop_features(self, tree: HTMLParser, page_data: PageData, html_content: str) -> PageData:
        """Rileva caratteristiche specifiche PrestaShop"""
        
        # Rilevamento da URL (già fatto in utils)
        ps_types = self.ps_detector.detect_page_type(page_data.url, html_content)
        
        page_data.is_product = ps_types['is_product']
        page_data.is_category = ps_types['is_category']
        page_data.is_cms = ps_types['is_cms']
        page_data.is_faceted_filter = ps_types['is_faceted_filter']
        page_data.is_cart_or_checkout = ps_types['is_cart_or_checkout']
        page_data.is_account = ps_types['is_account']
        
        # Affina rilevamento basandosi su contenuto HTML
        self._refine_prestashop_detection(tree, page_data, html_content)
        
        return page_data
    
    def _refine_prestashop_detection(self, tree: HTMLParser, page_data: PageData, html_content: str) -> None:
        """Affina rilevamento PrestaShop basandosi su HTML"""
        
        # Rileva dalla presenza di meta generator
        generator = tree.css_first('meta[name="generator" i]')
        if generator and 'prestashop' in generator.attributes.get('content', '').lower():
            # Conferma PrestaShop
            pass
        
        # Rilevamento pagina prodotto da JSON-LD
        if 'Product' in page_data.jsonld_types:
            page_data.is_product = True
        
        # Rilevamento categoria da breadcrumb
        if 'BreadcrumbList' in page_data.jsonld_types:
            # Analizza breadcrumb per determinare se categoria
            breadcrumb_scripts = tree.css('script[type="application/ld+json"]')
            for script in breadcrumb_scripts:
                if not script.text():
                    continue
                try:
                    data = json.loads(script.text())
                    if (isinstance(data, dict) and 
                        data.get('@type') == 'BreadcrumbList' and
                        'itemListElement' in data):
                        
                        items = data['itemListElement']
                        if len(items) > 1:  # Ha breadcrumb con più livelli
                            last_item = items[-1]
                            if isinstance(last_item, dict) and 'item' in last_item:
                                item_url = last_item['item'].get('url', '')
                                if '/category/' in item_url.lower() or '-c' in item_url:
                                    page_data.is_category = True
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Rilevamento filtri faceted search
        url_lower = page_data.url.lower()
        if ('selected_filters=' in url_lower or 
            'facets=' in url_lower or
            '?q=' in url_lower):
            page_data.is_faceted_filter = True
        
        # Rilevamento pagine transazionali SOLO da URL e body class specifici
        url_lower = page_data.url.lower()
        is_cart_url = any(keyword in url_lower for keyword in ['/cart', '/order', '/checkout', 'controller=cart', 'controller=order'])

        if (is_cart_url or
            tree.css_first('body.page-cart') or  # Body class PrestaShop specifico
            tree.css_first('body.page-order') or
            tree.css_first('body.page-checkout') or
            tree.css_first('body[id="cart"]') or
            tree.css_first('body[id="order"]')):
            page_data.is_cart_or_checkout = True
        
        # Rilevamento account da form login/register
        if (tree.css_first('form[action*="authentication"]') or
            tree.css_first('form[action*="login"]') or
            tree.css_first('.account') or
            tree.css_first('#login') or
            'my-account' in url_lower):
            page_data.is_account = True
    
    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        """Conversione sicura stringa -> int"""
        if not value:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def extract_sitemap_urls(self, sitemap_content: str) -> List[str]:
        """Estrae URL da contenuto sitemap XML"""
        urls = []
        
        try:
            # Parse XML semplificato con regex
            loc_pattern = r'<loc>(.*?)</loc>'
            matches = re.findall(loc_pattern, sitemap_content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                url = match.strip()
                if url and url.startswith(('http://', 'https://')):
                    normalized = self.url_normalizer.normalize(url)
                    if normalized and self.url_normalizer.is_same_domain(normalized):
                        urls.append(normalized)
        
        except Exception:
            pass
        
        return urls