"""
Modulo storage SQLite per PyPrestaScan
"""
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import aiosqlite


@dataclass
class PageData:
    """Dati di una pagina crawlata"""
    url: str
    normalized_url: str
    status_code: int
    ttfb_ms: int
    content_type: str
    content_length: int
    title: str
    title_length: int
    meta_description: str
    meta_description_length: int
    meta_robots: str
    x_robots_tag: str
    canonical: str
    h1_count: int
    headings_map: Dict[str, int]  # h1: count, h2: count, etc.
    internal_links_count: int
    external_links_count: int
    nofollow_links_count: int
    hreflang_map: Dict[str, str]  # lang: url
    og_title: str
    og_description: str
    og_image: str
    jsonld_types: List[str]
    images_total: int
    images_missing_alt: int
    images_empty_alt: int
    images_generic_alt: int
    is_product: bool
    is_category: bool
    is_cms: bool
    is_faceted_filter: bool
    is_cart_or_checkout: bool
    is_account: bool
    content_hash: str
    score: float
    crawled_at: datetime
    depth: int


@dataclass
class ImageData:
    """Dati di un'immagine"""
    page_url: str
    image_src: str
    alt_text: Optional[str]
    alt_status: str  # MISSING, EMPTY, GENERIC, OK
    width: Optional[int]
    height: Optional[int]
    file_size: Optional[int]
    loading_attr: Optional[str]  # lazy, eager, etc.


@dataclass
class IssueData:
    """Dati di un issue SEO"""
    page_url: str
    severity: str  # CRITICAL, WARNING, INFO
    code: str
    message: str
    meta: Dict[str, Any]  # dati aggiuntivi specifici per tipo issue


@dataclass
class QueueEntry:
    """Entry nella coda di crawling"""
    url: str
    normalized_url: str
    discovered_from: str
    depth: int
    priority: int
    added_at: datetime


@dataclass
class CrawlState:
    """Stato del crawling"""
    project_name: str
    base_url: str
    started_at: datetime
    finished_at: Optional[datetime]
    status: str  # RUNNING, COMPLETED, PAUSED, FAILED
    pages_crawled: int
    pages_queued: int
    pages_failed: int
    config_json: str


@dataclass
class FixData:
    """Dati di un fix suggerito"""
    fix_id: str
    issue_code: str
    page_url: str
    page_id: int
    fix_type: str  # meta_description, title, alt_text, canonical, h1, hreflang, robots
    severity: str  # CRITICAL, WARNING, INFO
    current_value: str
    suggested_value: str
    confidence: float  # 0.0 - 1.0
    automated: bool  # True se può essere applicato automaticamente
    sql_query: Optional[str]
    api_endpoint: Optional[str]
    api_payload: Optional[str]  # JSON serializzato
    explanation: str
    status: str  # PENDING, APPLIED, REJECTED, FAILED
    created_at: datetime
    applied_at: Optional[datetime]


