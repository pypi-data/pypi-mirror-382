"""
Client webhook per notifiche esterne (Slack, Discord, Telegram, Custom)
"""
import httpx
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class WebhookType(Enum):
    """Tipi di webhook supportati"""
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    CUSTOM = "custom"


@dataclass
class ScanNotification:
    """Dati notifica scansione completata"""
    project_name: str
    url: str
    total_pages: int
    total_issues: int
    critical_issues: int
    seo_score: float
    duration_seconds: int
    timestamp: str
    report_url: Optional[str] = None


class WebhookClient:
    """Client per invio notifiche webhook"""

    def __init__(self, timeout: int = 10):
        self.client = httpx.AsyncClient(timeout=timeout)

    async def send_scan_notification(
        self,
        notification: ScanNotification,
        webhook_url: str,
        webhook_type: WebhookType = WebhookType.CUSTOM
    ) -> bool:
        """
        Invia notifica scansione completata

        Args:
            notification: Dati scansione
            webhook_url: URL webhook destinazione
            webhook_type: Tipo webhook (slack/discord/telegram/custom)

        Returns:
            bool: True se invio riuscito
        """
        try:
            if webhook_type == WebhookType.SLACK:
                payload = self._build_slack_payload(notification)
            elif webhook_type == WebhookType.DISCORD:
                payload = self._build_discord_payload(notification)
            elif webhook_type == WebhookType.TELEGRAM:
                # Telegram usa URL diverso con bot token e chat_id
                return await self._send_telegram(notification, webhook_url)
            else:  # CUSTOM
                payload = self._build_custom_payload(notification)

            response = await self.client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            return response.status_code in [200, 201, 204]

        except Exception as e:
            print(f"❌ Errore invio webhook: {e}")
            return False

    def _build_slack_payload(self, notification: ScanNotification) -> Dict[str, Any]:
        """Costruisce payload Slack Incoming Webhook"""
        # Determina colore in base a severità
        if notification.critical_issues > 10:
            color = "#FF0000"  # Rosso
            status = "⚠️ ATTENZIONE"
        elif notification.critical_issues > 0:
            color = "#FFA500"  # Arancione
            status = "⚡ CONTROLLO RICHIESTO"
        else:
            color = "#00FF00"  # Verde
            status = "✅ TUTTO OK"

        duration_min = notification.duration_seconds // 60
        duration_sec = notification.duration_seconds % 60

        payload = {
            "text": f"🔍 Scansione SEO Completata: {notification.project_name}",
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "📊 Stato",
                            "value": status,
                            "short": True
                        },
                        {
                            "title": "⭐ Score SEO",
                            "value": f"{notification.seo_score:.1f}/100",
                            "short": True
                        },
                        {
                            "title": "🌐 URL",
                            "value": notification.url,
                            "short": False
                        },
                        {
                            "title": "📄 Pagine Scansionate",
                            "value": str(notification.total_pages),
                            "short": True
                        },
                        {
                            "title": "🐛 Issues Totali",
                            "value": str(notification.total_issues),
                            "short": True
                        },
                        {
                            "title": "🔴 Issues Critici",
                            "value": str(notification.critical_issues),
                            "short": True
                        },
                        {
                            "title": "⏱️ Durata",
                            "value": f"{duration_min}m {duration_sec}s",
                            "short": True
                        }
                    ],
                    "footer": "PyPrestaScan",
                    "footer_icon": "https://raw.githubusercontent.com/andreapianidev/pyprestascan/main/docs/logo.png",
                    "ts": int(datetime.fromisoformat(notification.timestamp).timestamp())
                }
            ]
        }

        if notification.report_url:
            payload["attachments"][0]["actions"] = [
                {
                    "type": "button",
                    "text": "📊 Visualizza Report",
                    "url": notification.report_url
                }
            ]

        return payload

    def _build_discord_payload(self, notification: ScanNotification) -> Dict[str, Any]:
        """Costruisce payload Discord Webhook"""
        # Determina colore embed
        if notification.critical_issues > 10:
            color = 0xFF0000  # Rosso
            emoji = "🔴"
        elif notification.critical_issues > 0:
            color = 0xFFA500  # Arancione
            emoji = "🟠"
        else:
            color = 0x00FF00  # Verde
            emoji = "🟢"

        duration_min = notification.duration_seconds // 60
        duration_sec = notification.duration_seconds % 60

        embed = {
            "title": f"🔍 Scansione SEO Completata",
            "description": f"**{notification.project_name}**\n{notification.url}",
            "color": color,
            "fields": [
                {
                    "name": "📊 Score SEO",
                    "value": f"⭐ {notification.seo_score:.1f}/100",
                    "inline": True
                },
                {
                    "name": "📄 Pagine",
                    "value": str(notification.total_pages),
                    "inline": True
                },
                {
                    "name": "🐛 Issues",
                    "value": str(notification.total_issues),
                    "inline": True
                },
                {
                    "name": f"{emoji} Issues Critici",
                    "value": str(notification.critical_issues),
                    "inline": True
                },
                {
                    "name": "⏱️ Durata",
                    "value": f"{duration_min}m {duration_sec}s",
                    "inline": True
                }
            ],
            "footer": {
                "text": "PyPrestaScan",
                "icon_url": "https://raw.githubusercontent.com/andreapianidev/pyprestascan/main/docs/logo.png"
            },
            "timestamp": notification.timestamp
        }

        if notification.report_url:
            embed["url"] = notification.report_url

        return {
            "embeds": [embed]
        }

    async def _send_telegram(self, notification: ScanNotification, bot_config: str) -> bool:
        """
        Invia notifica Telegram

        Args:
            notification: Dati scansione
            bot_config: Format "bot_token:chat_id"
        """
        try:
            bot_token, chat_id = bot_config.split(":", 1)
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

            # Emoji status
            if notification.critical_issues > 10:
                emoji = "🔴"
            elif notification.critical_issues > 0:
                emoji = "🟠"
            else:
                emoji = "🟢"

            duration_min = notification.duration_seconds // 60
            duration_sec = notification.duration_seconds % 60

            message = f"""
🔍 *Scansione SEO Completata* {emoji}

*Progetto:* {notification.project_name}
*URL:* {notification.url}

📊 *Risultati:*
⭐ Score SEO: {notification.seo_score:.1f}/100
📄 Pagine: {notification.total_pages}
🐛 Issues: {notification.total_issues}
🔴 Critici: {notification.critical_issues}
⏱️ Durata: {duration_min}m {duration_sec}s
"""

            if notification.report_url:
                message += f"\n📊 [Visualizza Report]({notification.report_url})"

            response = await self.client.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )

            return response.status_code == 200

        except Exception as e:
            print(f"❌ Errore Telegram: {e}")
            return False

    def _build_custom_payload(self, notification: ScanNotification) -> Dict[str, Any]:
        """Costruisce payload generico JSON per webhook custom"""
        return {
            "event": "scan_completed",
            "timestamp": notification.timestamp,
            "data": {
                "project_name": notification.project_name,
                "url": notification.url,
                "metrics": {
                    "total_pages": notification.total_pages,
                    "total_issues": notification.total_issues,
                    "critical_issues": notification.critical_issues,
                    "seo_score": notification.seo_score
                },
                "duration_seconds": notification.duration_seconds,
                "report_url": notification.report_url
            }
        }

    async def test_webhook(self, webhook_url: str, webhook_type: WebhookType) -> bool:
        """
        Testa connessione webhook

        Returns:
            bool: True se webhook raggiungibile
        """
        test_notification = ScanNotification(
            project_name="Test PyPrestaScan",
            url="https://example.com",
            total_pages=10,
            total_issues=5,
            critical_issues=0,
            seo_score=95.0,
            duration_seconds=30,
            timestamp=datetime.now().isoformat()
        )

        return await self.send_scan_notification(
            test_notification,
            webhook_url,
            webhook_type
        )

    async def close(self):
        """Chiudi connessione HTTP"""
        await self.client.aclose()


# Helper functions per facilità d'uso

async def send_slack_notification(webhook_url: str, notification: ScanNotification) -> bool:
    """Helper per Slack"""
    client = WebhookClient()
    try:
        return await client.send_scan_notification(notification, webhook_url, WebhookType.SLACK)
    finally:
        await client.close()


async def send_discord_notification(webhook_url: str, notification: ScanNotification) -> bool:
    """Helper per Discord"""
    client = WebhookClient()
    try:
        return await client.send_scan_notification(notification, webhook_url, WebhookType.DISCORD)
    finally:
        await client.close()


async def send_telegram_notification(bot_config: str, notification: ScanNotification) -> bool:
    """Helper per Telegram (bot_config = 'bot_token:chat_id')"""
    client = WebhookClient()
    try:
        return await client.send_scan_notification(notification, bot_config, WebhookType.TELEGRAM)
    finally:
        await client.close()
