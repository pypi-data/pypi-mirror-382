"""
Test per modulo CLI
"""
import pytest
from click.testing import CliRunner

from pyprestascan.cli import CrawlConfig, main
from pyprestascan.cli import parse_lang_map


class TestCrawlConfig:
    """Test per CrawlConfig"""
    
    def test_config_defaults(self):
        """Test valori default configurazione"""
        config = CrawlConfig(url="https://example.com")
        
        assert config.max_urls == 10000
        assert config.concurrency == 20
        assert config.delay == 0
        assert config.timeout == 15
        assert config.sitemap == "auto"
        assert config.include_subdomains is False
        assert config.prestashop_mode is True
        assert len(config.include_patterns) == 0
        assert len(config.exclude_patterns) == 0
    
    def test_config_validation_max_urls(self):
        """Test validazione max_urls"""
        # Valore valido
        config = CrawlConfig(url="https://example.com", max_urls=5000)
        assert config.max_urls == 5000
        
        # Valore non valido (dovrebbe fallire)
        with pytest.raises(ValueError):
            CrawlConfig(url="https://example.com", max_urls=0)
    
    def test_config_validation_concurrency(self):
        """Test validazione concurrency"""
        # Valore valido
        config = CrawlConfig(url="https://example.com", concurrency=50)
        assert config.concurrency == 50
        
        # Valore troppo alto (dovrebbe fallire)
        with pytest.raises(ValueError):
            CrawlConfig(url="https://example.com", concurrency=150)
    
    def test_config_validation_sitemap(self):
        """Test validazione sitemap"""
        # Valori validi
        for value in ["auto", "true", "false"]:
            config = CrawlConfig(url="https://example.com", sitemap=value)
            assert config.sitemap == value
        
        # Valore non valido
        with pytest.raises(ValueError):
            CrawlConfig(url="https://example.com", sitemap="invalid")
    
    def test_config_regex_patterns_validation(self):
        """Test validazione pattern regex"""
        # Pattern validi
        config = CrawlConfig(
            url="https://example.com",
            include_patterns=[r"/category/.*", r"\d+-p\d+\.html"],
            exclude_patterns=[r"\?.*sort="]
        )
        assert len(config.include_patterns) == 2
        assert len(config.exclude_patterns) == 1
        
        # Pattern regex non valido
        with pytest.raises(ValueError):
            CrawlConfig(
                url="https://example.com",
                include_patterns=[r"[invalid regex"]
            )
    
    def test_config_lang_map_parsing(self):
        """Test parsing lang_map"""
        # Da stringa
        config = CrawlConfig(
            url="https://example.com",
            lang_map="it=it,en=en,fr=fr"
        )
        expected = {"it": "it", "en": "en", "fr": "fr"}
        assert config.lang_map == expected
        
        # Da dict (già processato)
        config = CrawlConfig(
            url="https://example.com",
            lang_map={"de": "de", "es": "es"}
        )
        assert config.lang_map == {"de": "de", "es": "es"}


class TestLangMapParser:
    """Test per parser lang_map"""
    
    def test_parse_lang_map_valid(self):
        """Test parsing valido"""
        # Caso normale
        result = parse_lang_map(None, None, "it=it,en=en,fr=fr")
        expected = {"it": "it", "en": "en", "fr": "fr"}
        assert result == expected
        
        # Con spazi
        result = parse_lang_map(None, None, "it = it , en = en")
        expected = {"it": "it", "en": "en"}
        assert result == expected
    
    def test_parse_lang_map_empty(self):
        """Test parsing stringa vuota"""
        result = parse_lang_map(None, None, "")
        assert result == {}
        
        result = parse_lang_map(None, None, None)
        assert result == {}
    
    def test_parse_lang_map_invalid(self):
        """Test parsing non valido"""
        from click import BadParameter
        
        # Formato sbagliato
        with pytest.raises(BadParameter):
            parse_lang_map(None, None, "invalid_format")
        
        with pytest.raises(BadParameter):
            parse_lang_map(None, None, "it=it,invalid")


