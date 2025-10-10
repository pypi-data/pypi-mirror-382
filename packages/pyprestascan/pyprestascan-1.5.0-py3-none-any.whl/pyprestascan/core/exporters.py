"""
Modulo per export report CSV, JSON e HTML
"""
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .storage import CrawlDatabase
from .utils import RichLogger


class ReportExporter:
    """Esportatore report multi-formato"""
    
    def __init__(self,
                 db: CrawlDatabase,
                 export_dir: Path,
                 base_url: str = "",
                 include_generic_alt: bool = False,
                 logger: Optional[RichLogger] = None):

        self.db = db
        self.export_dir = Path(export_dir)
        self.base_url = base_url
        self.include_generic_alt = include_generic_alt
        self.logger = logger or RichLogger()
        
        # Crea directory se non esiste
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 per template HTML
        template_dir = Path(__file__).parent.parent / "reports" / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    async def export_all(self) -> None:
        """Esporta tutti i formati di report"""
        self.logger.info("📊 Inizio generazione report...")
        
        # Raccogli statistiche
        stats = await self.db.get_crawl_stats()
        
        # Export CSV
        await self._export_csv()
        
        # Export JSON
        await self._export_json(stats)
        
        # Export HTML
        await self._export_html(stats)
        
        self.logger.success("✅ Tutti i report generati")
    
    async def _export_csv(self) -> None:
        """Esporta report CSV"""
        self.logger.info("📄 Generazione CSV...")
        
        # Pages CSV
        await self._export_pages_csv()
        
        # Images issues CSV
        await self._export_images_csv()
        
        # Issues CSV
        await self._export_issues_csv()
        
        # Duplicates CSV
        await self._export_duplicates_csv()
        
        self.logger.success("✅ CSV completati")
    
    async def _export_pages_csv(self) -> None:
        """Esporta dati pagine in CSV"""
        pages_data = await self.db.export_pages()
        
        if not pages_data:
            return
        
        # Converti timestamp e JSON fields
        for page in pages_data:
            # Parse JSON fields
            if page.get('headings_map'):
                page['headings_map'] = json.dumps(json.loads(page['headings_map']))
            if page.get('hreflang_map'):
                page['hreflang_map'] = json.dumps(json.loads(page['hreflang_map']))
            if page.get('jsonld_types'):
                page['jsonld_types'] = json.dumps(json.loads(page['jsonld_types']))
            
            # Format timestamp
            if page.get('crawled_at'):
                page['crawled_at'] = str(page['crawled_at'])
        
        # Scrivi CSV
        csv_path = self.export_dir / "pages.csv"
        
        if pages_data:
            fieldnames = pages_data[0].keys()
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(pages_data)
        
        self.logger.info(f"📄 pages.csv: {len(pages_data)} righe")
    
    async def _export_images_csv(self) -> None:
        """Esporta immagini con problemi ALT in CSV"""
        images_data = await self.db.export_images_issues(self.include_generic_alt)
        
        if not images_data:
            return
        
        csv_path = self.export_dir / "images_missing_alt.csv"
        
        fieldnames = ['page_url', 'image_src', 'alt_text', 'alt_status']
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(images_data)
        
        self.logger.info(f"🖼️ images_missing_alt.csv: {len(images_data)} righe")
    
    async def _export_issues_csv(self) -> None:
        """Esporta issues SEO in CSV"""
        issues_data = await self.db.export_issues()
        
        if not issues_data:
            return
        
        # Parse meta JSON
        for issue in issues_data:
            if issue.get('meta'):
                try:
                    meta = json.loads(issue['meta'])
                    issue['meta'] = json.dumps(meta, ensure_ascii=False)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        csv_path = self.export_dir / "issues.csv"
        
        fieldnames = ['page_url', 'severity', 'code', 'message', 'meta']
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(issues_data)
        
        self.logger.info(f"⚠️ issues.csv: {len(issues_data)} righe")
    
    async def _export_duplicates_csv(self) -> None:
        """Esporta duplicati rilevati in CSV"""
        duplicates_data = await self.db.export_duplicates()
        
        if not duplicates_data:
            return
        
        csv_path = self.export_dir / "duplicates.csv"
        
        fieldnames = ['content_hash', 'url1', 'url2', 'similarity_score']
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(duplicates_data)
        
        self.logger.info(f"🔄 duplicates.csv: {len(duplicates_data)} righe")
    
    async def _export_json(self, stats: Dict[str, Any]) -> None:
        """Esporta report completo JSON"""
        self.logger.info("📄 Generazione JSON...")
        
        # Raccogli tutti i dati
        pages_data = await self.db.export_pages()
        images_data = await self.db.export_images_issues(self.include_generic_alt)
        issues_data = await self.db.export_issues()
        duplicates_data = await self.db.export_duplicates()
        
        # Componi report completo
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'tool': 'PyPrestaScan',
                'version': '1.0.0',
                'total_pages': len(pages_data),
                'total_issues': len(issues_data),
                'total_duplicates': len(duplicates_data),
                'images_with_alt_issues': len(images_data)
            },
            'statistics': stats,
            'pages': pages_data,
            'images_issues': images_data,
            'issues': issues_data,
            'duplicates': duplicates_data
        }
        
        # Scrivi JSON
        json_path = self.export_dir / "report.json"
        
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(report, jsonfile, indent=2, ensure_ascii=False, default=str)
        
        self.logger.success("✅ report.json completato")
    
    async def _export_html(self, stats: Dict[str, Any]) -> None:
        """Esporta dashboard HTML interattiva"""
        self.logger.info("🌐 Generazione dashboard HTML...")
        
        # Copia assets (CSS/JS) se non esistenti
        await self._copy_assets()
        
        # Raccogli dati per template
        template_data = await self._prepare_html_data(stats)
        
        # Renderizza template
        template = self.jinja_env.get_template('report.html.j2')
        html_content = template.render(**template_data)
        
        # Scrivi HTML
        html_path = self.export_dir / "report.html"
        with open(html_path, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)
        
        self.logger.success("✅ Dashboard HTML completata")
    
    async def _prepare_html_data(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dati per template HTML"""
        
        # Dati statistiche base
        general_stats = stats.get('general', {})
        status_stats = stats.get('status', {})
        issue_stats = stats.get('issues', {})
        alt_stats = stats.get('alt_text', {})
        
        # Calcola KPI principali
        total_pages = general_stats.get('total_pages', 0)
        pages_2xx = status_stats.get('2xx', 0)
        pages_with_issues = sum(issue_stats.values())
        images_no_alt = alt_stats.get('MISSING', 0) + alt_stats.get('EMPTY', 0)
        
        # Percentuali
        success_rate = (pages_2xx / max(total_pages, 1)) * 100
        pages_with_issues_pct = (pages_with_issues / max(total_pages, 1)) * 100
        
        # Top issues (più comuni)
        issues_data = await self.db.export_issues()
        top_issues = self._get_top_issues(issues_data)
        
        # Pagine con score più basso
        pages_data = await self.db.export_pages()
        low_score_pages = self._get_low_score_pages(pages_data)
        
        # Distribuzione score
        score_distribution = self._get_score_distribution(pages_data)

        # Immagini senza ALT
        images_issues = await self.db.export_images_issues(include_generic=self.include_generic_alt)

        # Estrai nome sito dall'URL
        from urllib.parse import urlparse
        site_url = self.base_url or "Unknown"
        parsed_url = urlparse(site_url)
        site_name = parsed_url.netloc.replace('www.', '') if parsed_url.netloc else "Unknown"

        # Performance e duplicati
        avg_ttfb = general_stats.get('avg_ttfb_ms', 0)
        duplicates_count = general_stats.get('duplicates', 0)
        pages_failed = status_stats.get('4xx', 0) + status_stats.get('5xx', 0)

        # Template data
        return {
            'site_name': site_name,
            'site_url': site_url,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tool_version': '1.5.0',

            # KPI
            'total_pages': total_pages,
            'success_rate': round(success_rate or 0, 1),
            'pages_with_issues': pages_with_issues,
            'pages_with_issues_pct': round(pages_with_issues_pct or 0, 1),
            'images_no_alt': images_no_alt,
            'avg_score': round(general_stats.get('avg_score') or 0, 1),
            'avg_ttfb': round(avg_ttfb, 0),
            'duplicates_count': duplicates_count,
            'pages_failed': pages_failed,

            # Statistiche dettagliate
            'status_stats': status_stats,
            'issue_stats': issue_stats,
            'alt_stats': alt_stats,

            # Breakdown per tipo pagina
            'product_pages': general_stats.get('product_pages', 0),
            'category_pages': general_stats.get('category_pages', 0),
            'cms_pages': general_stats.get('cms_pages', 0),
            
            # Top issues e pagine problematiche
            'top_issues': top_issues[:10],  # Top 10
            'low_score_pages': low_score_pages[:20],  # Top 20
            'score_distribution': score_distribution,
            'images_issues': images_issues[:100],  # Top 100 immagini problematiche
            
            # Dati per grafici (JSON encoded)
            'chart_data': {
                'status': self._prepare_chart_data(status_stats),
                'issues_by_severity': self._prepare_chart_data(issue_stats),
                'alt_text_status': self._prepare_chart_data(alt_stats),
                'score_distribution': score_distribution
            }
        }
    
    def _get_top_issues(self, issues_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ottieni top issues per frequenza"""
        if not issues_data:
            return []
        
        # Conta issues per codice
        issue_counts = {}
        for issue in issues_data:
            code = issue.get('code', 'UNKNOWN')
            if code not in issue_counts:
                issue_counts[code] = {
                    'code': code,
                    'message': issue.get('message', ''),
                    'severity': issue.get('severity', 'INFO'),
                    'count': 0,
                    'pages': set()
                }
            
            issue_counts[code]['count'] += 1
            issue_counts[code]['pages'].add(issue.get('page_url', ''))
        
        # Converti set a count
        for issue in issue_counts.values():
            issue['affected_pages'] = len(issue['pages'])
            del issue['pages']
        
        # Ordina per count
        return sorted(issue_counts.values(), key=lambda x: x['count'], reverse=True)
    
    def _get_low_score_pages(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ottieni pagine con score più basso"""
        if not pages_data:
            return []
        
        # Filtra pagine con score numerico
        scored_pages = []
        for page in pages_data:
            score = page.get('score', 0)
            try:
                score_num = float(score)
                scored_pages.append({
                    'url': page.get('url', ''),
                    'title': page.get('title', ''),
                    'score': score_num,
                    'status_code': page.get('status_code', 0),
                    'is_product': page.get('is_product', False),
                    'is_category': page.get('is_category', False)
                })
            except (ValueError, TypeError):
                continue
        
        # Ordina per score crescente
        return sorted(scored_pages, key=lambda x: x['score'])
    
    def _get_score_distribution(self, pages_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Ottieni distribuzione score in range"""
        if not pages_data:
            return {}
        
        distribution = {
            '0-20': 0,
            '21-40': 0,
            '41-60': 0,
            '61-80': 0,
            '81-100': 0
        }
        
        for page in pages_data:
            score = page.get('score', 0)
            try:
                score_num = float(score)
                if score_num <= 20:
                    distribution['0-20'] += 1
                elif score_num <= 40:
                    distribution['21-40'] += 1
                elif score_num <= 60:
                    distribution['41-60'] += 1
                elif score_num <= 80:
                    distribution['61-80'] += 1
                else:
                    distribution['81-100'] += 1
            except (ValueError, TypeError):
                continue
        
        return distribution
    
    def _prepare_chart_data(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dati per Chart.js"""
        if not data_dict:
            return {'labels': [], 'data': []}
        
        # Filtra valori zero se possibile
        filtered_data = {k: v for k, v in data_dict.items() if v > 0}
        
        if not filtered_data:
            filtered_data = data_dict  # Usa tutti se tutti sono zero
        
        return {
            'labels': list(filtered_data.keys()),
            'data': list(filtered_data.values())
        }
    
    async def _copy_assets(self) -> None:
        """Prepara assets per il report (ora usa CDN, quindi non servono file locali)"""
        # Gli assets CSS/JS sono ora caricati da CDN nel template HTML
        # per una migliore compatibilità e prestazioni
        pass