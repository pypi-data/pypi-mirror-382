"""
Modulo per generazione e applicazione fix SEO automatici
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import re
import hashlib
from datetime import datetime
import asyncio

from .storage import CrawlDatabase, PageData, IssueData, FixData
import json

# Import AI providers (opzionale)
try:
    from pyprestascan.ai import AIProviderFactory, CostEstimator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


@dataclass
class FixSuggestion:
    """Rappresenta un fix suggerito per un issue SEO"""
    fix_id: str  # Hash univoco del fix
    issue_code: str  # Codice issue (es: META_DESCRIPTION_MISSING)
    page_url: str
    page_id: int  # ID pagina nel DB
    fix_type: str  # Tipo fix: meta_description, title, alt_text, canonical, etc.
    severity: str  # CRITICAL, WARNING, INFO
    current_value: str
    suggested_value: str
    confidence: float  # 0.0 - 1.0
    automated: bool  # Se può essere applicato automaticamente
    sql_query: Optional[str]  # Query SQL per fix manuale
    api_endpoint: Optional[str]  # Endpoint API PrestaShop
    api_payload: Optional[Dict[str, Any]]  # Payload per API
    explanation: str  # Spiegazione del fix
    created_at: datetime


class FixGenerator:
    """Classe base per generatori di fix specifici"""

    def __init__(self, db: CrawlDatabase):
        self.db = db

    def generate_fixes(self, issues: List[IssueData], pages: List[PageData]) -> List[FixSuggestion]:
        """Genera fix per gli issues forniti"""
        raise NotImplementedError("Subclass must implement generate_fixes")

    def _create_fix_id(self, page_url: str, fix_type: str) -> str:
        """Crea ID univoco per un fix"""
        content = f"{page_url}:{fix_type}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


class MetaDescriptionFixer(FixGenerator):
    """Genera fix per meta description mancanti o errate"""

    def __init__(self, db: CrawlDatabase, ai_provider: Optional[str] = None, ai_api_key: Optional[str] = None):
        super().__init__(db)
        self.ai_provider = None

        # Inizializza AI se disponibile
        if AI_AVAILABLE and ai_provider and ai_api_key:
            try:
                self.ai_provider = AIProviderFactory.create(ai_provider, ai_api_key)
            except Exception as e:
                print(f"⚠️  AI provider non disponibile: {e}. Usando generazione template.")

    def generate_fixes(self, issues: List[IssueData], pages: List[PageData]) -> List[FixSuggestion]:
        fixes = []

        # Crea mappa issues per page_url
        issues_by_page = {}
        for issue in issues:
            if issue.code in ['META_DESCRIPTION_MISSING', 'META_DESCRIPTION_TOO_SHORT', 'META_DESCRIPTION_TOO_LONG']:
                issues_by_page[issue.page_url] = issue

        # Crea mappa pages per URL
        pages_by_url = {page.url: page for page in pages}

        # Se AI è disponibile, genera in batch (molto più efficiente)
        if self.ai_provider:
            fixes = self._generate_fixes_with_ai(issues_by_page, pages_by_url)
        else:
            # Fallback a generazione template
            for page_url, issue in issues_by_page.items():
                page = pages_by_url.get(page_url)
                if not page:
                    continue

                # Genera meta description suggerita
                suggested_desc = self._generate_meta_description(page)

                if suggested_desc:
                    confidence = self._calculate_confidence(page, suggested_desc)

                    fix = FixSuggestion(
                        fix_id=self._create_fix_id(page_url, 'meta_description'),
                        issue_code=issue.code,
                        page_url=page_url,
                        page_id=0,
                        fix_type='meta_description',
                        severity=issue.severity,
                        current_value=page.meta_description or "(vuoto)",
                        suggested_value=suggested_desc,
                        confidence=confidence,
                        automated=confidence >= 0.7,
                        sql_query=self._generate_sql(page, suggested_desc),
                        api_endpoint=self._get_api_endpoint(page),
                        api_payload=self._generate_api_payload(page, suggested_desc),
                        explanation=self._get_explanation(issue.code),
                        created_at=datetime.now()
                    )
                    fixes.append(fix)

        return fixes

    def _generate_fixes_with_ai(self, issues_by_page: Dict, pages_by_url: Dict) -> List[FixSuggestion]:
        """Genera fix usando AI in batch (ottimizzato per pochi token)"""
        fixes = []

        # Prepara batch items (max 20 alla volta per non esplodere i token)
        batch_items = []
        page_mapping = []

        for page_url, issue in list(issues_by_page.items())[:20]:  # Limita a 20
            page = pages_by_url.get(page_url)
            if not page or not page.title:
                continue

            page_type = "prodotto" if page.is_product else ("categoria" if page.is_category else "cms")

            batch_items.append({
                'title': page.title,
                'page_type': page_type,
                'url': page_url
            })
            page_mapping.append((page_url, issue, page))

        if not batch_items:
            return fixes

        # Chiamata AI batch (UNA SOLA chiamata per tutti gli item!)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            ai_results = loop.run_until_complete(self.ai_provider.generate_batch(batch_items))

            # Crea fix da risultati AI
            for (page_url, issue, page), ai_result in zip(page_mapping, ai_results):
                fix = FixSuggestion(
                    fix_id=self._create_fix_id(page_url, 'meta_description'),
                    issue_code=issue.code,
                    page_url=page_url,
                    page_id=0,
                    fix_type='meta_description',
                    severity=issue.severity,
                    current_value=page.meta_description or "(vuoto)",
                    suggested_value=ai_result.meta_description,
                    confidence=ai_result.confidence,
                    automated=True,  # AI è sempre automatable
                    sql_query=self._generate_sql(page, ai_result.meta_description),
                    api_endpoint=self._get_api_endpoint(page),
                    api_payload=self._generate_api_payload(page, ai_result.meta_description),
                    explanation=f"Generato da AI ({ai_result.provider}) - {ai_result.tokens_used} token. " + self._get_explanation(issue.code),
                    created_at=datetime.now()
                )
                fixes.append(fix)

        except Exception as e:
            print(f"⚠️  Errore AI: {e}. Fallback a generazione template.")
            # Fallback a template per gli item falliti
            for page_url, issue, page in page_mapping:
                suggested_desc = self._generate_meta_description(page)
                if suggested_desc:
                    fix = FixSuggestion(
                        fix_id=self._create_fix_id(page_url, 'meta_description'),
                        issue_code=issue.code,
                        page_url=page_url,
                        page_id=0,
                        fix_type='meta_description',
                        severity=issue.severity,
                        current_value=page.meta_description or "(vuoto)",
                        suggested_value=suggested_desc,
                        confidence=self._calculate_confidence(page, suggested_desc),
                        automated=True,
                        sql_query=self._generate_sql(page, suggested_desc),
                        api_endpoint=self._get_api_endpoint(page),
                        api_payload=self._generate_api_payload(page, suggested_desc),
                        explanation=self._get_explanation(issue.code),
                        created_at=datetime.now()
                    )
                    fixes.append(fix)

        return fixes

    def _generate_meta_description(self, page: PageData) -> Optional[str]:
        """Genera meta description ottimizzata"""
        # Strategia 1: Usa title + prime 100 char del contenuto (simulato)
        if page.title:
            # Limita a 150-160 caratteri
            base_desc = page.title

            # Aggiungi tipo pagina se disponibile
            if page.is_product:
                base_desc += " - Acquista online su " + self._extract_domain(page.url)
            elif page.is_category:
                base_desc += " - Scopri tutti i prodotti disponibili"
            elif page.is_cms:
                base_desc += " - Informazioni e dettagli"

            # Tronca a 160 caratteri
            if len(base_desc) > 160:
                base_desc = base_desc[:157] + "..."

            # Assicurati sia almeno 50 caratteri
            if len(base_desc) < 50:
                base_desc += " - Visita il nostro sito per scoprire di più."

            return base_desc

        return None

    def _calculate_confidence(self, page: PageData, suggested: str) -> float:
        """Calcola confidence del fix"""
        confidence = 0.5  # Base

        # Aumenta se ha title valido
        if page.title and len(page.title) > 10:
            confidence += 0.2

        # Aumenta se lunghezza ottimale
        if 50 <= len(suggested) <= 160:
            confidence += 0.2

        # Aumenta se è pagina prodotto/categoria (più info disponibili)
        if page.is_product or page.is_category:
            confidence += 0.1

        return min(1.0, confidence)

    def _generate_sql(self, page: PageData, description: str) -> str:
        """Genera query SQL per fix manuale"""
        # Estrai ID prodotto/categoria dall'URL
        page_id = self._extract_page_id(page.url)

        if page.is_product:
            return f"""
