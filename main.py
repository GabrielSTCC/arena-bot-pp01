"""
Ponto de entrada do Arena Bot (PP01 — Inteligência Artificial).

Execução:
    python main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Garante import dos pacotes locais ao executar diretamente.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui.pygame_app import Aplicacao


def main() -> None:
    """Inicia a interface gráfica do Arena Bot."""
    app = Aplicacao()
    app.executar()


if __name__ == "__main__":
    main()
