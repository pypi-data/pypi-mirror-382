"""
HTTP fetcher asincrono con supporto per robots.txt, retry e rate limiting
"""
import asyncio
import time
from typing import Optional, Dict, List, Tuple, Any
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass
from datetime import datetime

import httpx
from aiolimiter import AsyncLimiter

from ..core.utils import RichLogger


@dataclass
class FetchResponse:
    """Risposta di una richiesta HTTP"""
    url: str
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    content_type: str
    content_length: int
    ttfb_ms: int  # Time to First Byte in milliseconds
    total_time_ms: int
    error: Optional[str] = None


@dataclass
class RobotsInfo:
    """Informazioni da robots.txt"""
    allowed: bool
    crawl_delay: Optional[float] = None  # in seconds
    sitemap_urls: Optional[List[str]] = None


class HttpFetcher:
    """Client HTTP asincrono con gestione robots.txt e rate limiting"""
    
    def __init__(self, 
                 concurrency: int = 20,
                 delay_ms: int = 0,
                 timeout: int = 15,
                 user_agent: str = "PyPrestaScan/1.0",
                 auth: Optional[Tuple[str, str]] = None,
                 logger: Optional[RichLogger] = None):
        
        self.concurrency = concurrency
        self.delay_ms = delay_ms
        self.timeout = timeout
        self.user_agent = user_agent
        self.auth = auth
        self.logger = logger or RichLogger()
        
        # Rate limiter globale
        self.limiter = AsyncLimiter(max_rate=concurrency, time_period=1.0)
        
        # Semaforo per limitare richieste concurrent
        self.semaphore = asyncio.Semaphore(concurrency)
        
        # Cache robots.txt per dominio (stored as boolean for now without reppy)
        self.robots_cache: Dict[str, bool] = {}
        
        # Client HTTP
        self.client: Optional[httpx.AsyncClient] = None
        
        # Statistiche
        self.stats = {
            'requests_made': 0,
            'requests_failed': 0,
            'bytes_downloaded': 0,
            'robots_checks': 0,
            'robots_denied': 0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def start(self) -> None:
        """Inizializza client HTTP"""
        if self.client:
            return
        
        # Configurazione client HTTPX
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_connections=self.concurrency * 2),
            headers={'User-Agent': self.user_agent},
            auth=self.auth,
            follow_redirects=True,
            max_redirects=5
        )
        
        self.logger.info("🌐 Client HTTP inizializzato", "🔧")
    
    async def close(self) -> None:
        """Chiude client HTTP"""
        if self.client:
            await self.client.aclose()
            self.client = None
        
        # Log statistiche finali
        self.logger.info(f"📊 Richieste: {self.stats['requests_made']}, "
                        f"Fallite: {self.stats['requests_failed']}, "
                        f"MB scaricati: {self.stats['bytes_downloaded'] / 1024 / 1024:.1f}")
    
    async def _get_robots_txt(self, domain: str):
        """Recupera e caching robots.txt per dominio"""
        if domain in self.robots_cache:
            return self.robots_cache[domain]
        
        robots_url = f"https://{domain}/robots.txt"
        
        try:
            response = await self.client.get(robots_url)
            self.stats['requests_made'] += 1
            
            if response.status_code == 200:
                # Simuliamo robots permissivo per ora (senza reppy)
                self.logger.robots_ok(f"robots.txt trovato per {domain}")
            else:
                self.logger.debug(f"📥 robots.txt non trovato per {domain}, assumo permissivo")
            
            # Memorizza come permissivo
            self.robots_cache[domain] = True
            return True
            
        except Exception as e:
            # In caso di errore, assumo permissivo
            self.logger.debug(f"⚠️ Errore caricamento robots.txt per {domain}: {e}")
            self.robots_cache[domain] = True
            return True
    
    async def check_robots_allowed(self, url: str) -> RobotsInfo:
        """Verifica se URL è permesso da robots.txt"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        robots_ok = await self._get_robots_txt(domain)
        self.stats['robots_checks'] += 1
        
        # Per ora assumiamo sempre permesso (senza parsing robots.txt completo)
        allowed = True  
        
        if not allowed:
            self.stats['robots_denied'] += 1
            self.logger.robots_deny(url)
        
        # Default crawl delay
        crawl_delay = None
        
        # Nessuna sitemap per ora
        sitemaps = []
        
        return RobotsInfo(
            allowed=allowed,
            crawl_delay=crawl_delay,
            sitemap_urls=sitemaps
        )
    
    async def _apply_delays(self, robots_info: Optional[RobotsInfo] = None) -> None:
        """Applica delay configurato e/o da robots.txt"""
        # Delay base configurato
        if self.delay_ms > 0:
            await asyncio.sleep(self.delay_ms / 1000.0)
        
        # Delay da robots.txt (se maggiore)
        if robots_info and robots_info.crawl_delay:
            robots_delay_ms = robots_info.crawl_delay * 1000
            if robots_delay_ms > self.delay_ms:
                additional_delay = (robots_delay_ms - self.delay_ms) / 1000.0
                await asyncio.sleep(additional_delay)
    
    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> FetchResponse:
        """Effettua richiesta HTTP con retry e metriche"""
        start_time = time.perf_counter()
        ttfb_time = None
        
        for attempt in range(3):  # Max 3 retry
            try:
                response = await self.client.request(method, url, **kwargs)
                
                # Calcola TTFB (prima volta che riceviamo risposta)
                if ttfb_time is None:
                    ttfb_time = time.perf_counter()
                
                self.stats['requests_made'] += 1
                
                # Se è un errore temporaneo, ritenta
                if response.status_code in (429, 502, 503, 504) and attempt < 2:
                    retry_delay = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    self.logger.debug(f"🔄 Retry {attempt + 1} per {url} dopo {retry_delay}s")
                    await asyncio.sleep(retry_delay)
                    continue
                
                # Leggi contenuto
                content = response.content
                text = ""
                
                # Decodifica text solo per content-type appropriati
                content_type = response.headers.get('content-type', '').lower()
                if any(ct in content_type for ct in ['text/', 'application/json', 'application/xml']):
                    text = response.text
                
                total_time = time.perf_counter() - start_time
                ttfb = ttfb_time - start_time if ttfb_time else total_time
                
                self.stats['bytes_downloaded'] += len(content)
                
                return FetchResponse(
                    url=str(response.url),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    content=content,
                    text=text,
                    content_type=content_type,
                    content_length=len(content),
                    ttfb_ms=int(ttfb * 1000),
                    total_time_ms=int(total_time * 1000)
                )
                
            except httpx.TimeoutException as e:
                if attempt < 2:
                    self.logger.debug(f"⏱️ Timeout per {url}, retry {attempt + 1}")
                    continue
                
                self.stats['requests_failed'] += 1
                return FetchResponse(
                    url=url,
                    status_code=0,
                    headers={},
                    content=b'',
                    text='',
                    content_type='',
                    content_length=0,
                    ttfb_ms=0,
                    total_time_ms=int((time.perf_counter() - start_time) * 1000),
                    error=f"Timeout: {e}"
                )
                
            except Exception as e:
                if attempt < 2:
                    self.logger.debug(f"❌ Errore per {url}: {e}, retry {attempt + 1}")
                    continue
                
                self.stats['requests_failed'] += 1
                return FetchResponse(
                    url=url,
                    status_code=0,
                    headers={},
                    content=b'',
                    text='',
                    content_type='',
                    content_length=0,
                    ttfb_ms=0,
                    total_time_ms=int((time.perf_counter() - start_time) * 1000),
                    error=str(e)
                )
        
        # Non dovrebbe mai arrivare qui
        return FetchResponse(
            url=url, status_code=0, headers={}, content=b'', text='',
            content_type='', content_length=0, ttfb_ms=0, total_time_ms=0,
            error="Max retry raggiunto"
        )
    
    async def fetch(self, url: str, check_robots: bool = True) -> FetchResponse:
        """Fetch singolo URL con controlli robots.txt"""
        if not self.client:
            await self.start()
        
        # Controllo robots.txt
        robots_info = None
        if check_robots:
            robots_info = await self.check_robots_allowed(url)
            if not robots_info.allowed:
                return FetchResponse(
                    url=url,
                    status_code=403,
                    headers={},
                    content=b'',
                    text='',
                    content_type='',
                    content_length=0,
                    ttfb_ms=0,
                    total_time_ms=0,
                    error="Bloccato da robots.txt"
                )
        
        # Limiti di rate
        async with self.semaphore:
            async with self.limiter:
                # Applica delay
                await self._apply_delays(robots_info)
                
                # Effettua richiesta
                response = await self._make_request(url)
                
                # Log richiesta
                self.logger.page_crawled(url, response.status_code, response.ttfb_ms)
                
                return response
    
    async def fetch_batch(self, urls: List[str], check_robots: bool = True) -> List[FetchResponse]:
        """Fetch batch di URL in parallelo"""
        if not self.client:
            await self.start()
        
        # Crea task per ogni URL
        tasks = [self.fetch(url, check_robots) for url in urls]
        
        # Esegui in parallelo
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Gestisci eccezioni
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                results.append(FetchResponse(
                    url=urls[i],
                    status_code=0,
                    headers={},
                    content=b'',
                    text='',
                    content_type='',
                    content_length=0,
                    ttfb_ms=0,
                    total_time_ms=0,
                    error=str(response)
                ))
            else:
                results.append(response)
        
        return results
    
    async def fetch_sitemap(self, sitemap_url: str) -> List[str]:
        """Scarica e parsa sitemap XML"""
        response = await self.fetch(sitemap_url, check_robots=False)
        
        if response.status_code != 200 or not response.text:
            self.logger.debug(f"⚠️ Sitemap non accessibile: {sitemap_url}")
            return []
        
        urls = []
        try:
            # Parse XML semplificato per estrarre URL
            import re
            
            # Cerca <loc>URL</loc> in sitemap
            loc_pattern = r'<loc>(.*?)</loc>'
            matches = re.findall(loc_pattern, response.text, re.IGNORECASE)
            
            for match in matches:
                url = match.strip()
                if url and url.startswith(('http://', 'https://')):
                    urls.append(url)
            
            # Se è un sitemapindex, scarica anche le sitemap referenziate
            if '<sitemapindex' in response.text.lower():
                self.logger.info(f"🗺️ Sitemapindex trovato con {len(urls)} sitemap")
                
                # Scarica sitemap individuali
                all_urls = []
                for sitemap_ref in urls[:10]:  # Limita a 10 sitemap per evitare esplosione
                    sub_urls = await self.fetch_sitemap(sitemap_ref)
                    all_urls.extend(sub_urls)
                
                return all_urls
            
            else:
                self.logger.sitemap_found(sitemap_url, len(urls))
                return urls
                
        except Exception as e:
            self.logger.error(f"Errore parsing sitemap {sitemap_url}: {e}")
            return []
    
    async def discover_sitemaps(self, base_url: str) -> List[str]:
        """Scopre sitemap da URL base e robots.txt"""
        parsed = urlparse(base_url)
        domain = parsed.netloc
        
        sitemap_urls = set()
        
        # Sitemap standard
        standard_sitemap = f"https://{domain}/sitemap.xml"
        response = await self.fetch(standard_sitemap, check_robots=False)
        
        if response.status_code == 200:
            sitemap_urls.add(standard_sitemap)
        
        # Sitemap da robots.txt
        try:
            robots_info = await self.check_robots_allowed(base_url)
            if robots_info.sitemap_urls:
                sitemap_urls.update(robots_info.sitemap_urls)
        except Exception:
            pass
        
        return list(sitemap_urls)
    
    def get_stats(self) -> Dict[str, Any]:
        """Restituisce statistiche fetcher"""
        return self.stats.copy()