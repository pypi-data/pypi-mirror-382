"""
PrestaShop API Client per applicazione automatica fix SEO
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import httpx
import asyncio
from xml.etree import ElementTree as ET
import base64
from datetime import datetime


@dataclass
class APIResponse:
    """Risposta API PrestaShop"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    status_code: int = 200


class PrestaShopAPIError(Exception):
    """Eccezione custom per errori API"""
    pass


class PrestaShopAPIClient:
    """
    Client asincrono per API REST PrestaShop

    Supporta:
    - Autenticazione con Webservice Key
    - CRUD su products, categories, cms
    - Batch update per applicare fix multipli
    - Backup/rollback automatico

    Example:
        >>> client = PrestaShopAPIClient("https://shop.com", "YOUR_KEY")
        >>> await client.test_connection()
        >>> await client.update_product_meta(42, {"meta_description": "..."})
    """

    def __init__(self, shop_url: str, webservice_key: str, timeout: int = 30):
        """
        Args:
            shop_url: URL shop PrestaShop (es: https://myshop.com)
            webservice_key: Chiave webservice da backoffice
            timeout: Timeout richieste in secondi
        """
        self.shop_url = shop_url.rstrip('/')
        self.api_base = f"{self.shop_url}/api"
        self.webservice_key = webservice_key

        # Auth header (Basic Auth con key come username)
        auth_string = f"{webservice_key}:"
        auth_bytes = auth_string.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_string = base64_bytes.decode('ascii')

        self.headers = {
            'Authorization': f'Basic {base64_string}',
            'Content-Type': 'application/xml',
            'Accept': 'application/xml'
        }

        self.client = httpx.AsyncClient(timeout=timeout, headers=self.headers)

    async def test_connection(self) -> APIResponse:
        """
        Testa connessione API

        Returns:
            APIResponse con success=True se connessione OK
        """
        try:
            response = await self.client.get(f"{self.api_base}")

            if response.status_code == 200:
                return APIResponse(success=True, data={'message': 'Connessione OK'})
            else:
                return APIResponse(
                    success=False,
                    error=f"Status code: {response.status_code}",
                    status_code=response.status_code
                )
        except httpx.HTTPError as e:
            return APIResponse(success=False, error=str(e))

    async def get_product(self, product_id: int, language_id: int = 1) -> APIResponse:
        """
        Ottieni dettagli prodotto

        Args:
            product_id: ID prodotto PrestaShop
            language_id: ID lingua (default: 1)

        Returns:
            APIResponse con dati prodotto in formato dict
        """
        try:
            url = f"{self.api_base}/products/{product_id}"
            response = await self.client.get(url)

            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.text)
                product_data = self._xml_to_dict(root)

                return APIResponse(success=True, data=product_data)
            else:
                return APIResponse(
                    success=False,
                    error=f"Prodotto {product_id} non trovato",
                    status_code=response.status_code
                )
        except Exception as e:
            return APIResponse(success=False, error=str(e))

    async def update_product_meta(
        self,
        product_id: int,
        meta_data: Dict[str, str],
        language_id: int = 1
    ) -> APIResponse:
        """
        Aggiorna meta SEO prodotto

        Args:
            product_id: ID prodotto
            meta_data: Dict con chiavi: meta_title, meta_description, meta_keywords
            language_id: ID lingua

        Returns:
            APIResponse con success=True se update OK

        Example:
            >>> await client.update_product_meta(42, {
            ...     "meta_description": "Scarpe Nike Air Zoom...",
            ...     "meta_title": "Nike Air Zoom | MyShop"
            ... })
        """
        try:
            # 1. GET prodotto esistente
            product_resp = await self.get_product(product_id)
            if not product_resp.success:
                return product_resp

            # 2. Modifica XML con nuovi meta
            xml_str = self._build_product_update_xml(
                product_resp.data,
                meta_data,
                language_id
            )

            # 3. PUT update
            url = f"{self.api_base}/products/{product_id}"
            response = await self.client.put(url, content=xml_str)

            if response.status_code in [200, 201]:
                return APIResponse(
                    success=True,
                    data={'product_id': product_id, 'updated': meta_data}
                )
            else:
                return APIResponse(
                    success=False,
                    error=f"Update failed: {response.text[:200]}",
                    status_code=response.status_code
                )
        except Exception as e:
            return APIResponse(success=False, error=str(e))

    async def update_category_meta(
        self,
        category_id: int,
        meta_data: Dict[str, str],
        language_id: int = 1
    ) -> APIResponse:
        """Aggiorna meta SEO categoria"""
        try:
            url = f"{self.api_base}/categories/{category_id}"

            # GET current
            get_resp = await self.client.get(url)
            if get_resp.status_code != 200:
                return APIResponse(success=False, error="Categoria non trovata")

            # Build update XML
            root = ET.fromstring(get_resp.text)
            category_node = root.find('.//category')

            # Update meta fields
            for field, value in meta_data.items():
                field_node = category_node.find(f'.//{field}')
                if field_node is not None:
                    lang_node = field_node.find(f'.//language[@id="{language_id}"]')
                    if lang_node is not None:
                        lang_node.text = value

            xml_str = ET.tostring(root, encoding='unicode')

            # PUT update
            put_resp = await self.client.put(url, content=xml_str)

            if put_resp.status_code in [200, 201]:
                return APIResponse(success=True, data={'category_id': category_id})
            else:
                return APIResponse(success=False, error=put_resp.text[:200])

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    async def batch_update_fixes(
        self,
        fixes: List[Dict[str, Any]],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Applica multipli fix in batch

        Args:
            fixes: Lista fix da applicare. Ogni fix deve avere:
                - resource_type: "product" | "category" | "cms"
                - resource_id: ID risorsa
                - meta_data: Dict con meta da aggiornare
            dry_run: Se True, simula senza applicare

        Returns:
            Dict con statistiche: success_count, failed_count, errors

        Example:
            >>> fixes = [
            ...     {
            ...         "resource_type": "product",
            ...         "resource_id": 42,
            ...         "meta_data": {"meta_description": "..."}
            ...     },
            ...     ...
            ... ]
            >>> result = await client.batch_update_fixes(fixes)
            >>> print(f"Applicati {result['success_count']} fix")
        """
        results = {
            'total': len(fixes),
            'success_count': 0,
            'failed_count': 0,
            'errors': [],
            'dry_run': dry_run
        }

        for fix in fixes:
            if dry_run:
                # Simula solo
                results['success_count'] += 1
                continue

            try:
                resource_type = fix['resource_type']
                resource_id = fix['resource_id']
                meta_data = fix['meta_data']

                if resource_type == 'product':
                    resp = await self.update_product_meta(resource_id, meta_data)
                elif resource_type == 'category':
                    resp = await self.update_category_meta(resource_id, meta_data)
                else:
                    results['failed_count'] += 1
                    results['errors'].append(f"Tipo risorsa non supportato: {resource_type}")
                    continue

                if resp.success:
                    results['success_count'] += 1
                else:
                    results['failed_count'] += 1
                    results['errors'].append(f"{resource_type} {resource_id}: {resp.error}")

            except Exception as e:
                results['failed_count'] += 1
                results['errors'].append(f"Errore generico: {str(e)}")

        return results

    async def create_backup_snapshot(self) -> str:
        """
        Crea snapshot backup database

        NOTA: Richiede modulo PrestaShop custom o accesso DB diretto.
        Per ora ritorna timestamp come ID snapshot.

        Returns:
            ID snapshot (timestamp)
        """
        # TODO: Implementare backup reale quando disponibile modulo
        snapshot_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        return snapshot_id

    async def close(self):
        """Chiude client HTTP"""
        await self.client.aclose()

    # Helper methods

    def _xml_to_dict(self, element: ET.Element) -> Dict:
        """Converte XML Element a dict"""
        result = {}
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                result[child.tag] = self._xml_to_dict(child)
        return result

    def _build_product_update_xml(
        self,
        product_data: Dict,
        meta_updates: Dict[str, str],
        language_id: int
    ) -> str:
        """
        Costruisce XML per update prodotto

        NOTA: PrestaShop richiede XML completo con struttura specifica
        """
        # Simplified - in produzione usare template XML completo
        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<prestashop xmlns:xlink="http://www.w3.org/1999/xlink">
    <product>
        <meta_description>
            <language id="{language_id}"><![CDATA[{meta_updates.get('meta_description', '')}]]></language>
        </meta_description>
        <meta_title>
            <language id="{language_id}"><![CDATA[{meta_updates.get('meta_title', '')}]]></language>
        </meta_title>
        <meta_keywords>
            <language id="{language_id}"><![CDATA[{meta_updates.get('meta_keywords', '')}]]></language>
        </meta_keywords>
    </product>
</prestashop>
"""
        return xml_template


# Utility functions

async def test_prestashop_connection(shop_url: str, api_key: str) -> bool:
    """
    Test rapido connessione API PrestaShop

    Args:
        shop_url: URL shop
        api_key: Chiave webservice

    Returns:
        True se connessione OK
    """
    client = PrestaShopAPIClient(shop_url, api_key)
    try:
        result = await client.test_connection()
        return result.success
    finally:
        await client.close()
