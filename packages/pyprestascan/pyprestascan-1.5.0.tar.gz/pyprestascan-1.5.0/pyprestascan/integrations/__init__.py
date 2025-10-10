"""
Modulo integrazioni esterne (PrestaShop API, Excel Export, Webhook, etc.)
"""
from .prestashop_api import PrestaShopAPIClient
from .excel_exporter import ExcelReportExporter
from .webhook_client import WebhookClient, ScanNotification, WebhookType

__all__ = [
    'PrestaShopAPIClient',
    'ExcelReportExporter',
    'WebhookClient',
    'ScanNotification',
    'WebhookType'
]
