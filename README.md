# Arena Bot — PP01 (RUS0086 · Inteligência Artificial)

Solução **autoral** do Projeto Prático 01 da UFC Russas: dois robôs (**Alfa** e **Beta**) competem coletando minérios em uma grade 15×9, integrando:

| Técnica | Papel no jogo |
|---------|----------------|
| **A\*** + heurística **Manhattan** | Calcular rotas evitando paredes e armadilhas |
| **Minimax** recursivo com poda **α-β** (`d ≥ 4`) | Escolher qual minério perseguir |
| **Base de conhecimento** proposicional | Autorizar coleta / forçar descarga |

Código e organização distintos do jogo de referência do professor (não reutiliza assets nem estrutura daquele projeto).

---

## Começar em 1 minuto

```bash
git clone https://github.com/GabrielSTCC/arena-bot-pp01.git
cd arena-bot-pp01
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Guia completo: **[docs/COMO_USAR.md](docs/COMO_USAR.md)**

---

## Documentação (leia isto)

| Documento | Conteúdo |
|-----------|----------|
| **[docs/HEURISTICAS.md](docs/HEURISTICAS.md)** | Manhattan vs Euclidiana, por que no A*, admissibilidade, como experimentar |
| **[docs/ARQUITETURA.md](docs/ARQUITETURA.md)** | Ciclo de turno, módulos, Minimax e BC |
| **[docs/COMO_USAR.md](docs/COMO_USAR.md)** | Instalação, controles, tela de Opções |

---

## Controles rápidos

| UI / tecla | Ação |
|------------|------|
| Jogar | Inicia torneio |
| Opções | Rounds, paredes, armadilhas, dano de bateria |
| P / R / ESC / F11 | Pausar, reiniciar round, menu, maximizar |
| ─ □ × | Minimizar, maximizar, fechar |

Padrões (sem mexer em Opções): 1 round, 25 paredes, 6 armadilhas, −4 bateria na armadilha.

---

## Estrutura do repositório

```
.
├── main.py                 # Entrada
├── config.py               # Constantes do enunciado
├── requirements.txt
├── core/                   # Arena, agente, partida, config da UI
├── ia/
│   ├── heuristicas.py      # Manhattan (oficial) e Euclidiana
│   ├── navegacao.py        # A*  f = g + h
│   ├── busca_baseline.py   # BFS (sem heurística)
│   ├── estrategia.py       # Minimax + α-β
│   └── conhecimento.py     # BC + encadeamento para frente
├── ui/                     # Pygame
├── assets/                 # Sprites autorais (fallback geométrico se faltar)
└── docs/                   # Documentação para colegas / estudo
```

---

## Para quem for implementar / estudar

1. Entenda a busca: [HEURISTICAS.md](docs/HEURISTICAS.md).
2. Veja o fluxo: [ARQUITETURA.md](docs/ARQUITETURA.md).
3. Código sugerido na ordem: `heuristicas` → `navegacao` → `estrategia` → `conhecimento` → `partida`.

### Como a heurística entra no A* (exemplo)

```python
from ia.heuristicas import manhattan
from ia.navegacao import buscar_caminho

resultado = buscar_caminho(arena, origem, destino, heuristica=manhattan)
# resultado.caminho, resultado.custo, resultado.nos_expandidos
```

Detalhes e prova informal de admissibilidade estão em **docs/HEURISTICAS.md**.

---

## Originalidade (importante para a disciplina)

- Este repositório é **estudo / referência da equipe**.
- **Não** entregue cópia do código do professor nem deste repo sem compreender e adaptar às regras de originalidade da disciplina.
- O enunciado exige solução com os **mesmos modelos** (A*, Minimax α-β, BC), mas **código próprio**.

---

## Declaração de uso de IA

Partes do esqueleto e da documentação podem ter sido elaboradas com apoio de assistentes de IA; a lógica de A*, Minimax/α-β e BC foi alinhada ao enunciado do PP01 e deve ser compreendida na defesa.

---

## Licença de assets

Sprites em `assets/` (quando presentes) e renderização geométrica são autorais. Não há reutilização de `.png`/fontes do projeto de referência do professor.
