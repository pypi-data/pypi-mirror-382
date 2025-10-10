"""
Crawler principale PyPrestaScan - Orchestrazione crawling asincrono
"""
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import json
import signal
import sys

from .utils import URLNormalizer, ProjectManager, RichLogger, create_progress
from .storage import CrawlDatabase, CrawlState, QueueEntry, PageData, ImageData, IssueData
from .fetcher import HttpFetcher
from .parser import SEOParser
from .analyzer import SEORuleEngine, DuplicateDetector
from .exporters import ReportExporter
from ..cli import CrawlConfig, CliContext


class CrawlStats:
    """Statistiche runtime del crawling"""
    
    def __init__(self):
        self.pages_crawled = 0
        self.pages_failed = 0
        self.pages_2xx = 0
        self.pages_3xx = 0
        self.pages_4xx = 0
        self.pages_5xx = 0
        self.total_issues = 0
        self.images_analyzed = 0
        self.images_no_alt = 0
        self.duplicates_found = 0
        self.start_time = datetime.now()
        self.bytes_downloaded = 0
    
    def update_from_page(self, page: PageData) -> None:
        """Aggiorna statistiche da una pagina"""
        self.pages_crawled += 1
        
        if 200 <= page.status_code < 300:
            self.pages_2xx += 1
        elif 300 <= page.status_code < 400:
            self.pages_3xx += 1
        elif 400 <= page.status_code < 500:
            self.pages_4xx += 1
        elif page.status_code >= 500:
            self.pages_5xx += 1
        
        self.images_analyzed += page.images_total
        self.images_no_alt += page.images_missing_alt + page.images_empty_alt
        self.bytes_downloaded += page.content_length
    
    def update_issues(self, issues: List[IssueData]) -> None:
        """Aggiorna conteggio issues"""
        self.total_issues += len(issues)
    
    def to_dict(self) -> Dict[str, Any]:
        """Esporta statistiche come dict"""
        runtime = datetime.now() - self.start_time
        
        return {
            'pages_crawled': self.pages_crawled,
            'pages_failed': self.pages_failed,
            'pages_2xx': self.pages_2xx,
            'pages_3xx': self.pages_3xx,
            'pages_4xx': self.pages_4xx,
            'pages_5xx': self.pages_5xx,
            'total_issues': self.total_issues,
            'images_analyzed': self.images_analyzed,
            'images_no_alt': self.images_no_alt,
            'duplicates_found': self.duplicates_found,
            'runtime_seconds': runtime.total_seconds(),
            'bytes_downloaded': self.bytes_downloaded,
            'avg_speed': self.pages_crawled / max(runtime.total_seconds(), 1)
        }