-- Fix meta description per prodotto
UPDATE ps_product_lang
SET meta_description = '{description.replace("'", "''")}'
WHERE id_product = {page_id} AND id_lang = 1;
"""
        elif page.is_category:
            return f"""
-- Fix meta description per categoria
UPDATE ps_category_lang
SET meta_description = '{description.replace("'", "''")}'
WHERE id_category = {page_id} AND id_lang = 1;
"""
        elif page.is_cms:
            return f"""
-- Fix meta description per CMS
UPDATE ps_cms_lang
SET meta_description = '{description.replace("'", "''")}'
WHERE id_cms = {page_id} AND id_lang = 1;
"""
        else:
            return "-- Tipo pagina non supportato per SQL fix automatico"

    def _get_api_endpoint(self, page: PageData) -> Optional[str]:
        """Ottieni endpoint API PrestaShop"""
        page_id = self._extract_page_id(page.url)

        if page.is_product:
            return f"/api/products/{page_id}"
        elif page.is_category:
            return f"/api/categories/{page_id}"
        elif page.is_cms:
            return f"/api/content_management_system/{page_id}"

        return None

    def _generate_api_payload(self, page: PageData, description: str) -> Optional[Dict[str, Any]]:
        """Genera payload per API PrestaShop"""
        if page.is_product:
            return {
                "product": {
                    "meta_description": {
                        "language": [{"@id": "1", "#text": description}]
                    }
                }
            }
        elif page.is_category:
            return {
                "category": {
                    "meta_description": {
                        "language": [{"@id": "1", "#text": description}]
                    }
                }
            }
        elif page.is_cms:
            return {
                "content": {
                    "meta_description": {
                        "language": [{"@id": "1", "#text": description}]
                    }
                }
            }

        return None

    def _extract_page_id(self, url: str) -> int:
        """Estrae ID pagina dall'URL PrestaShop"""
        # Pattern comuni: /123-nome o ?id_product=123
        patterns = [
            r'/(\d+)-',  # /123-nome-prodotto
            r'id_product=(\d+)',
            r'id_category=(\d+)',
            r'id_cms=(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return int(match.group(1))

        return 0  # Sconosciuto

    def _extract_domain(self, url: str) -> str:
        """Estrae dominio dall'URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

    def _get_explanation(self, issue_code: str) -> str:
        """Ottieni spiegazione del fix"""
        explanations = {
            'META_DESCRIPTION_MISSING': 'La meta description è fondamentale per il CTR in SERP. Aggiungendo una description accattivante di 120-160 caratteri, aumenti le probabilità di click.',
            'META_DESCRIPTION_TOO_SHORT': 'Una meta description troppo corta (< 50 caratteri) non fornisce informazioni sufficienti agli utenti in SERP.',
            'META_DESCRIPTION_TOO_LONG': 'Una meta description oltre 160 caratteri viene troncata da Google, perdendo parte del messaggio.'
        }
        return explanations.get(issue_code, '')


class TitleFixer(FixGenerator):
    """Genera fix per title mancanti o errati"""

    def generate_fixes(self, issues: List[IssueData], pages: List[PageData]) -> List[FixSuggestion]:
        fixes = []

        issues_by_page = {}
        for issue in issues:
            if issue.code in ['TITLE_MISSING', 'TITLE_TOO_SHORT', 'TITLE_TOO_LONG']:
                issues_by_page[issue.page_url] = issue

        pages_by_url = {page.url: page for page in pages}

        for page_url, issue in issues_by_page.items():
            page = pages_by_url.get(page_url)
            if not page:
                continue

            suggested_title = self._generate_title(page)

            if suggested_title:
                confidence = self._calculate_confidence(page, suggested_title)

                fix = FixSuggestion(
                    fix_id=self._create_fix_id(page_url, 'title'),
                    issue_code=issue.code,
                    page_url=page_url,
                    page_id=0,
                    fix_type='title',
                    severity=issue.severity,
                    current_value=page.title or "(vuoto)",
                    suggested_value=suggested_title,
                    confidence=confidence,
                    automated=confidence >= 0.6,
                    sql_query=self._generate_sql(page, suggested_title),
                    api_endpoint=self._get_api_endpoint(page),
                    api_payload=self._generate_api_payload(page, suggested_title),
                    explanation=self._get_explanation(issue.code),
                    created_at=datetime.now()
                )
                fixes.append(fix)

        return fixes

    def _generate_title(self, page: PageData) -> Optional[str]:
        """Genera title ottimizzato"""
        current = page.title or ""
        domain = self._extract_domain(page.url)
        brand = domain.split('.')[0].title()

        if not current or len(current) < 10:
            # Genera da URL
            path = page.url.split('/')[-1].replace('-', ' ').replace('.html', '')
            suggested = path.title()

            # Aggiungi brand se < 50 caratteri
            if len(suggested) < 50:
                suggested += f" | {brand}"

            return suggested[:60]

        elif len(current) > 60:
            # Tronca preservando significato
            suggested = current[:57] + "..."
            return suggested

        elif len(current) < 10:
            # Espandi
            suggested = f"{current} - {brand}"
            return suggested[:60]

        return None

    def _calculate_confidence(self, page: PageData, suggested: str) -> float:
        """Calcola confidence del fix"""
        confidence = 0.4

        if page.title and len(page.title) > 5:
            confidence += 0.2

        if 30 <= len(suggested) <= 60:
            confidence += 0.3

        if page.is_product or page.is_category:
            confidence += 0.1

        return min(1.0, confidence)

    def _generate_sql(self, page: PageData, title: str) -> str:
        """Genera SQL fix"""
        page_id = self._extract_page_id(page.url)

        if page.is_product:
            return f"""
-- Fix title per prodotto
UPDATE ps_product_lang
SET meta_title = '{title.replace("'", "''")}'
WHERE id_product = {page_id} AND id_lang = 1;
"""
        elif page.is_category:
            return f"""
-- Fix title per categoria
UPDATE ps_category_lang
SET meta_title = '{title.replace("'", "''")}'
WHERE id_category = {page_id} AND id_lang = 1;
"""
        else:
            return "-- SQL fix non disponibile per questo tipo di pagina"

    def _get_api_endpoint(self, page: PageData) -> Optional[str]:
        page_id = self._extract_page_id(page.url)
        if page.is_product:
            return f"/api/products/{page_id}"
        elif page.is_category:
            return f"/api/categories/{page_id}"
        return None

    def _generate_api_payload(self, page: PageData, title: str) -> Optional[Dict[str, Any]]:
        if page.is_product:
            return {
                "product": {
                    "meta_title": {"language": [{"@id": "1", "#text": title}]}
                }
            }
        return None

    def _extract_page_id(self, url: str) -> int:
        patterns = [r'/(\d+)-', r'id_product=(\d+)', r'id_category=(\d+)']
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return int(match.group(1))
        return 0

    def _extract_domain(self, url: str) -> str:
        from urllib.parse import urlparse
        return urlparse(url).netloc

    def _get_explanation(self, issue_code: str) -> str:
        explanations = {
            'TITLE_MISSING': 'Il tag <title> è il fattore SEO più importante. Google lo usa come titolo principale in SERP.',
            'TITLE_TOO_SHORT': 'Un title troppo corto (<10 caratteri) non fornisce informazioni sufficienti a Google e agli utenti.',
            'TITLE_TOO_LONG': 'Un title oltre 60 caratteri viene troncato in SERP, perdendo parte del messaggio.'
        }
        return explanations.get(issue_code, '')


class AltTextFixer(FixGenerator):
    """Genera fix per ALT text mancanti"""

    def generate_fixes(self, issues: List[IssueData], pages: List[PageData]) -> List[FixSuggestion]:
        fixes = []

        # ALT text è più complesso, richiederebbe accesso alle immagini
        # Per ora generiamo fix basati su title e context

        issues_by_page = {}
        for issue in issues:
            if issue.code == 'IMAGES_MISSING_ALT':
                issues_by_page[issue.page_url] = issue

        pages_by_url = {page.url: page for page in pages}

        for page_url, issue in issues_by_page.items():
            page = pages_by_url.get(page_url)
            if not page:
                continue

            # Genera ALT generico basato su context
            suggested_alt = self._generate_alt_text(page)

            if suggested_alt:
                fix = FixSuggestion(
                    fix_id=self._create_fix_id(page_url, 'alt_text'),
                    issue_code=issue.code,
                    page_url=page_url,
                    page_id=0,
                    fix_type='alt_text',
                    severity=issue.severity,
                    current_value=f"{page.images_missing_alt + page.images_empty_alt} immagini senza ALT",
                    suggested_value=suggested_alt,
                    confidence=0.5,  # Bassa confidence per ALT generici
                    automated=False,  # Richiede revisione manuale
                    sql_query="-- ALT text richiede modifica template o database immagini specifico",
                    api_endpoint=None,
                    api_payload=None,
                    explanation=self._get_explanation('IMAGES_MISSING_ALT'),
                    created_at=datetime.now()
                )
                fixes.append(fix)

        return fixes

    def _generate_alt_text(self, page: PageData) -> str:
        """Genera ALT text suggerito"""
        if page.is_product and page.title:
            return f"{page.title} - Immagine prodotto"
        elif page.is_category and page.title:
            return f"{page.title} - Categoria"
        elif page.title:
            return f"{page.title}"
        else:
            return "Immagine descrittiva"

    def _get_explanation(self, issue_code: str) -> str:
        return 'Gli attributi ALT sono fondamentali per accessibilità e SEO immagini. Descrivi ogni immagine in modo specifico.'


class CanonicalFixer(FixGenerator):
    """Genera fix per canonical URL mancanti"""

    def generate_fixes(self, issues: List[IssueData], pages: List[PageData]) -> List[FixSuggestion]:
        fixes = []

        issues_by_page = {}
        for issue in issues:
            if issue.code in ['CANONICAL_MISSING', 'CANONICAL_MISSING_PRODUCT']:
                issues_by_page[issue.page_url] = issue

        pages_by_url = {page.url: page for page in pages}

        for page_url, issue in issues_by_page.items():
            page = pages_by_url.get(page_url)
            if not page:
                continue

            # Self-canonical o canonical pulito
            suggested_canonical = self._generate_canonical(page)

            if suggested_canonical:
                fix = FixSuggestion(
                    fix_id=self._create_fix_id(page_url, 'canonical'),
                    issue_code=issue.code,
                    page_url=page_url,
                    page_id=0,
                    fix_type='canonical',
                    severity=issue.severity,
                    current_value="(mancante)",
                    suggested_value=suggested_canonical,
                    confidence=0.9,  # Alta confidence per canonical
                    automated=True,
                    sql_query="-- Canonical richiede modifica template header",
                    api_endpoint=None,
                    api_payload=None,
                    explanation=self._get_explanation(issue.code),
                    created_at=datetime.now()
                )
                fixes.append(fix)

        return fixes

    def _generate_canonical(self, page: PageData) -> str:
        """Genera canonical URL"""
        # Rimuovi parametri query non essenziali
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(page.url)

        # Self-canonical pulito (senza parametri)
        clean_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            '',  # params
            '',  # query
            ''   # fragment
        ))

        return clean_url

    def _get_explanation(self, issue_code: str) -> str:
        explanations = {
            'CANONICAL_MISSING': 'Il canonical URL previene contenuti duplicati. Indica a Google quale versione della pagina indicizzare.',
            'CANONICAL_MISSING_PRODUCT': 'Le pagine prodotto devono avere canonical per evitare duplicati da filtri e varianti.'
        }
        return explanations.get(issue_code, '')


class SEOFixer:
    """Classe principale per gestione fix SEO"""

    def __init__(self, db_path: Path, config: Any = None, ai_provider: Optional[str] = None, ai_api_key: Optional[str] = None):
        self.db = CrawlDatabase(db_path)
        self.config = config
        self.ai_provider = ai_provider
        self.ai_api_key = ai_api_key

        # Genera generators con AI se disponibile
        self.generators = [
            MetaDescriptionFixer(self.db, ai_provider=ai_provider, ai_api_key=ai_api_key),
            TitleFixer(self.db),
            AltTextFixer(self.db),
            CanonicalFixer(self.db)
        ]

    async def generate_all_fixes(self) -> List[FixSuggestion]:
        """Genera tutti i fix possibili dagli issues rilevati"""
        # Carica issues e pages dal database
        issues = await self.db.export_issues()
        pages = await self.db.export_pages()

        # Converti a oggetti - rimuovi 'id' dai dict perché PageData/IssueData non hanno campo id
        import json
        issue_objects = []
        for issue in issues:
            issue_copy = {k: v for k, v in issue.items() if k != 'id'}
            # Converti meta da JSON string a dict se necessario
            if 'meta' in issue_copy and isinstance(issue_copy['meta'], str):
                try:
                    issue_copy['meta'] = json.loads(issue_copy['meta'])
                except:
                    issue_copy['meta'] = {}
            issue_objects.append(IssueData(**issue_copy))

        page_objects = []
        for page in pages:
            page_copy = {k: v for k, v in page.items() if k != 'id'}
            # Converti campi JSON da string a dict/list se necessario
            json_fields = ['headings_map', 'hreflang_map', 'jsonld_types']
            for field in json_fields:
                if field in page_copy and isinstance(page_copy[field], str):
                    try:
                        page_copy[field] = json.loads(page_copy[field])
                    except:
                        page_copy[field] = {} if field.endswith('_map') else []
            # Converti crawled_at da string a datetime se necessario
            if 'crawled_at' in page_copy and isinstance(page_copy['crawled_at'], str):
                from datetime import datetime
                try:
                    page_copy['crawled_at'] = datetime.fromisoformat(page_copy['crawled_at'])
                except:
                    page_copy['crawled_at'] = datetime.now()
            page_objects.append(PageData(**page_copy))

        all_fixes = []

        # Genera fix da ogni generator
        for generator in self.generators:
            fixes = generator.generate_fixes(issue_objects, page_objects)
            all_fixes.extend(fixes)

        return all_fixes

    def get_fixes_for_issue(self, issue_code: str) -> List[FixSuggestion]:
        """Ottieni fix per uno specifico issue"""
        # Implementazione sincrona per GUI
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        all_fixes = loop.run_until_complete(self.generate_all_fixes())

        return [fix for fix in all_fixes if fix.issue_code == issue_code]

    def export_fixes_csv(self, fixes: List[FixSuggestion], output_path: Path) -> None:
        """Esporta fix in formato CSV"""
        import csv

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Fix ID', 'Issue Code', 'Page URL', 'Fix Type', 'Severity',
                'Current Value', 'Suggested Value', 'Confidence', 'Automated',
                'Explanation'
            ])

            # Data
            for fix in fixes:
                writer.writerow([
                    fix.fix_id,
                    fix.issue_code,
                    fix.page_url,
                    fix.fix_type,
                    fix.severity,
                    fix.current_value[:100],  # Limita lunghezza
                    fix.suggested_value[:100],
                    f"{fix.confidence:.2f}",
                    'Yes' if fix.automated else 'No',
                    fix.explanation[:200]
                ])

    def export_fixes_sql(self, fixes: List[FixSuggestion], output_path: Path) -> None:
        """Esporta fix in formato SQL"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("-- SQL Fix Script generato da PyPrestaScan\n")
            f.write(f"-- Generato il: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Totale fix: {len(fixes)}\n\n")
            f.write("-- IMPORTANTE: Fai backup del database prima di eseguire!\n\n")

            for fix in fixes:
                if fix.sql_query and fix.automated:
                    f.write(f"\n-- Fix ID: {fix.fix_id}\n")
                    f.write(f"-- Pagina: {fix.page_url}\n")
                    f.write(f"-- Confidence: {fix.confidence:.2f}\n")
                    f.write(fix.sql_query)
                    f.write("\n")

    async def save_fixes_to_db(self, fixes: List[FixSuggestion]) -> None:
        """Salva fix nel database come FixData"""
        fix_data_list = []

        for fix in fixes:
            fix_data = FixData(
                fix_id=fix.fix_id,
                issue_code=fix.issue_code,
                page_url=fix.page_url,
                page_id=fix.page_id,
                fix_type=fix.fix_type,
                severity=fix.severity,
                current_value=fix.current_value,
                suggested_value=fix.suggested_value,
                confidence=fix.confidence,
                automated=fix.automated,
                sql_query=fix.sql_query,
                api_endpoint=fix.api_endpoint,
                api_payload=json.dumps(fix.api_payload) if fix.api_payload else None,
                explanation=fix.explanation,
                status='PENDING',
                created_at=fix.created_at,
                applied_at=None
            )
            fix_data_list.append(fix_data)

        await self.db.save_fixes_batch(fix_data_list)

    async def load_fixes_from_db(self, status: Optional[str] = None) -> List[FixSuggestion]:
        """Carica fix dal database come FixSuggestion"""
        fix_data_list = await self.db.get_all_fixes(status=status)

        suggestions = []
        for fix_data in fix_data_list:
            suggestion = FixSuggestion(
                fix_id=fix_data.fix_id,
                issue_code=fix_data.issue_code,
                page_url=fix_data.page_url,
                page_id=fix_data.page_id,
                fix_type=fix_data.fix_type,
                severity=fix_data.severity,
                current_value=fix_data.current_value,
                suggested_value=fix_data.suggested_value,
                confidence=fix_data.confidence,
                automated=fix_data.automated,
                sql_query=fix_data.sql_query,
                api_endpoint=fix_data.api_endpoint,
                api_payload=json.loads(fix_data.api_payload) if fix_data.api_payload else None,
                explanation=fix_data.explanation,
                created_at=fix_data.created_at
            )
            suggestions.append(suggestion)

        return suggestions