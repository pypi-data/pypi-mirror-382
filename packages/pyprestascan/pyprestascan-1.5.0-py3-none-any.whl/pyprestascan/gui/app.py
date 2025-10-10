"""
Launcher per l'interfaccia grafica PyPrestaScan
"""
import sys
import os
from pathlib import Path

# Aggiungi il path del progetto per import
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

try:
    from pyprestascan.gui.main_window import main
except ImportError as e:
    print(f"❌ Errore import GUI: {e}")
    print("\n💡 Assicurati di aver installato PySide6:")
    print("pip install PySide6")
    sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())