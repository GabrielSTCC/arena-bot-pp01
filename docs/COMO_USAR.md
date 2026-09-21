# Como usar (instalação e execução)

## Requisitos

- Python **3.10+**
- Sistema com suporte a janela gráfica (Pygame / SDL)

## Instalação

```bash
git clone https://github.com/GabrielSTCC/arena-bot-pp01.git
cd arena-bot-pp01

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Executar

```bash
python main.py
```

## Controles

| Tecla / UI | Ação |
|------------|------|
| **Jogar** | Inicia torneio (N rounds conforme Opções) |
| **Opções** | Ajusta parâmetros da arena/torneio |
| **Regras** | Resumo das regras |
| **P** | Pausar / continuar |
| **R** | Reiniciar o round atual |
| **ESC** | Voltar ao menu (ou sair do modo maximizado) |
| **F11** | Maximizar / restaurar |
| Barra superior **─ □ ×** | Minimizar, maximizar, fechar |

## Tela de Opções

Valores padrão = enunciado do PP01. Só mudam se você alterar.

| Parâmetro | Padrão | O que faz |
|-----------|--------|-----------|
| Rounds do torneio | 1 | Quantas partidas seguidas (placar acumulado) |
| Paredes | 25 | Obstáculos intransponíveis |
| Armadilhas | 6 | Células com custo extra de bateria |
| Dano da armadilha | 4 | Bateria gasta ao pisar na armadilha |

Use **Restaurar padrões** para voltar aos defaults.

## Para quem for estudar / implementar

1. Leia [HEURISTICAS.md](HEURISTICAS.md) — Manhattan, A*, por quê.
2. Leia [ARQUITETURA.md](ARQUITETURA.md) — ciclo de turno e módulos.
3. Comece pelo código em `ia/heuristicas.py` → `ia/navegacao.py` → `ia/estrategia.py` → `ia/conhecimento.py`.
4. O loop de integração está em `core/partida.py` (`executar_turno`).

## Problemas comuns

- **Pygame não abre janela (SSH/headless):** precisa de display local (Wayland/X11) ou variável `DISPLAY`.
- **Dependências:** confira `pip install -r requirements.txt` dentro do venv.
- **Não copie o jogo de referência do professor:** este repositório é a solução **autoral**; use-o como estudo, não como cópia para entregar no lugar do seu código.
