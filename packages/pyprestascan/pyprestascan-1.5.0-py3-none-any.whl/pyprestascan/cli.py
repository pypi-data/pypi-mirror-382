"""
CLI module per PyPrestaScan
"""
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

import click
from pydantic import BaseModel, HttpUrl, Field, validator


class CrawlConfig(BaseModel):
    """Configurazione per il crawling"""
    url: HttpUrl
    max_urls: int = Field(default=10000, ge=1)
    concurrency: int = Field(default=20, ge=1, le=100)
    delay: int = Field(default=0, ge=0)  # ms
    timeout: int = Field(default=15, ge=1)  # seconds
    sitemap: str = Field(default="auto", pattern="^(auto|true|false)$")
    include_subdomains: bool = False
    include_patterns: List[str] = Field(default_factory=list)
    exclude_patterns: List[str] = Field(default_factory=list)
    user_agent: str = "PyPrestaScan/1.0 (+https://github.com/pyprestascan/pyprestascan)"
    auth_user: Optional[str] = None
    auth_pass: Optional[str] = None
    resume: bool = False
    project: str = "default"
    export_dir: Path = Field(default_factory=lambda: Path("./report"))
    include_generic: bool = False
    lang_map: Dict[str, str] = Field(default_factory=dict)
    prestashop_mode: bool = True
    depth: Optional[int] = Field(default=None, ge=1)

    @validator('include_patterns', 'exclude_patterns')
    def validate_regex_patterns(cls, v):
        """Valida che i pattern regex siano validi"""
        for pattern in v:
            try:
                re.compile(pattern)
            except re.error as e:
                raise ValueError(f"Pattern regex non valido '{pattern}': {e}")
        return v

    @validator('lang_map', pre=True)
    def parse_lang_map(cls, v):
        """Parse lang_map da stringa tipo 'it=it,en=en' a dict"""
        if isinstance(v, str):
            lang_dict = {}
            if v.strip():
                for pair in v.split(','):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        lang_dict[key.strip()] = value.strip()
            return lang_dict
        return v

    class Config:
        validate_assignment = True


@dataclass
class CliContext:
    """Contesto globale CLI"""
    config: CrawlConfig
    debug: bool = False
    quiet: bool = False
    no_color: bool = False


def parse_lang_map(ctx, param, value):
    """Callback per parsing lang_map"""
    if not value:
        return {}
    
    lang_dict = {}
    for pair in value.split(','):
        if '=' in pair:
            key, val = pair.split('=', 1)
            lang_dict[key.strip()] = val.strip()
        else:
            raise click.BadParameter(f"Formato lang-map non valido: {pair}. Usa formato 'key=value,key2=value2'")
    
    return lang_dict


@click.command()
@click.option('--url', required=True, help='URL base del sito da analizzare')
@click.option('--max-urls', default=10000, type=click.IntRange(1), 
              help='Numero massimo di URL da crawlare (default: 10000)')
@click.option('--concurrency', default=20, type=click.IntRange(1, 100),
              help='Numero di richieste concurrent (default: 20)')
@click.option('--delay', default=0, type=click.IntRange(0),
              help='Delay minimo tra richieste in ms (default: 0)')
@click.option('--timeout', default=15, type=click.IntRange(1),
              help='Timeout per richieste HTTP in secondi (default: 15)')
@click.option('--sitemap', default='auto', type=click.Choice(['auto', 'true', 'false']),
              help='Utilizzo sitemap.xml (default: auto)')
@click.option('--include-subdomains', is_flag=True,
              help='Include sottodomini del dominio principale')
@click.option('--include', 'include_patterns', multiple=True,
              help='Pattern regex per includere URL (ripetibile)')
@click.option('--exclude', 'exclude_patterns', multiple=True,
              help='Pattern regex per escludere URL (ripetibili)')
@click.option('--user-agent', 
              default='PyPrestaScan/1.0 (+https://github.com/pyprestascan/pyprestascan)',
              help='User-Agent personalizzato')
@click.option('--auth-user', help='Username per autenticazione basic')
@click.option('--auth-pass', help='Password per autenticazione basic')
@click.option('--resume', is_flag=True, help='Riprende progetto esistente da database')
@click.option('--project', default='default', help='Nome progetto (cartella .pyprestascan/<nome>)')
@click.option('--export-dir', default='./report', type=click.Path(),
              help='Directory per export report (default: ./report)')
@click.option('--include-generic', is_flag=True,
              help='Include ALT generici nel report immagini')
@click.option('--lang-map', callback=parse_lang_map, default='',
              help='Mappatura lingue formato "it=it,en=en"')
@click.option('--prestashop-mode/--no-prestashop-mode', default=True,
              help='Abilita/disabilita euristiche specifiche PrestaShop (default: abilitato)')
@click.option('--depth', type=click.IntRange(1),
              help='Profondità massima crawling (opzionale)')
@click.option('--debug', is_flag=True, help='Abilita output debug')
@click.option('--quiet', is_flag=True, help='Output minimo')
@click.option('--no-color', is_flag=True, help='Disabilita output colorato')
@click.pass_context
def main(ctx, **kwargs):
    """
    PyPrestaScan - CLI per analisi SEO specializzata di e-commerce PrestaShop
    
    Analizza siti PrestaShop (1.6, 1.7, 8, 9) con crawling asincrono scalabile,
    rispettando robots.txt e fornendo report dettagliati CSV/JSON/HTML.
    
    Esempi:
    
    \b
    # Scansione base
    pyprestascan --url https://shop.example.com
    
    \b  
    # Con configurazioni personalizzate
    pyprestascan --url https://shop.example.com --max-urls 50000 --concurrency 30 --delay 100
    
    \b
    # Con filtri
    pyprestascan --url https://shop.example.com --include "/category/" --exclude "\\?.*sort="
    
    \b
    # Riprendi scansione esistente
    pyprestascan --resume --project myshop
    """
    
    # Estrai parametri CLI
    cli_params = {k: v for k, v in kwargs.items() 
                  if k not in ['debug', 'quiet', 'no_color']}
    
    # Converti export_dir a Path
    cli_params['export_dir'] = Path(cli_params['export_dir'])
    
    # Converti liste a list
    cli_params['include_patterns'] = list(cli_params['include_patterns'])
    cli_params['exclude_patterns'] = list(cli_params['exclude_patterns'])
    
    try:
        # Crea config validandolo con Pydantic
        config = CrawlConfig(**cli_params)
        
        # Crea contesto
        cli_context = CliContext(
            config=config,
            debug=kwargs['debug'],
            quiet=kwargs['quiet'],
            no_color=kwargs['no_color']
        )
        
        # Imposta contesto Click
        ctx.obj = cli_context
        
        # Import ritardato per evitare dipendenze circolari
        from pyprestascan.core.crawler import PyPrestaScanner
        import asyncio

        # Avvia scanner
        scanner = PyPrestaScanner(config, cli_context)
        return asyncio.run(scanner.run())
        
    except Exception as e:
        if kwargs['debug']:
            raise
        click.echo(f"❌ Errore: {e}", err=True)
        ctx.exit(1)


if __name__ == '__main__':
    main()