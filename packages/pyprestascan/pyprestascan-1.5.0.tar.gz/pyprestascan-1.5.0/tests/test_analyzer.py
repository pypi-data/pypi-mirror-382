"""
Test per modulo analyzer
"""
import pytest
from datetime import datetime

from pyprestascan.core.analyzer import SEORuleEngine, DuplicateDetector
from pyprestascan.core.storage import PageData, ImageData
from pyprestascan.core.parser import ParsedData


class TestSEORuleEngine:
    """Test per SEORuleEngine"""
    
    def setup_method(self):
        """Setup per ogni test"""
        self.engine = SEORuleEngine(prestashop_mode=True)
    
    def create_test_page(self, **kwargs):
        """Crea PageData di test con valori default"""
        defaults = {
            'url': 'https://example.com/test',
            'normalized_url': 'https://example.com/test',
            'status_code': 200,
            'ttfb_ms': 100,
            'content_type': 'text/html',
            'content_length': 1000,
            'title': 'Test Page Title',
            'title_length': 15,
            'meta_description': 'This is a test meta description for the page',
            'meta_description_length': 48,
            'meta_robots': '',
            'x_robots_tag': '',
            'canonical': 'https://example.com/test',
            'h1_count': 1,
            'headings_map': {'h1': 1, 'h2': 2},
            'internal_links_count': 10,
            'external_links_count': 2,
            'nofollow_links_count': 0,
            'hreflang_map': {},
            'og_title': 'Test OG Title',
            'og_description': 'Test OG Description',
            'og_image': 'https://example.com/image.jpg',
            'jsonld_types': [],
            'images_total': 5,
            'images_missing_alt': 0,
            'images_empty_alt': 0,
            'images_generic_alt': 0,
            'is_product': False,
            'is_category': False,
            'is_cms': False,
            'is_faceted_filter': False,
            'is_cart_or_checkout': False,
            'is_account': False,
            'content_hash': 'abc123',
            'score': 0.0,
            'crawled_at': datetime.now(),
            'depth': 0
        }
        defaults.update(kwargs)
        return PageData(**defaults)
    
    def test_title_missing_rule(self):
        """Test regola title mancante"""
        # Pagina senza title
        page = self.create_test_page(title='')
        parsed_data = ParsedData(page=page, images=[], links=[])
        
        issues, score = self.engine.analyze_page(parsed_data)
        
        # Dovrebbe rilevare issue title mancante
        title_issues = [i for i in issues if i.code == 'TITLE_MISSING']
        assert len(title_issues) > 0
        assert score < 100  # Score penalizzato
    
    def test_h1_multiple_rule(self):
        """Test regola H1 multipli"""
        # Pagina con H1 multipli
        page = self.create_test_page(h1_count=3, headings_map={'h1': 3})
        parsed_data = ParsedData(page=page, images=[], links=[])
        
        issues, score = self.engine.analyze_page(parsed_data)
        
        # Dovrebbe rilevare issue H1 multipli
        h1_issues = [i for i in issues if i.code == 'H1_MULTIPLE']
        assert len(h1_issues) > 0
    
    def test_meta_description_too_long_rule(self):
        """Test regola meta description troppo lunga"""
        long_desc = "x" * 200  # 200 caratteri
        page = self.create_test_page(
            meta_description=long_desc,
            meta_description_length=len(long_desc)
        )
        parsed_data = ParsedData(page=page, images=[], links=[])
        
        issues, score = self.engine.analyze_page(parsed_data)
        
        # Dovrebbe rilevare issue meta description troppo lunga
        desc_issues = [i for i in issues if i.code == 'META_DESCRIPTION_TOO_LONG']
        assert len(desc_issues) > 0
    
    def test_images_missing_alt_rule(self):
        """Test regola immagini senza ALT"""
        page = self.create_test_page(
            images_missing_alt=3,
            images_empty_alt=2,
            images_total=10
        )
        parsed_data = ParsedData(page=page, images=[], links=[])
        
        issues, score = self.engine.analyze_page(parsed_data)
        
        # Dovrebbe rilevare issue immagini senza ALT
        img_issues = [i for i in issues if i.code == 'IMAGES_MISSING_ALT']
        assert len(img_issues) > 0
    
    def test_prestashop_product_no_canonical(self):
        """Test regola prodotto PrestaShop senza canonical"""
        page = self.create_test_page(
            is_product=True,
            canonical=''  # Canonical mancante
        )
        parsed_data = ParsedData(page=page, images=[], links=[])
        
        issues, score = self.engine.analyze_page(parsed_data)
        
        # Dovrebbe rilevare issue canonical mancante su prodotto
        canonical_issues = [i for i in issues if i.code == 'CANONICAL_MISSING_PRODUCT']
        assert len(canonical_issues) > 0
    
    def test_prestashop_cart_indexable(self):
        """Test regola cart/checkout indicizzabile"""
        page = self.create_test_page(
            is_cart_or_checkout=True,
            meta_robots=''  # Senza noindex
        )
        parsed_data = ParsedData(page=page, images=[], links=[])
        
        issues, score = self.engine.analyze_page(parsed_data)
        
        # Dovrebbe rilevare issue cart indicizzabile
        cart_issues = [i for i in issues if i.code == 'CART_INDEXABLE']
        assert len(cart_issues) > 0
    
    def test_prestashop_product_no_jsonld(self):
        """Test regola prodotto senza JSON-LD"""
        page = self.create_test_page(
            is_product=True,
            jsonld_types=[]  # Senza Product schema
        )
        parsed_data = ParsedData(page=page, images=[], links=[])
        
        issues, score = self.engine.analyze_page(parsed_data)
        
        # Dovrebbe rilevare issue prodotto senza JSON-LD
        jsonld_issues = [i for i in issues if i.code == 'PRODUCT_NO_JSONLD']
        assert len(jsonld_issues) > 0
    
    def test_score_calculation_perfect_page(self):
        """Test calcolo score per pagina perfetta"""
        page = self.create_test_page(
            title='Perfect SEO Title',
            title_length=17,
            meta_description='Perfect meta description with right length for SEO optimization',
            meta_description_length=65,
            h1_count=1,
            canonical='https://example.com/test',
            is_product=True,
            jsonld_types=['Product']
        )
        parsed_data = ParsedData(page=page, images=[], links=[])
        
        issues, score = self.engine.analyze_page(parsed_data)
        
        # Pagina perfetta dovrebbe avere score alto
        assert score >= 90
        
        # Issues dovrebbero essere minimi
        critical_issues = [i for i in issues if i.severity == 'CRITICAL']
        assert len(critical_issues) == 0
    
    def test_prestashop_mode_disabled(self):
        """Test con modalità PrestaShop disabilitata"""
        engine = SEORuleEngine(prestashop_mode=False)
        
        page = self.create_test_page(
            is_product=True,
            canonical='',  # Canonical mancante
            jsonld_types=[]  # JSON-LD mancante
        )
        parsed_data = ParsedData(page=page, images=[], links=[])
        
        issues, score = engine.analyze_page(parsed_data)
        
        # Non dovrebbe rilevare issues PrestaShop-specifici
        ps_issues = [i for i in issues if 'PRODUCT' in i.code or 'CANONICAL_MISSING_PRODUCT' in i.code]
        assert len(ps_issues) == 0