class CrawlDatabase:
    """Gestione database SQLite per crawling"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Inizializza database con schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Stato del crawling
                CREATE TABLE IF NOT EXISTS crawl_state (
                    id INTEGER PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    base_url TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    finished_at TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'RUNNING',
                    pages_crawled INTEGER DEFAULT 0,
                    pages_queued INTEGER DEFAULT 0,
                    pages_failed INTEGER DEFAULT 0,
                    config_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Coda URL da crawlare
                CREATE TABLE IF NOT EXISTS crawl_queue (
                    id INTEGER PRIMARY KEY,
                    url TEXT NOT NULL,
                    normalized_url TEXT NOT NULL UNIQUE,
                    discovered_from TEXT,
                    depth INTEGER DEFAULT 0,
                    priority INTEGER DEFAULT 0,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'PENDING'  -- PENDING, PROCESSING, COMPLETED, FAILED
                );
                
                -- URL già visitati (per deduplicazione rapida)
                CREATE TABLE IF NOT EXISTS visited_urls (
                    normalized_url TEXT PRIMARY KEY,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Dati pagine crawlate
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY,
                    url TEXT NOT NULL,
                    normalized_url TEXT NOT NULL UNIQUE,
                    status_code INTEGER,
                    ttfb_ms INTEGER,
                    content_type TEXT,
                    content_length INTEGER,
                    title TEXT,
                    title_length INTEGER,
                    meta_description TEXT,
                    meta_description_length INTEGER,
                    meta_robots TEXT,
                    x_robots_tag TEXT,
                    canonical TEXT,
                    h1_count INTEGER DEFAULT 0,
                    headings_map TEXT,  -- JSON
                    internal_links_count INTEGER DEFAULT 0,
                    external_links_count INTEGER DEFAULT 0,
                    nofollow_links_count INTEGER DEFAULT 0,
                    hreflang_map TEXT,  -- JSON
                    og_title TEXT,
                    og_description TEXT,
                    og_image TEXT,
                    jsonld_types TEXT,  -- JSON array
                    images_total INTEGER DEFAULT 0,
                    images_missing_alt INTEGER DEFAULT 0,
                    images_empty_alt INTEGER DEFAULT 0,
                    images_generic_alt INTEGER DEFAULT 0,
                    is_product BOOLEAN DEFAULT FALSE,
                    is_category BOOLEAN DEFAULT FALSE,
                    is_cms BOOLEAN DEFAULT FALSE,
                    is_faceted_filter BOOLEAN DEFAULT FALSE,
                    is_cart_or_checkout BOOLEAN DEFAULT FALSE,
                    is_account BOOLEAN DEFAULT FALSE,
                    content_hash TEXT,
                    score REAL DEFAULT 0.0,
                    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    depth INTEGER DEFAULT 0
                );
                
                -- Dati immagini
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY,
                    page_url TEXT NOT NULL,
                    image_src TEXT NOT NULL,
                    alt_text TEXT,
                    alt_status TEXT,  -- MISSING, EMPTY, GENERIC, OK
                    width INTEGER,
                    height INTEGER,
                    file_size INTEGER,
                    loading_attr TEXT,
                    FOREIGN KEY (page_url) REFERENCES pages (url)
                );
                
                -- Issues SEO
                CREATE TABLE IF NOT EXISTS issues (
                    id INTEGER PRIMARY KEY,
                    page_url TEXT NOT NULL,
                    severity TEXT NOT NULL,  -- CRITICAL, WARNING, INFO
                    code TEXT NOT NULL,
                    message TEXT NOT NULL,
                    meta TEXT,  -- JSON con dati aggiuntivi
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (page_url) REFERENCES pages (url)
                );
                
                -- Duplicati rilevati
                CREATE TABLE IF NOT EXISTS duplicates (
                    id INTEGER PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    url1 TEXT NOT NULL,
                    url2 TEXT NOT NULL,
                    similarity_score REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- Fix suggeriti
                CREATE TABLE IF NOT EXISTS fixes (
                    id INTEGER PRIMARY KEY,
                    fix_id TEXT NOT NULL UNIQUE,
                    issue_code TEXT NOT NULL,
                    page_url TEXT NOT NULL,
                    page_id INTEGER NOT NULL,
                    fix_type TEXT NOT NULL,  -- meta_description, title, alt_text, canonical, etc.
                    severity TEXT NOT NULL,  -- CRITICAL, WARNING, INFO
                    current_value TEXT,
                    suggested_value TEXT NOT NULL,
                    confidence REAL NOT NULL,  -- 0.0 - 1.0
                    automated BOOLEAN DEFAULT FALSE,
                    sql_query TEXT,
                    api_endpoint TEXT,
                    api_payload TEXT,  -- JSON serializzato
                    explanation TEXT NOT NULL,
                    status TEXT DEFAULT 'PENDING',  -- PENDING, APPLIED, REJECTED, FAILED
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    applied_at TIMESTAMP,
                    FOREIGN KEY (page_url) REFERENCES pages (url)
                );

                -- Indici per performance
                CREATE INDEX IF NOT EXISTS idx_queue_status ON crawl_queue (status);
                CREATE INDEX IF NOT EXISTS idx_queue_priority ON crawl_queue (priority DESC);
                CREATE INDEX IF NOT EXISTS idx_pages_status ON pages (status_code);
                CREATE INDEX IF NOT EXISTS idx_pages_type ON pages (is_product, is_category, is_cms);
                CREATE INDEX IF NOT EXISTS idx_images_alt_status ON images (alt_status);
                CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues (severity);
                CREATE INDEX IF NOT EXISTS idx_duplicates_hash ON duplicates (content_hash);
                CREATE INDEX IF NOT EXISTS idx_fixes_status ON fixes (status);
                CREATE INDEX IF NOT EXISTS idx_fixes_type ON fixes (fix_type);
                CREATE INDEX IF NOT EXISTS idx_fixes_page ON fixes (page_url);
            """)
    
    async def save_crawl_state(self, state: CrawlState) -> None:
        """Salva stato del crawling"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO crawl_state 
                (project_name, base_url, started_at, finished_at, status, 
                 pages_crawled, pages_queued, pages_failed, config_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.project_name, state.base_url, state.started_at,
                state.finished_at, state.status, state.pages_crawled,
                state.pages_queued, state.pages_failed, state.config_json
            ))
            await db.commit()
    
    async def load_crawl_state(self) -> Optional[CrawlState]:
        """Carica ultimo stato del crawling"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT project_name, base_url, started_at, finished_at, status,
                       pages_crawled, pages_queued, pages_failed, config_json
                FROM crawl_state ORDER BY id DESC LIMIT 1
            """) as cursor:
                row = await cursor.fetchone()
                if row:
                    return CrawlState(*row)
        return None
    
    async def add_to_queue(self, entries: List[QueueEntry]) -> int:
        """Aggiunge URL alla coda (batch)"""
        if not entries:
            return 0
        
        async with aiosqlite.connect(self.db_path) as db:
            # Filtro URL già visitati
            placeholders = ','.join('?' * len(entries))
            normalized_urls = [entry.normalized_url for entry in entries]
            
            async with db.execute(f"""
                SELECT normalized_url FROM visited_urls 
                WHERE normalized_url IN ({placeholders})
            """, normalized_urls) as cursor:
                visited = {row[0] for row in await cursor.fetchall()}
            
            # Inserisci solo URL nuovi
            new_entries = [entry for entry in entries 
                          if entry.normalized_url not in visited]
            
            if new_entries:
                await db.executemany("""
                    INSERT OR IGNORE INTO crawl_queue 
                    (url, normalized_url, discovered_from, depth, priority, added_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [
                    (entry.url, entry.normalized_url, entry.discovered_from,
                     entry.depth, entry.priority, entry.added_at)
                    for entry in new_entries
                ])
                
                # Marca come visitati
                await db.executemany("""
                    INSERT OR IGNORE INTO visited_urls (normalized_url)
                    VALUES (?)
                """, [(entry.normalized_url,) for entry in new_entries])
                
                await db.commit()
            
            return len(new_entries)
    
    async def get_next_from_queue(self, limit: int = 1) -> List[QueueEntry]:
        """Recupera prossimi URL dalla coda"""
        async with aiosqlite.connect(self.db_path) as db:
            # Marca come PROCESSING
            await db.execute("""
                UPDATE crawl_queue SET status = 'PROCESSING'
                WHERE id IN (
                    SELECT id FROM crawl_queue 
                    WHERE status = 'PENDING'
                    ORDER BY priority DESC, added_at ASC
                    LIMIT ?
                )
            """, (limit,))
            
            # Recupera entries
            async with db.execute("""
                SELECT url, normalized_url, discovered_from, depth, priority, added_at
                FROM crawl_queue 
                WHERE status = 'PROCESSING'
                ORDER BY priority DESC, added_at ASC
                LIMIT ?
            """, (limit,)) as cursor:
                rows = await cursor.fetchall()
                
            await db.commit()
            
            return [QueueEntry(*row) for row in rows]
    
    async def mark_queue_completed(self, normalized_urls: List[str]) -> None:
        """Marca URL come completati nella coda"""
        if not normalized_urls:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            placeholders = ','.join('?' * len(normalized_urls))
            await db.execute(f"""
                UPDATE crawl_queue SET status = 'COMPLETED'
                WHERE normalized_url IN ({placeholders})
            """, normalized_urls)
            await db.commit()
    
    async def mark_queue_failed(self, normalized_urls: List[str]) -> None:
        """Marca URL come falliti nella coda"""
        if not normalized_urls:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            placeholders = ','.join('?' * len(normalized_urls))
            await db.execute(f"""
                UPDATE crawl_queue SET status = 'FAILED'
                WHERE normalized_url IN ({placeholders})
            """, normalized_urls)
            await db.commit()
    
    async def save_page(self, page: PageData) -> None:
        """Salva dati di una pagina"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                values_tuple = (
                    page.url, page.normalized_url, page.status_code, page.ttfb_ms,
                    page.content_type, page.content_length, page.title, page.title_length,
                    page.meta_description, page.meta_description_length, page.meta_robots,
                    page.x_robots_tag, page.canonical, page.h1_count,
                    json.dumps(page.headings_map), page.internal_links_count,
                    page.external_links_count, page.nofollow_links_count,
                    json.dumps(page.hreflang_map), page.og_title, page.og_description,
                    page.og_image, json.dumps(page.jsonld_types), page.images_total,
                    page.images_missing_alt, page.images_empty_alt, page.images_generic_alt,
                    page.is_product, page.is_category, page.is_cms, page.is_faceted_filter,
                    page.is_cart_or_checkout, page.is_account, page.content_hash,
                    page.score, page.crawled_at, page.depth
                )
                
                await db.execute("""
                    INSERT OR REPLACE INTO pages (
                        url, normalized_url, status_code, ttfb_ms, content_type, content_length,
                        title, title_length, meta_description, meta_description_length,
                        meta_robots, x_robots_tag, canonical, h1_count, headings_map,
                        internal_links_count, external_links_count, nofollow_links_count,
                        hreflang_map, og_title, og_description, og_image, jsonld_types,
                        images_total, images_missing_alt, images_empty_alt, images_generic_alt,
                        is_product, is_category, is_cms, is_faceted_filter, 
                        is_cart_or_checkout, is_account, content_hash, score, crawled_at, depth
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values_tuple)
            except Exception as e:
                # Log errore database per debugging
                import traceback
                error_msg = f"Errore salvando pagina {page.url}: {e}"
                if hasattr(self, 'logger'):
                    self.logger.error(error_msg)
                    self.logger.debug(traceback.format_exc())
                raise
            await db.commit()
    
    async def save_images(self, images: List[ImageData]) -> None:
        """Salva dati immagini (batch)"""
        if not images:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.executemany("""
                INSERT INTO images (
                    page_url, image_src, alt_text, alt_status, width, height,
                    file_size, loading_attr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (img.page_url, img.image_src, img.alt_text, img.alt_status,
                 img.width, img.height, img.file_size, img.loading_attr)
                for img in images
            ])
            await db.commit()
    
    async def save_issues(self, issues: List[IssueData]) -> None:
        """Salva issues SEO (batch)"""
        if not issues:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.executemany("""
                INSERT INTO issues (page_url, severity, code, message, meta)
                VALUES (?, ?, ?, ?, ?)
            """, [
                (issue.page_url, issue.severity, issue.code, 
                 issue.message, json.dumps(issue.meta))
                for issue in issues
            ])
            await db.commit()
    
    async def save_duplicate(self, content_hash: str, url1: str, url2: str, 
                           similarity: float = 1.0) -> None:
        """Salva duplicato rilevato"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO duplicates (content_hash, url1, url2, similarity_score)
                VALUES (?, ?, ?, ?)
            """, (content_hash, url1, url2, similarity))
            await db.commit()
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Statistiche coda"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT status, COUNT(*) FROM crawl_queue GROUP BY status
            """) as cursor:
                rows = await cursor.fetchall()
                
            stats = dict(rows)
            return {
                'pending': stats.get('PENDING', 0),
                'processing': stats.get('PROCESSING', 0),
                'completed': stats.get('COMPLETED', 0),
                'failed': stats.get('FAILED', 0),
                'total': sum(stats.values())
            }
    
    async def get_crawl_stats(self) -> Dict[str, Any]:
        """Statistiche crawling complete"""
        async with aiosqlite.connect(self.db_path) as db:
            # Statistiche pagine per status
            async with db.execute("""
                SELECT 
                    CASE 
                        WHEN status_code BETWEEN 200 AND 299 THEN '2xx'
                        WHEN status_code BETWEEN 300 AND 399 THEN '3xx'
                        WHEN status_code BETWEEN 400 AND 499 THEN '4xx'
                        WHEN status_code BETWEEN 500 AND 599 THEN '5xx'
                        ELSE 'other'
                    END as status_range,
                    COUNT(*) as count
                FROM pages GROUP BY status_range
            """) as cursor:
                status_stats = dict(await cursor.fetchall())
            
            # Statistiche issues per severity
            async with db.execute("""
                SELECT severity, COUNT(*) FROM issues GROUP BY severity
            """) as cursor:
                issue_stats = dict(await cursor.fetchall())
            
            # Statistiche immagini per ALT status
            async with db.execute("""
                SELECT alt_status, COUNT(*) FROM images GROUP BY alt_status
            """) as cursor:
                alt_stats = dict(await cursor.fetchall())
            
            # Statistiche generali
            async with db.execute("""
                SELECT 
                    COUNT(*) as total_pages,
                    COUNT(CASE WHEN is_product THEN 1 END) as product_pages,
                    COUNT(CASE WHEN is_category THEN 1 END) as category_pages,
                    COUNT(CASE WHEN is_cms THEN 1 END) as cms_pages,
                    AVG(score) as avg_score
                FROM pages
            """) as cursor:
                general_stats = dict(zip([
                    'total_pages', 'product_pages', 'category_pages', 
                    'cms_pages', 'avg_score'
                ], await cursor.fetchone()))
            
            return {
                'status': status_stats,
                'issues': issue_stats,
                'alt_text': alt_stats,
                'general': general_stats,
                'queue': await self.get_queue_stats()
            }
    
    # Metodi per export
    async def export_pages(self) -> List[Dict[str, Any]]:
        """Export dati pagine per CSV/JSON"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM pages ORDER BY crawled_at
            """) as cursor:
                columns = [description[0] for description in cursor.description]
                rows = await cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
    
    async def export_images_issues(self, include_generic: bool = False) -> List[Dict[str, Any]]:
        """Export immagini con problemi ALT"""
        alt_filter = "('MISSING', 'EMPTY')"
        if include_generic:
            alt_filter = "('MISSING', 'EMPTY', 'GENERIC')"
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(f"""
                SELECT page_url, image_src, alt_text, alt_status
                FROM images 
                WHERE alt_status IN {alt_filter}
                ORDER BY page_url, image_src
            """) as cursor:
                columns = [description[0] for description in cursor.description]
                rows = await cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
    
    async def export_issues(self) -> List[Dict[str, Any]]:
        """Export issues SEO"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT page_url, severity, code, message, meta
                FROM issues 
                ORDER BY severity DESC, page_url
            """) as cursor:
                columns = [description[0] for description in cursor.description]
                rows = await cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
    
    async def export_duplicates(self) -> List[Dict[str, Any]]:
        """Export duplicati rilevati"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT content_hash, url1, url2, similarity_score
                FROM duplicates
                ORDER BY similarity_score DESC
            """) as cursor:
                columns = [description[0] for description in cursor.description]
                rows = await cursor.fetchall()

                return [dict(zip(columns, row)) for row in rows]

    # Metodi per Fix Data
    async def save_fix(self, fix: FixData) -> None:
        """Salva un fix suggerito"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO fixes (
                    fix_id, issue_code, page_url, page_id, fix_type, severity,
                    current_value, suggested_value, confidence, automated,
                    sql_query, api_endpoint, api_payload, explanation, status,
                    created_at, applied_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fix.fix_id, fix.issue_code, fix.page_url, fix.page_id,
                fix.fix_type, fix.severity, fix.current_value, fix.suggested_value,
                fix.confidence, fix.automated, fix.sql_query, fix.api_endpoint,
                fix.api_payload, fix.explanation, fix.status,
                fix.created_at, fix.applied_at
            ))
            await db.commit()

    async def save_fixes_batch(self, fixes: List[FixData]) -> None:
        """Salva multipli fix in batch"""
        if not fixes:
            return

        async with aiosqlite.connect(self.db_path) as db:
            await db.executemany("""
                INSERT OR REPLACE INTO fixes (
                    fix_id, issue_code, page_url, page_id, fix_type, severity,
                    current_value, suggested_value, confidence, automated,
                    sql_query, api_endpoint, api_payload, explanation, status,
                    created_at, applied_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (fix.fix_id, fix.issue_code, fix.page_url, fix.page_id,
                 fix.fix_type, fix.severity, fix.current_value, fix.suggested_value,
                 fix.confidence, fix.automated, fix.sql_query, fix.api_endpoint,
                 fix.api_payload, fix.explanation, fix.status,
                 fix.created_at, fix.applied_at)
                for fix in fixes
            ])
            await db.commit()

    async def get_all_fixes(self, status: Optional[str] = None) -> List[FixData]:
        """Recupera tutti i fix, opzionalmente filtrati per status"""
        async with aiosqlite.connect(self.db_path) as db:
            if status:
                query = "SELECT * FROM fixes WHERE status = ? ORDER BY severity DESC, confidence DESC"
                params = (status,)
            else:
                query = "SELECT * FROM fixes ORDER BY severity DESC, confidence DESC"
                params = ()

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()

                fixes = []
                for row in rows:
                    fix = FixData(
                        fix_id=row[1],
                        issue_code=row[2],
                        page_url=row[3],
                        page_id=row[4],
                        fix_type=row[5],
                        severity=row[6],
                        current_value=row[7],
                        suggested_value=row[8],
                        confidence=row[9],
                        automated=bool(row[10]),
                        sql_query=row[11],
                        api_endpoint=row[12],
                        api_payload=row[13],
                        explanation=row[14],
                        status=row[15],
                        created_at=datetime.fromisoformat(row[16]) if row[16] else datetime.now(),
                        applied_at=datetime.fromisoformat(row[17]) if row[17] else None
                    )
                    fixes.append(fix)

                return fixes

    async def get_fixes_by_page(self, page_url: str) -> List[FixData]:
        """Recupera fix per una specifica pagina"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM fixes WHERE page_url = ? ORDER BY severity DESC, confidence DESC
            """, (page_url,)) as cursor:
                rows = await cursor.fetchall()

                fixes = []
                for row in rows:
                    fix = FixData(
                        fix_id=row[1],
                        issue_code=row[2],
                        page_url=row[3],
                        page_id=row[4],
                        fix_type=row[5],
                        severity=row[6],
                        current_value=row[7],
                        suggested_value=row[8],
                        confidence=row[9],
                        automated=bool(row[10]),
                        sql_query=row[11],
                        api_endpoint=row[12],
                        api_payload=row[13],
                        explanation=row[14],
                        status=row[15],
                        created_at=datetime.fromisoformat(row[16]) if row[16] else datetime.now(),
                        applied_at=datetime.fromisoformat(row[17]) if row[17] else None
                    )
                    fixes.append(fix)

                return fixes

    async def get_fix_by_id(self, fix_id: str) -> Optional[FixData]:
        """Recupera un fix specifico per ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT * FROM fixes WHERE fix_id = ?
            """, (fix_id,)) as cursor:
                row = await cursor.fetchone()

                if row:
                    return FixData(
                        fix_id=row[1],
                        issue_code=row[2],
                        page_url=row[3],
                        page_id=row[4],
                        fix_type=row[5],
                        severity=row[6],
                        current_value=row[7],
                        suggested_value=row[8],
                        confidence=row[9],
                        automated=bool(row[10]),
                        sql_query=row[11],
                        api_endpoint=row[12],
                        api_payload=row[13],
                        explanation=row[14],
                        status=row[15],
                        created_at=datetime.fromisoformat(row[16]) if row[16] else datetime.now(),
                        applied_at=datetime.fromisoformat(row[17]) if row[17] else None
                    )
                return None

    async def update_fix_status(self, fix_id: str, status: str,
                               applied_at: Optional[datetime] = None) -> None:
        """Aggiorna lo status di un fix"""
        async with aiosqlite.connect(self.db_path) as db:
            if applied_at:
                await db.execute("""
                    UPDATE fixes SET status = ?, applied_at = ? WHERE fix_id = ?
                """, (status, applied_at, fix_id))
            else:
                await db.execute("""
                    UPDATE fixes SET status = ? WHERE fix_id = ?
                """, (status, fix_id))
            await db.commit()

    async def delete_fix(self, fix_id: str) -> None:
        """Elimina un fix"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM fixes WHERE fix_id = ?", (fix_id,))
            await db.commit()

    async def get_fix_stats(self) -> Dict[str, Any]:
        """Statistiche sui fix"""
        async with aiosqlite.connect(self.db_path) as db:
            # Conteggio per status
            async with db.execute("""
                SELECT status, COUNT(*) FROM fixes GROUP BY status
            """) as cursor:
                status_stats = dict(await cursor.fetchall())

            # Conteggio per tipo
            async with db.execute("""
                SELECT fix_type, COUNT(*) FROM fixes GROUP BY fix_type
            """) as cursor:
                type_stats = dict(await cursor.fetchall())

            # Conteggio per severity
            async with db.execute("""
                SELECT severity, COUNT(*) FROM fixes GROUP BY severity
            """) as cursor:
                severity_stats = dict(await cursor.fetchall())

            # Media confidence
            async with db.execute("""
                SELECT AVG(confidence) FROM fixes WHERE status = 'PENDING'
            """) as cursor:
                avg_confidence = await cursor.fetchone()

            # Fix automatizzabili
            async with db.execute("""
                SELECT COUNT(*) FROM fixes WHERE automated = 1 AND status = 'PENDING'
            """) as cursor:
                automated_count = await cursor.fetchone()

            return {
                'by_status': status_stats,
                'by_type': type_stats,
                'by_severity': severity_stats,
                'avg_confidence': avg_confidence[0] if avg_confidence[0] else 0.0,
                'automated_pending': automated_count[0] if automated_count else 0
            }

    async def export_fixes(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Export fix per CSV/JSON"""
        async with aiosqlite.connect(self.db_path) as db:
            if status:
                query = """
                    SELECT fix_id, issue_code, page_url, page_id, fix_type, severity,
                           current_value, suggested_value, confidence, automated,
                           explanation, status, created_at, applied_at
                    FROM fixes WHERE status = ?
                    ORDER BY severity DESC, confidence DESC
                """
                params = (status,)
            else:
                query = """
                    SELECT fix_id, issue_code, page_url, page_id, fix_type, severity,
                           current_value, suggested_value, confidence, automated,
                           explanation, status, created_at, applied_at
                    FROM fixes
                    ORDER BY severity DESC, confidence DESC
                """
                params = ()

            async with db.execute(query, params) as cursor:
                columns = [description[0] for description in cursor.description]
                rows = await cursor.fetchall()

                return [dict(zip(columns, row)) for row in rows]