class TestCLI:
    """Test per interfaccia CLI"""
    
    def setup_method(self):
        """Setup per ogni test"""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test output help"""
        result = self.runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert 'PyPrestaScan' in result.output
        assert '--url' in result.output
        assert '--max-urls' in result.output
    
    def test_cli_missing_url(self):
        """Test CLI senza URL richiesto"""
        result = self.runner.invoke(main, [])
        
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()
    
    def test_cli_basic_invocation(self):
        """Test invocazione CLI base"""
        # Nota: questo test non eseguirà il crawling reale
        # perché non abbiamo un server di test, ma verifica
        # che i parametri siano processati correttamente
        
        result = self.runner.invoke(main, [
            '--url', 'https://example.com',
            '--max-urls', '100',
            '--concurrency', '5',
            '--debug'
        ], catch_exceptions=False)
        
        # Il comando dovrebbe iniziare (potrebbe fallire dopo per network)
        # ma i parametri dovrebbero essere processati correttamente
        # L'exit code dipende dalla disponibilità di example.com
    
    def test_cli_invalid_parameters(self):
        """Test parametri CLI non validi"""
        # Concurrency troppo alta
        result = self.runner.invoke(main, [
            '--url', 'https://example.com',
            '--concurrency', '200'
        ])
        
        assert result.exit_code != 0
        
        # Max URLs zero
        result = self.runner.invoke(main, [
            '--url', 'https://example.com',
            '--max-urls', '0'
        ])
        
        assert result.exit_code != 0
    
    def test_cli_pattern_parameters(self):
        """Test parametri pattern"""
        # Test che i pattern vengano accettati
        result = self.runner.invoke(main, [
            '--url', 'https://example.com',
            '--include', '/category/',
            '--include', r'\d+-p\d+\.html',
            '--exclude', r'\?.*sort=',
            '--max-urls', '10'  # Piccolo per test veloce
        ], catch_exceptions=False)
        
        # Dovrebbe processare i parametri senza errori di parsing
        # (il fallimento sarà probabilmente di rete)
    
    def test_cli_boolean_flags(self):
        """Test flag booleani"""
        result = self.runner.invoke(main, [
            '--url', 'https://example.com',
            '--include-subdomains',
            '--resume',
            '--include-generic',
            '--debug',
            '--quiet',
            '--no-color'
        ], catch_exceptions=False)
        
        # Flag dovrebbero essere processati correttamente
    
    def test_cli_project_and_export_dir(self):
        """Test parametri progetto e directory"""
        result = self.runner.invoke(main, [
            '--url', 'https://example.com',
            '--project', 'test-project',
            '--export-dir', '/tmp/test-reports'
        ], catch_exceptions=False)
        
        # Parametri dovrebbero essere processati
    
    def test_cli_auth_parameters(self):
        """Test parametri autenticazione"""
        result = self.runner.invoke(main, [
            '--url', 'https://example.com',
            '--auth-user', 'testuser',
            '--auth-pass', 'testpass'
        ], catch_exceptions=False)
        
        # Parametri auth dovrebbero essere accettati
    
    def test_cli_lang_map_parameter(self):
        """Test parametro lang-map"""
        result = self.runner.invoke(main, [
            '--url', 'https://example.com',
            '--lang-map', 'it=it,en=en,fr=fr'
        ], catch_exceptions=False)
        
        # Lang map dovrebbe essere processata
        
        # Test formato non valido
        result = self.runner.invoke(main, [
            '--url', 'https://example.com',
            '--lang-map', 'invalid-format'
        ])
        
        assert result.exit_code != 0


@pytest.mark.integration
class TestCLIIntegration:
    """Test di integrazione CLI (opzionali, richiedono network)"""
    
    def setup_method(self):
        """Setup per test integrazione"""
        self.runner = CliRunner()
    
    @pytest.mark.skip(reason="Richiede connessione di rete")
    def test_cli_real_crawl_small(self):
        """Test crawling reale su esempio piccolo"""
        # Test solo se abbiamo un sito di test disponibile
        result = self.runner.invoke(main, [
            '--url', 'https://httpbin.org',  # Sito di test
            '--max-urls', '5',
            '--concurrency', '2',
            '--timeout', '10'
        ])
        
        # Dovrebbe completare senza errori critici
        assert result.exit_code in [0, 1]  # 0=successo, 1=errori minori