class TestDuplicateDetector:
    """Test per DuplicateDetector"""
    
    def setup_method(self):
        """Setup per ogni test"""
        self.detector = DuplicateDetector()
    
    def create_test_page(self, url, content_hash):
        """Crea PageData di test"""
        return PageData(
            url=url,
            normalized_url=url,
            status_code=200,
            ttfb_ms=100,
            content_type='text/html',
            content_length=1000,
            title='Test',
            title_length=4,
            meta_description='Test desc',
            meta_description_length=9,
            meta_robots='',
            x_robots_tag='',
            canonical='',
            h1_count=1,
            headings_map={},
            internal_links_count=0,
            external_links_count=0,
            nofollow_links_count=0,
            hreflang_map={},
            og_title='',
            og_description='',
            og_image='',
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
            content_hash=content_hash,
            score=0.0,
            crawled_at=datetime.now(),
            depth=0
        )
    
    def test_no_duplicates_initially(self):
        """Test nessun duplicato inizialmente"""
        page = self.create_test_page('https://example.com/page1', 'hash1')
        
        duplicates = self.detector.add_page(page)
        
        assert len(duplicates) == 0
    
    def test_detect_duplicates(self):
        """Test rilevamento duplicati"""
        # Prima pagina
        page1 = self.create_test_page('https://example.com/page1', 'same_hash')
        duplicates1 = self.detector.add_page(page1)
        assert len(duplicates1) == 0
        
        # Seconda pagina con stesso hash
        page2 = self.create_test_page('https://example.com/page2', 'same_hash')
        duplicates2 = self.detector.add_page(page2)
        
        # Dovrebbe rilevare duplicato
        assert len(duplicates2) == 1
        assert duplicates2[0] == 'https://example.com/page1'
        
        # Terza pagina con stesso hash
        page3 = self.create_test_page('https://example.com/page3', 'same_hash')
        duplicates3 = self.detector.add_page(page3)
        
        # Dovrebbe rilevare entrambi i duplicati precedenti
        assert len(duplicates3) == 2
        assert 'https://example.com/page1' in duplicates3
        assert 'https://example.com/page2' in duplicates3
    
    def test_different_hashes_no_duplicates(self):
        """Test hash diversi non generano duplicati"""
        page1 = self.create_test_page('https://example.com/page1', 'hash1')
        page2 = self.create_test_page('https://example.com/page2', 'hash2')
        page3 = self.create_test_page('https://example.com/page3', 'hash3')
        
        self.detector.add_page(page1)
        duplicates2 = self.detector.add_page(page2)
        duplicates3 = self.detector.add_page(page3)
        
        assert len(duplicates2) == 0
        assert len(duplicates3) == 0
    
    def test_get_all_duplicates(self):
        """Test ottenimento tutti i duplicati"""
        # Aggiungi pagine con duplicati
        self.detector.add_page(self.create_test_page('https://example.com/page1', 'hash1'))
        self.detector.add_page(self.create_test_page('https://example.com/page2', 'hash1'))
        self.detector.add_page(self.create_test_page('https://example.com/page3', 'hash2'))
        self.detector.add_page(self.create_test_page('https://example.com/page4', 'hash2'))
        self.detector.add_page(self.create_test_page('https://example.com/page5', 'hash3'))  # Unico
        
        all_duplicates = self.detector.get_all_duplicates()
        
        # Dovrebbe trovare 2 gruppi di duplicati
        assert len(all_duplicates) == 2
        
        # Verifica gruppi
        hash1_group = next(group for hash, group in all_duplicates if hash == 'hash1')
        hash2_group = next(group for hash, group in all_duplicates if hash == 'hash2')
        
        assert len(hash1_group) == 2
        assert len(hash2_group) == 2
    
    def test_clear(self):
        """Test pulizia cache"""
        self.detector.add_page(self.create_test_page('https://example.com/page1', 'hash1'))
        self.detector.add_page(self.create_test_page('https://example.com/page2', 'hash1'))
        
        # Verifica che ci siano duplicati
        assert len(self.detector.get_all_duplicates()) == 1
        
        # Pulisci cache
        self.detector.clear()
        
        # Non dovrebbe più esserci nulla
        assert len(self.detector.get_all_duplicates()) == 0