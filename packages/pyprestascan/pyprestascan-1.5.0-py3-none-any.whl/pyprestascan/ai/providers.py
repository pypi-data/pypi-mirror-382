"""
Provider AI per generazione contenuti SEO ottimizzati
Supporta: DeepSeek, OpenAI GPT, Anthropic Claude
"""
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
import httpx
import asyncio
import json


@dataclass
class AIGeneratedContent:
    """Contenuto generato da AI"""
    meta_description: str
    confidence: float
    tokens_used: int
    provider: str


class AIProvider(ABC):
    """Classe base astratta per provider AI"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    @abstractmethod
    async def generate_meta_description(
        self,
        title: str,
        url: str,
        page_type: str,
        context: Optional[str] = None
    ) -> AIGeneratedContent:
        """Genera meta description ottimizzata"""
        pass

    @abstractmethod
    async def generate_batch(
        self,
        items: List[Dict[str, Any]]
    ) -> List[AIGeneratedContent]:
        """Genera contenuti in batch (più efficiente)"""
        pass

    async def close(self):
        """Chiude connessione HTTP"""
        await self.client.aclose()


class DeepSeekProvider(AIProvider):
    """Provider DeepSeek (economico: $0.14/1M input tokens)"""

    BASE_URL = "https://api.deepseek.com/v1/chat/completions"
    MODEL = "deepseek-chat"  # Modello più economico

    async def generate_meta_description(
        self,
        title: str,
        url: str,
        page_type: str,
        context: Optional[str] = None
    ) -> AIGeneratedContent:
        """Genera singola meta description"""

        # Prompt ottimizzato per ridurre token
        prompt = self._build_prompt(title, url, page_type, context)

        response = await self.client.post(
            self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Sei un esperto SEO. Genera meta description ottimizzate (120-160 caratteri) in italiano. Rispondi SOLO con il testo, senza spiegazioni."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,  # Bassa per risultati consistenti
                "max_tokens": 100   # Sufficiente per 160 caratteri
            }
        )

        response.raise_for_status()
        data = response.json()

        description = data['choices'][0]['message']['content'].strip()

        # Valida lunghezza
        if len(description) > 160:
            description = description[:157] + "..."

        return AIGeneratedContent(
            meta_description=description,
            confidence=0.95,  # Alta per AI
            tokens_used=data['usage']['total_tokens'],
            provider="deepseek"
        )

    async def generate_batch(
        self,
        items: List[Dict[str, Any]]
    ) -> List[AIGeneratedContent]:
        """Genera batch in UNA SOLA chiamata (risparmio enorme)"""

        # Costruisci prompt batch compatto
        batch_prompt = "Genera meta description SEO (120-160 char) per:\n\n"
        for i, item in enumerate(items, 1):
            batch_prompt += f"{i}. {item['title']} ({item['page_type']})\n"
        batch_prompt += "\nRispondi con SOLO le description, una per riga, numerate."

        response = await self.client.post(
            self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Esperto SEO italiano. Genera meta description ottimizzate."
                    },
                    {
                        "role": "user",
                        "content": batch_prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": len(items) * 50  # ~50 token per description
            }
        )

        response.raise_for_status()
        data = response.json()

        # Parsing output
        descriptions = data['choices'][0]['message']['content'].strip().split('\n')
        tokens_per_item = data['usage']['total_tokens'] // len(items)

        results = []
        for desc in descriptions[:len(items)]:
            # Rimuovi numerazione
            clean_desc = desc.split('. ', 1)[-1].strip()

            results.append(AIGeneratedContent(
                meta_description=clean_desc[:160],
                confidence=0.95,
                tokens_used=tokens_per_item,
                provider="deepseek"
            ))

        return results

    def _build_prompt(self, title: str, url: str, page_type: str, context: Optional[str]) -> str:
        """Prompt compatto per singola description"""
        prompt = f"Title: {title}\nTipo: {page_type}\n"
        if context:
            prompt += f"Context: {context[:100]}\n"  # Max 100 char
        return prompt


class OpenAIProvider(AIProvider):
    """Provider OpenAI GPT (medio: $0.15-$0.60/1M input tokens)"""

    BASE_URL = "https://api.openai.com/v1/chat/completions"
    MODEL = "gpt-4o-mini"  # Modello più economico

    async def generate_meta_description(
        self,
        title: str,
        url: str,
        page_type: str,
        context: Optional[str] = None
    ) -> AIGeneratedContent:
        """Genera meta description con GPT-4o-mini"""

        prompt = f"Meta description SEO (120-160 char) per: {title} ({page_type})"

        response = await self.client.post(
            self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "SEO expert. Generate optimized Italian meta descriptions. Reply with ONLY the text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 100
            }
        )

        response.raise_for_status()
        data = response.json()

        description = data['choices'][0]['message']['content'].strip()

        return AIGeneratedContent(
            meta_description=description[:160],
            confidence=0.97,
            tokens_used=data['usage']['total_tokens'],
            provider="openai"
        )

    async def generate_batch(self, items: List[Dict[str, Any]]) -> List[AIGeneratedContent]:
        """Batch processing con GPT"""
        # Stesso approccio di DeepSeek
        batch_prompt = "Meta descriptions (120-160 char):\n"
        for i, item in enumerate(items, 1):
            batch_prompt += f"{i}. {item['title']}\n"

        response = await self.client.post(
            self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.MODEL,
                "messages": [
                    {"role": "system", "content": "SEO expert generating Italian meta descriptions."},
                    {"role": "user", "content": batch_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": len(items) * 50
            }
        )

        response.raise_for_status()
        data = response.json()

        descriptions = data['choices'][0]['message']['content'].strip().split('\n')
        tokens_per_item = data['usage']['total_tokens'] // len(items)

        return [
            AIGeneratedContent(
                meta_description=desc.split('. ', 1)[-1].strip()[:160],
                confidence=0.97,
                tokens_used=tokens_per_item,
                provider="openai"
            )
            for desc in descriptions[:len(items)]
        ]


class ClaudeProvider(AIProvider):
    """Provider Anthropic Claude (costoso: $3/1M input tokens)"""

    BASE_URL = "https://api.anthropic.com/v1/messages"
    MODEL = "claude-3-5-haiku-20241022"  # Haiku più economico

    async def generate_meta_description(
        self,
        title: str,
        url: str,
        page_type: str,
        context: Optional[str] = None
    ) -> AIGeneratedContent:
        """Genera con Claude Haiku"""

        prompt = f"Meta description SEO (120-160 char) per prodotto PrestaShop: {title}"

        response = await self.client.post(
            self.BASE_URL,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": self.MODEL,
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "system": "SEO expert. Generate ONLY the meta description text in Italian, no explanations."
            }
        )

        response.raise_for_status()
        data = response.json()

        description = data['content'][0]['text'].strip()

        # Claude usage tracking
        tokens_used = data['usage']['input_tokens'] + data['usage']['output_tokens']

        return AIGeneratedContent(
            meta_description=description[:160],
            confidence=0.98,
            tokens_used=tokens_used,
            provider="claude"
        )

    async def generate_batch(self, items: List[Dict[str, Any]]) -> List[AIGeneratedContent]:
        """Batch con Claude"""
        batch_prompt = f"Generate {len(items)} Italian meta descriptions (120-160 char), one per line:\n\n"
        for i, item in enumerate(items, 1):
            batch_prompt += f"{i}. {item['title']}\n"

        response = await self.client.post(
            self.BASE_URL,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": self.MODEL,
                "max_tokens": len(items) * 50,
                "messages": [{"role": "user", "content": batch_prompt}],
                "system": "SEO expert. Reply with ONLY meta descriptions, numbered."
            }
        )

        response.raise_for_status()
        data = response.json()

        descriptions = data['content'][0]['text'].strip().split('\n')
        tokens_used = data['usage']['input_tokens'] + data['usage']['output_tokens']
        tokens_per_item = tokens_used // len(items)

        return [
            AIGeneratedContent(
                meta_description=desc.split('. ', 1)[-1].strip()[:160],
                confidence=0.98,
                tokens_used=tokens_per_item,
                provider="claude"
            )
            for desc in descriptions[:len(items)]
        ]


class AIProviderFactory:
    """Factory per creare provider AI"""

    @staticmethod
    def create(provider_name: str, api_key: str) -> AIProvider:
        """Crea provider basato sul nome"""
        providers = {
            'deepseek': DeepSeekProvider,
            'openai': OpenAIProvider,
            'claude': ClaudeProvider
        }

        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Provider non supportato: {provider_name}")

        return provider_class(api_key)

    @staticmethod
    def get_available_providers() -> List[Dict[str, Any]]:
        """Lista provider disponibili con info costi"""
        return [
            {
                'id': 'deepseek',
                'name': 'DeepSeek',
                'model': 'deepseek-chat',
                'cost_per_1m': '$0.14',
                'recommended': True,
                'description': 'Più economico, qualità eccellente'
            },
            {
                'id': 'openai',
                'name': 'OpenAI GPT-4o-mini',
                'model': 'gpt-4o-mini',
                'cost_per_1m': '$0.15',
                'recommended': True,
                'description': 'Ottimo rapporto qualità/prezzo'
            },
            {
                'id': 'claude',
                'name': 'Anthropic Claude Haiku',
                'model': 'claude-3-5-haiku-20241022',
                'cost_per_1m': '$0.80',
                'recommended': False,
                'description': 'Qualità massima, più costoso'
            }
        ]


# Utility per stimare costi
class CostEstimator:
    """Stima costi operazione AI"""

    COSTS = {
        'deepseek': 0.14 / 1_000_000,   # $0.14 per 1M token
        'openai': 0.15 / 1_000_000,      # $0.15 per 1M token
        'claude': 0.80 / 1_000_000       # $0.80 per 1M token (Haiku input)
    }

    @staticmethod
    def estimate_cost(provider: str, num_items: int, avg_tokens_per_item: int = 150) -> Dict[str, Any]:
        """Stima costo operazione"""
        total_tokens = num_items * avg_tokens_per_item
        cost_per_token = CostEstimator.COSTS.get(provider.lower(), 0)
        total_cost = total_tokens * cost_per_token

        return {
            'provider': provider,
            'num_items': num_items,
            'estimated_tokens': total_tokens,
            'estimated_cost_usd': round(total_cost, 4),
            'estimated_cost_eur': round(total_cost * 0.92, 4),  # Approssimativo
            'cost_per_item': round(total_cost / num_items, 6)
        }