class PyPrestaScanner:
    """Scanner principale PyPrestaScan"""
    
    def __init__(self, config: CrawlConfig, cli_context: CliContext, setup_signals: bool = True):
        self.config = config
        self.cli_context = cli_context
        self.setup_signals = setup_signals
        self.logger = RichLogger(
            debug=cli_context.debug,
            quiet=cli_context.quiet,
            no_color=cli_context.no_color
        )
        
        # Componenti
        self.project_manager = ProjectManager(config.project)
        self.url_normalizer = URLNormalizer(
            urlparse(str(config.url)).netloc, 
            config.include_subdomains
        )
        self.db = CrawlDatabase(self.project_manager.get_db_path())
        self.fetcher: Optional[HttpFetcher] = None
        self.parser = SEOParser(self.url_normalizer, config.prestashop_mode)
        self.analyzer = SEORuleEngine(config.prestashop_mode)
        self.duplicate_detector = DuplicateDetector()
        
        # Stato
        self.stats = CrawlStats()
        self.is_running = False
        self.should_stop = False
        self.sitemap_url_count = 0  # Conteggio URL da sitemap
        
        # Progress tracking
        self.progress = create_progress()
        self.crawl_task_id = None
        
        # Setup signal handlers per interruzione graziosa (solo se in main thread)
        if self.setup_signals:
            try:
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
            except ValueError:
                # Signal handlers possono essere impostati solo nel main thread
                self.logger.debug("🔧 Signal handlers saltati (non main thread)")
    
    def _signal_handler(self, signum, frame):
        """Gestisce interruzione per shutdown graceful"""
        if not self.should_stop:
            self.logger.warning("🛑 Interruzione richiesta, completamento in corso...")
            self.should_stop = True
        else:
            self.logger.error("🛑 Interruzione forzata!")
            sys.exit(1)
    
    async def run(self) -> int:
        """Esegue scansione completa"""
        try:
            self.is_running = True
            
            # Inizializza componenti
            await self._initialize()
            
            # Carica o inizia nuovo crawl
            if self.config.resume:
                await self._resume_crawl()
            else:
                await self._start_new_crawl()
            
            # Esegui crawling
            with self.progress:
                await self._run_crawling()
            
            # Genera report
            await self._generate_reports()
            
            # Statistiche finali
            self._print_final_stats()
            
            return 0
            
        except KeyboardInterrupt:
            self.logger.warning("🛑 Crawling interrotto dall'utente")
            return 1
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.logger.error(f"Errore durante crawling: {e}")
            self.logger.error(f"Traceback:\n{error_details}")
            if self.cli_context.debug:
                raise
            return 1
        finally:
            await self._cleanup()
    
    async def _initialize(self) -> None:
        """Inizializza componenti asincroni"""
        # Auth tuple se configurata
        auth = None
        if self.config.auth_user and self.config.auth_pass:
            auth = (self.config.auth_user, self.config.auth_pass)
        
        # Inizializza fetcher
        self.fetcher = HttpFetcher(
            concurrency=self.config.concurrency,
            delay_ms=self.config.delay,
            timeout=self.config.timeout,
            user_agent=self.config.user_agent,
            auth=auth,
            logger=self.logger
        )
        
        await self.fetcher.start()
        
        self.logger.info(f"🚀 Scanner inizializzato per {self.config.url}")
    
    async def _start_new_crawl(self) -> None:
        """Inizia nuovo crawling"""
        base_url = str(self.config.url)
        
        # Salva stato iniziale
        state = CrawlState(
            project_name=self.config.project,
            base_url=base_url,
            started_at=datetime.now(),
            finished_at=None,
            status='RUNNING',
            pages_crawled=0,
            pages_queued=0,
            pages_failed=0,
            config_json=json.dumps(self.config.model_dump(), default=str)
        )
        await self.db.save_crawl_state(state)
        
        # Aggiungi URL iniziale alla coda
        normalized_base = self.url_normalizer.normalize(base_url)
        initial_entry = QueueEntry(
            url=base_url,
            normalized_url=normalized_base,
            discovered_from='seed',
            depth=0,
            priority=100,  # Priorità massima per seed
            added_at=datetime.now()
        )
        
        await self.db.add_to_queue([initial_entry])
        
        # Scopri e aggiungi sitemap se configurato
        if self.config.sitemap in ('auto', 'true'):
            await self._discover_sitemaps(base_url)
        
        self.logger.info(f"🌱 Crawling iniziato da {base_url}")
    
    async def _resume_crawl(self) -> None:
        """Riprende crawling esistente"""
        state = await self.db.load_crawl_state()
        
        if not state:
            self.logger.error("❌ Nessun crawling esistente da riprendere")
            raise ValueError("Nessun progetto esistente da riprendere")
        
        if state.status == 'COMPLETED':
            self.logger.warning("⚠️ Il crawling era già completato")
        
        # Aggiorna stato
        state.status = 'RUNNING'
        await self.db.save_crawl_state(state)
        
        queue_stats = await self.db.get_queue_stats()
        self.logger.info(f"🔄 Ripreso crawling: {queue_stats['pending']} URL in coda")
    
    async def _discover_sitemaps(self, base_url: str) -> None:
        """Scopre e processa sitemap"""
        try:
            sitemap_urls = await self.fetcher.discover_sitemaps(base_url)

            for sitemap_url in sitemap_urls:
                urls = await self.fetcher.fetch_sitemap(sitemap_url)

                if urls:
                    # Converti a QueueEntry
                    entries = []
                    for url in urls:
                        normalized = self.url_normalizer.normalize(url)
                        if normalized and self.url_normalizer.is_same_domain(normalized):
                            entries.append(QueueEntry(
                                url=url,
                                normalized_url=normalized,
                                discovered_from=f'sitemap:{sitemap_url}',
                                depth=1,
                                priority=50,
                                added_at=datetime.now()
                            ))

                    # Aggiungi alla coda (batch)
                    if entries:
                        added = await self.db.add_to_queue(entries)
                        self.sitemap_url_count += added  # Conta URL da sitemap
                        self.logger.info(f"🗺️ Aggiunti {added} URL da sitemap {sitemap_url}")

            # Log totale
            if self.sitemap_url_count > 0:
                self.logger.success(f"✅ Totale URL da sitemap: {self.sitemap_url_count}")

        except Exception as e:
            self.logger.warning(f"⚠️ Errore discovery sitemap: {e}")
    
    async def _run_crawling(self) -> None:
        """Esegue loop principale di crawling"""
        
        # Progress bar
        self.crawl_task_id = self.progress.add_task(
            "🔍 Crawling in corso...", 
            total=self.config.max_urls
        )
        
        batch_size = min(self.config.concurrency, 50)  # Max 50 URL per batch
        
        while (not self.should_stop and 
               self.stats.pages_crawled < self.config.max_urls):
            
            # Recupera batch dalla coda
            queue_entries = await self.db.get_next_from_queue(batch_size)
            
            if not queue_entries:
                self.logger.info("✅ Nessun URL in coda, crawling completato")
                break
            
            # Processa batch in parallelo
            await self._process_batch(queue_entries)
            
            # Aggiorna progress
            self.progress.update(
                self.crawl_task_id, 
                completed=self.stats.pages_crawled,
                description=f"🔍 Crawlate: {self.stats.pages_crawled} | "
                           f"Coda: {len(queue_entries)} | "
                           f"Errori: {self.stats.pages_failed}"
            )
            
            # Breve pausa per evitare overload
            await asyncio.sleep(0.1)
        
        # Finalizza crawling
        await self._finalize_crawling()
    
    async def _process_batch(self, queue_entries: List[QueueEntry]) -> None:
        """Processa batch di URL in parallelo"""
        
        # Fetch parallelo
        urls = [entry.url for entry in queue_entries]
        responses = await self.fetcher.fetch_batch(urls, check_robots=True)
        
        # Processa ogni risposta
        tasks = []
        for i, (entry, response) in enumerate(zip(queue_entries, responses)):
            task = self._process_single_page(entry, response)
            tasks.append(task)
        
        # Attendi completamento
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Gestisci errori
        completed_urls = []
        failed_urls = []
        
        for i, result in enumerate(results):
            normalized_url = queue_entries[i].normalized_url
            
            if isinstance(result, Exception):
                self.logger.error(f"❌ Errore processing {normalized_url}: {result}")
                failed_urls.append(normalized_url)
                self.stats.pages_failed += 1
            else:
                completed_urls.append(normalized_url)
        
        # Aggiorna stato coda
        if completed_urls:
            await self.db.mark_queue_completed(completed_urls)
        if failed_urls:
            await self.db.mark_queue_failed(failed_urls)
    
    async def _process_single_page(self, queue_entry: QueueEntry, response) -> None:
        """Processa singola pagina"""
        
        # Parse risposta
        parsed_data = self.parser.parse(response, queue_entry.depth)
        page = parsed_data.page
        
        # Imposta timestamp
        page.crawled_at = datetime.now()
        
        # Analisi SEO e scoring
        issues, score = self.analyzer.analyze_page(parsed_data)
        page.score = score
        
        # Rileva duplicati
        duplicates = self.duplicate_detector.add_page(page)
        if duplicates:
            for dup_url in duplicates:
                await self.db.save_duplicate(
                    page.content_hash, 
                    page.normalized_url, 
                    dup_url
                )
                self.stats.duplicates_found += 1
        
        # Salva dati nel database
        await self.db.save_page(page)
        
        if parsed_data.images:
            await self.db.save_images(parsed_data.images)
            self.logger.images_analyzed(len(parsed_data.images), 
                                      page.images_missing_alt + page.images_empty_alt)
        
        if issues:
            await self.db.save_issues(issues)
        
        # Aggiorna statistiche
        self.stats.update_from_page(page)
        self.stats.update_issues(issues)
        
        # Log pagina
        self.logger.page_crawled(page.url, page.status_code, page.ttfb_ms)
        
        # Aggiungi nuovi link alla coda (se sotto depth limit)
        if (parsed_data.links and 
            (not self.config.depth or queue_entry.depth < self.config.depth)):
            
            # Filtra per pattern include/exclude
            filtered_links = self._filter_links(parsed_data.links)
            
            if filtered_links:
                new_entries = []
                for link in filtered_links:
                    new_entries.append(QueueEntry(
                        url=link,
                        normalized_url=self.url_normalizer.normalize(link),
                        discovered_from=page.url,
                        depth=queue_entry.depth + 1,
                        priority=max(0, 50 - queue_entry.depth * 10),
                        added_at=datetime.now()
                    ))
                
                # Aggiungi alla coda (batch)
                added = await self.db.add_to_queue(new_entries)
                if added > 0:
                    self.logger.debug(f"🌐 {added} nuovi URL in coda da {page.url}")
    
    def _filter_links(self, links: List[str]) -> List[str]:
        """Filtra link per pattern include/exclude"""
        if not links:
            return []
        
        filtered = []
        
        for link in links:
            # Applica pattern exclude
            if self.config.exclude_patterns:
                if any(re.search(pattern, link) for pattern in self.config.exclude_patterns):
                    continue
            
            # Applica pattern include (se configurati)
            if self.config.include_patterns:
                if not any(re.search(pattern, link) for pattern in self.config.include_patterns):
                    continue
            
            filtered.append(link)
        
        return filtered
    
    async def _finalize_crawling(self) -> None:
        """Finalizza crawling e aggiorna stato"""
        
        # Aggiorna stato finale
        state = CrawlState(
            project_name=self.config.project,
            base_url=str(self.config.url),
            started_at=self.stats.start_time,
            finished_at=datetime.now(),
            status='COMPLETED',
            pages_crawled=self.stats.pages_crawled,
            pages_queued=0,  # Sarà aggiornato da DB query
            pages_failed=self.stats.pages_failed,
            config_json=json.dumps(self.config.model_dump(), default=str)
        )
        
        await self.db.save_crawl_state(state)
        
        self.logger.success("✅ Crawling completato!")
    
    async def _generate_reports(self) -> None:
        """Genera report finali"""
        export_dir = self.project_manager.get_export_dir(self.config.export_dir)
        
        exporter = ReportExporter(
            db=self.db,
            export_dir=export_dir,
            base_url=str(self.config.url),
            include_generic_alt=self.config.include_generic,
            logger=self.logger
        )
        
        await exporter.export_all()
        
        self.logger.success(f"📊 Report generati in {export_dir}")
    
    def _print_final_stats(self) -> None:
        """Stampa statistiche finali"""
        stats_dict = self.stats.to_dict()
        
        # Arricchisci con ulteriori metriche
        runtime_minutes = stats_dict['runtime_seconds'] / 60
        mb_downloaded = stats_dict['bytes_downloaded'] / 1024 / 1024
        
        stats_dict.update({
            'runtime_minutes': runtime_minutes,
            'mb_downloaded': mb_downloaded,
            'total_pages': self.stats.pages_crawled
        })
        
        self.logger.print_summary(stats_dict)
    
    async def _cleanup(self) -> None:
        """Cleanup risorse"""
        if self.fetcher:
            await self.fetcher.close()
        
        self.is_running = False
        
        self.logger.info("🧹 Cleanup completato")