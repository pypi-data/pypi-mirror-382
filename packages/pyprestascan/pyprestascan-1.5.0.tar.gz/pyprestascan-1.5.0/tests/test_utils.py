"""
Test per modulo utils
"""
import pytest

from pyprestascan.core.utils import URLNormalizer, PrestaShopDetector, TextAnalyzer


class TestURLNormalizer:
    """Test per URLNormalizer"""
    
    def setup_method(self):
        """Setup per ogni test"""
        self.normalizer = URLNormalizer("example.com")
    
    def test_normalize_basic(self):
        """Test normalizzazione base"""
        # Rimuove trailing slash
        assert self.normalizer.normalize("https://example.com/page/") == "https://example.com/page"
        
        # Mantiene root slash
        assert self.normalizer.normalize("https://example.com/") == "https://example.com/"
        
        # Rimuove fragment
        assert self.normalizer.normalize("https://example.com/page#section") == "https://example.com/page"
    
    def test_normalize_noisy_params(self):
        """Test rimozione parametri rumorosi"""
        url = "https://example.com/category?orderby=price&id_lang=1&page=2"
        result = self.normalizer.normalize(url)
        # Dovrebbe rimuovere parametri rumorosi PrestaShop
        assert "orderby" not in result
        assert "id_lang" not in result
        assert "page" not in result
    
    def test_normalize_preserve_clean_params(self):
        """Test preservazione parametri puliti"""
        url = "https://example.com/search?q=product&custom=value"
        result = self.normalizer.normalize(url, remove_noisy_params=False)
        assert "q=product" in result
        assert "custom=value" in result
    
    def test_is_same_domain(self):
        """Test verifica stesso dominio"""
        assert self.normalizer.is_same_domain("https://example.com/page")
        assert not self.normalizer.is_same_domain("https://other.com/page")
    
    def test_is_same_domain_subdomains(self):
        """Test con sottodomini"""
        normalizer = URLNormalizer("example.com", include_subdomains=True)
        assert normalizer.is_same_domain("https://shop.example.com/page")
        assert normalizer.is_same_domain("https://example.com/page")
        assert not normalizer.is_same_domain("https://other.com/page")
    
    def test_resolve_relative(self):
        """Test risoluzione URL relativi"""
        base = "https://example.com/category/"
        relative = "../product/item.html"
        result = self.normalizer.resolve_relative(base, relative)
        assert result == "https://example.com/product/item.html"


class TestPrestaShopDetector:
    """Test per PrestaShopDetector"""
    
    def test_is_prestashop_url(self):
        """Test rilevamento URL PrestaShop"""
        # URL prodotto tipico
        assert PrestaShopDetector.is_prestashop_url("https://shop.com/product-name-p123.html")
        
        # URL categoria tipico
        assert PrestaShopDetector.is_prestashop_url("https://shop.com/category/electronics-c45.html")
        
        # URL con parametri
        assert PrestaShopDetector.is_prestashop_url("https://shop.com/index.php?id_product=123")
        
        # URL normale (non PrestaShop)
        assert not PrestaShopDetector.is_prestashop_url("https://shop.com/about-us")
    
    def test_detect_page_type_from_url(self):
        """Test rilevamento tipo pagina da URL"""
        # Prodotto
        result = PrestaShopDetector.detect_page_type("https://shop.com/smartphone-p123.html")
        assert result['is_product'] is True
        assert result['is_category'] is False
        
        # Categoria
        result = PrestaShopDetector.detect_page_type("https://shop.com/electronics-c45.html")
        assert result['is_category'] is True
        assert result['is_product'] is False
        
        # Cart/Checkout
        result = PrestaShopDetector.detect_page_type("https://shop.com/cart")
        assert result['is_cart_or_checkout'] is True
        
        # Filtri faceted
        result = PrestaShopDetector.detect_page_type("https://shop.com/category?selected_filters=brand-apple")
        assert result['is_faceted_filter'] is True


class TestTextAnalyzer:
    """Test per TextAnalyzer"""
    
    def test_extract_visible_text(self):
        """Test estrazione testo visibile"""
        html = """
        <html>
            <head><title>Page Title</title></head>
            <body>
                <script>var x = 'hidden';</script>
                <style>.hidden { display: none; }</style>
                <h1>Main Heading</h1>
                <p>Visible paragraph text.</p>
                <div>Another visible text</div>
            </body>
        </html>
        """
        
        result = TextAnalyzer.extract_visible_text(html)
        
        # Dovrebbe contenere solo testo visibile
        assert "Main Heading" in result
        assert "Visible paragraph text" in result
        assert "Another visible text" in result
        
        # Non dovrebbe contenere script/style
        assert "var x =" not in result
        assert ".hidden" not in result
    
    def test_is_generic_alt(self):
        """Test rilevamento ALT generico"""
        # ALT generici
        assert TextAnalyzer.is_generic_alt("image")
        assert TextAnalyzer.is_generic_alt("foto")
        assert TextAnalyzer.is_generic_alt("banner")
        assert TextAnalyzer.is_generic_alt("placeholder")
        assert TextAnalyzer.is_generic_alt("")
        assert TextAnalyzer.is_generic_alt("   ")  # Solo spazi
        
        # ALT validi
        assert not TextAnalyzer.is_generic_alt("Smartphone Apple iPhone 15")
        assert not TextAnalyzer.is_generic_alt("Categoria Elettronica")
    
    def test_classify_alt_status(self):
        """Test classificazione status ALT"""
        assert TextAnalyzer.classify_alt_status(None) == "MISSING"
        assert TextAnalyzer.classify_alt_status("") == "EMPTY"
        assert TextAnalyzer.classify_alt_status("   ") == "EMPTY"
        assert TextAnalyzer.classify_alt_status("image") == "GENERIC"
        assert TextAnalyzer.classify_alt_status("iPhone 15 Pro") == "OK"
    
    def test_calculate_content_hash(self):
        """Test calcolo hash contenuto"""
        text1 = "Questo è un testo di esempio con data 01/01/2024 e prezzo 99,99€"
        text2 = "Questo è un testo di esempio con data 15/12/2023 e prezzo 149,50€"
        
        hash1 = TextAnalyzer.calculate_content_hash(text1)
        hash2 = TextAnalyzer.calculate_content_hash(text2)
        
        # Gli hash dovrebbero essere uguali (date e prezzi normalizzati)
        assert hash1 == hash2
        
        # Testo diverso dovrebbe avere hash diverso
        text3 = "Testo completamente diverso senza date o prezzi"
        hash3 = TextAnalyzer.calculate_content_hash(text3)
        assert hash1 != hash3


@pytest.mark.parametrize("url,expected_product,expected_category", [
    ("https://shop.com/smartphone-p123.html", True, False),
    ("https://shop.com/category/electronics-c45.html", False, True),
    ("https://shop.com/index.php?id_product=123", True, False),
    ("https://shop.com/index.php?id_category=45", False, True),
    ("https://shop.com/about-us", False, False),
])
def test_prestashop_url_detection_parametrized(url, expected_product, expected_category):
    """Test parametrizzato per rilevamento URL PrestaShop"""
    result = PrestaShopDetector.detect_page_type(url)
    assert result['is_product'] == expected_product
    assert result['is_category'] == expected_category