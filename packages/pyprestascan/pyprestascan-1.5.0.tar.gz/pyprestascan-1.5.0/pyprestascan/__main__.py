"""
Entry point per PyPrestaScan CLI
"""
import sys
import asyncio
from typing import Optional

from pyprestascan.cli import main as cli_main


def main() -> Optional[int]:
    """Entry point principale"""
    try:
        # Su Windows, imposta policy per event loop
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Esegui CLI
        return cli_main()
    
    except KeyboardInterrupt:
        print("\n🛑 Operazione annullata dall'utente")
        return 1
    except Exception as e:
        print(f"❌ Errore inaspettato: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main() or 0)