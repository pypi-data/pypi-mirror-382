"""
Excel Report Exporter avanzato con formattazione professionale
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell


class ExcelReportExporter:
    """
    Export Excel con formattazione professionale per report SEO

    Features:
    - Executive Summary con KPI cards
    - Issues dettagliati con conditional formatting
    - Fix applicabili prioritizzati
    - Grafici interattivi
    - Protezione fogli sensibili

    Example:
        >>> exporter = ExcelReportExporter(scan_results)
        >>> file_path = exporter.export("report.xlsx")
    """

    def __init__(self, scan_results: Dict[str, Any]):
        """
        Args:
            scan_results: Risultati scansione con chiavi:
                - statistics: dict con metriche generali
                - issues: list di issue rilevati
                - pages: list di pagine scansionate
                - fixes: list di fix suggeriti (opzionale)
        """
        self.results = scan_results
        self.workbook = None
        self.formats = {}

    def export(self, output_path: Path) -> Path:
        """
        Esporta report Excel completo

        Args:
            output_path: Path dove salvare file Excel

        Returns:
            Path del file creato
        """
        output_path = Path(output_path)

        # Crea workbook
        self.workbook = xlsxwriter.Workbook(str(output_path))
        self._create_formats()

        # Crea sheets
        self._create_executive_summary()
        self._create_issues_sheet()
        self._create_pages_sheet()

        if self.results.get('fixes'):
            self._create_fixes_sheet()

        # Chiudi e salva
        self.workbook.close()

        return output_path

    def _create_formats(self):
        """Crea formati riutilizzabili"""
        wb = self.workbook

        # Header format
        self.formats['header'] = wb.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#667eea',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        # Title format
        self.formats['title'] = wb.add_format({
            'bold': True,
            'font_size': 18,
            'font_color': '#667eea'
        })

        # KPI format
        self.formats['kpi_label'] = wb.add_format({
            'bold': True,
            'font_size': 11,
            'align': 'right'
        })

        self.formats['kpi_value'] = wb.add_format({
            'font_size': 14,
            'bold': True,
            'num_format': '#,##0'
        })

        # Severity formats
        self.formats['critical'] = wb.add_format({
            'bg_color': '#ffebee',
            'font_color': '#c62828',
            'bold': True
        })

        self.formats['warning'] = wb.add_format({
            'bg_color': '#fff3e0',
            'font_color': '#ef6c00'
        })

        self.formats['info'] = wb.add_format({
            'bg_color': '#e3f2fd',
            'font_color': '#1565c0'
        })

        # URL link format
        self.formats['url'] = wb.add_format({
            'font_color': 'blue',
            'underline': True
        })

        # Number formats
        self.formats['number'] = wb.add_format({'num_format': '#,##0'})
        self.formats['percent'] = wb.add_format({'num_format': '0.00%'})

    def _create_executive_summary(self):
        """Sheet 1: Executive Summary con KPI e grafici"""
        sheet = self.workbook.add_worksheet('Executive Summary')
        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 20)

        stats = self.results.get('statistics', {})

        # Title
        sheet.merge_range('A1:B1', 'SEO Scan Report', self.formats['title'])
        sheet.write('A2', f"Generato: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # KPI Cards
        row = 4
        kpis = [
            ('Pagine Scansionate:', stats.get('total_pages', 0)),
            ('Issues Totali:', stats.get('total_issues', 0)),
            ('Issues Critici:', stats.get('critical_issues', 0)),
            ('Issues Warning:', stats.get('warning_issues', 0)),
            ('Issues Info:', stats.get('info_issues', 0)),
            ('Tasso Successo:', stats.get('success_rate', 0) / 100),
            ('Score SEO Medio:', stats.get('avg_seo_score', 0)),
        ]

        for label, value in kpis:
            sheet.write(row, 0, label, self.formats['kpi_label'])

            if 'Tasso' in label:
                sheet.write(row, 1, value, self.formats['percent'])
            else:
                sheet.write(row, 1, value, self.formats['kpi_value'])
            row += 1

        # Grafico Issues per severity
        if stats.get('critical_issues', 0) > 0:
            chart = self.workbook.add_chart({'type': 'pie'})

            chart.add_series({
                'name': 'Issues per Severity',
                'categories': ['Executive Summary', 6, 0, 8, 0],  # Labels
                'values': ['Executive Summary', 6, 1, 8, 1],      # Values
                'data_labels': {'percentage': True},
                'points': [
                    {'fill': {'color': '#c62828'}},  # Critical
                    {'fill': {'color': '#ef6c00'}},  # Warning
                    {'fill': {'color': '#1565c0'}},  # Info
                ]
            })

            chart.set_title({'name': 'Distribuzione Issues'})
            chart.set_legend({'position': 'bottom'})

            sheet.insert_chart('D4', chart, {'x_scale': 1.5, 'y_scale': 1.5})

    def _create_issues_sheet(self):
        """Sheet 2: Issues dettagliati con filtri"""
        sheet = self.workbook.add_worksheet('Issues Dettagliati')

        # Headers
        headers = [
            'Severity',
            'Codice',
            'Descrizione',
            'Occorrenze',
            'Pagine Coinvolte',
            'Impatto SEO'
        ]

        for col, header in enumerate(headers):
            sheet.write(0, col, header, self.formats['header'])

        # Column widths
        sheet.set_column('A:A', 12)  # Severity
        sheet.set_column('B:B', 25)  # Codice
        sheet.set_column('C:C', 50)  # Descrizione
        sheet.set_column('D:D', 12)  # Occorrenze
        sheet.set_column('E:E', 15)  # Pagine
        sheet.set_column('F:F', 15)  # Impatto

        # Data
        issues = self.results.get('issues', [])
        row = 1

        for issue in issues:
            severity = issue.get('severity', 'INFO')
            severity_format = self.formats.get(severity.lower(), None)

            sheet.write(row, 0, severity, severity_format)
            sheet.write(row, 1, issue.get('code', ''))
            sheet.write(row, 2, issue.get('description', ''))
            sheet.write(row, 3, issue.get('occurrences', 0), self.formats['number'])
            sheet.write(row, 4, issue.get('affected_pages', 0), self.formats['number'])

            # Calcola impatto (weight * occurrences)
            impact = issue.get('weight', 1) * issue.get('occurrences', 0)
            sheet.write(row, 5, impact, self.formats['number'])

            row += 1

        # Auto-filter
        if row > 1:
            sheet.autofilter(0, 0, row - 1, len(headers) - 1)

        # Freeze panes (header row)
        sheet.freeze_panes(1, 0)

    def _create_pages_sheet(self):
        """Sheet 3: Pagine scansionate"""
        sheet = self.workbook.add_worksheet('Pagine')

        headers = [
            'URL',
            'Titolo',
            'Status Code',
            'Score SEO',
            'Issues',
            'Tipo Pagina'
        ]

        for col, header in enumerate(headers):
            sheet.write(0, col, header, self.formats['header'])

        sheet.set_column('A:A', 60)  # URL
        sheet.set_column('B:B', 40)  # Title
        sheet.set_column('C:C', 12)  # Status
        sheet.set_column('D:D', 12)  # Score
        sheet.set_column('E:E', 10)  # Issues
        sheet.set_column('F:F', 15)  # Tipo

        pages = self.results.get('pages', [])
        row = 1

        for page in pages:
            url = page.get('url', '')
            sheet.write_url(row, 0, url, self.formats['url'], string=url[:60])
            sheet.write(row, 1, page.get('title', '')[:40])
            sheet.write(row, 2, page.get('status_code', 0))
            sheet.write(row, 3, page.get('seo_score', 0))
            sheet.write(row, 4, page.get('issue_count', 0))

            # Tipo pagina
            page_type = 'Unknown'
            if page.get('is_product'):
                page_type = 'Product'
            elif page.get('is_category'):
                page_type = 'Category'
            elif page.get('is_cms'):
                page_type = 'CMS'

            sheet.write(row, 5, page_type)
            row += 1

        if row > 1:
            sheet.autofilter(0, 0, row - 1, len(headers) - 1)

        sheet.freeze_panes(1, 0)

    def _create_fixes_sheet(self):
        """Sheet 4: Fix Applicabili (opzionale)"""
        sheet = self.workbook.add_worksheet('Fix Suggeriti')

        headers = [
            'Priority',
            'URL Pagina',
            'Tipo Fix',
            'Valore Attuale',
            'Valore Suggerito',
            'Confidence',
            'SQL Query'
        ]

        for col, header in enumerate(headers):
            sheet.write(0, col, header, self.formats['header'])

        sheet.set_column('A:A', 10)  # Priority
        sheet.set_column('B:B', 50)  # URL
        sheet.set_column('C:C', 20)  # Tipo
        sheet.set_column('D:D', 40)  # Current
        sheet.set_column('E:E', 40)  # Suggested
        sheet.set_column('F:F', 12)  # Confidence
        sheet.set_column('G:G', 60)  # SQL

        fixes = self.results.get('fixes', [])
        # Ordina per confidence DESC
        fixes_sorted = sorted(
            fixes,
            key=lambda x: x.get('confidence', 0),
            reverse=True
        )

        row = 1
        for idx, fix in enumerate(fixes_sorted, 1):
            sheet.write(row, 0, idx)
            sheet.write_url(row, 1, fix.get('page_url', ''), self.formats['url'])
            sheet.write(row, 2, fix.get('fix_type', ''))
            sheet.write(row, 3, fix.get('current_value', '')[:40])
            sheet.write(row, 4, fix.get('suggested_value', '')[:40])
            sheet.write(row, 5, fix.get('confidence', 0), self.formats['percent'])
            sheet.write(row, 6, fix.get('sql_query', ''))

            row += 1

        if row > 1:
            sheet.autofilter(0, 0, row - 1, len(headers) - 1)

        sheet.freeze_panes(1, 0)

        # Protect sheet (optional - users can still filter/sort)
        # sheet.protect()


# Utility function

def export_to_excel(
    scan_results: Dict[str, Any],
    output_path: Path,
    include_fixes: bool = True
) -> Path:
    """
    Export rapido a Excel

    Args:
        scan_results: Risultati scansione
        output_path: Path output
        include_fixes: Include sheet fix suggeriti

    Returns:
        Path file creato
    """
    if not include_fixes:
        scan_results = {**scan_results, 'fixes': None}

    exporter = ExcelReportExporter(scan_results)
    return exporter.export(output_path)
