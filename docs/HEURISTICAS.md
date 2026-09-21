# Heurísticas e busca informada (A*)

Este documento explica **quais heurísticas o Arena Bot usa**, **por que foram escolhidas** e **onde estão no código**. Serve para colegas entenderem a Unidade 3A (busca heurística) do PP01.

## 1. Formulação do problema de navegação

| Elemento | Definição neste projeto |
|----------|-------------------------|
| **Estados** | Células livres `(x, y)` (sem parede) |
| **Estado inicial** | Posição atual do robô |
| **Ações** | Mover para vizinho ortogonal (cima, baixo, esquerda, direita) — **vizinhança-4** |
| **Teste de objetivo** | Célula atual = alvo (minério ou base) |
| **Custo de aresta** `c(n, n')` | `2` se `n'` é armadilha; `1` caso contrário |

Importante: esse custo de **aresta** (grafo de busca) é diferente do gasto de **bateria** no jogo (−2 passo normal, −4 armadilha por padrão). O A* usa o custo de aresta para preferir contornar armadilhas.

## 2. Função de avaliação do A*

\[
f(n) = g(n) + h(n)
\]

- `g(n)`: custo acumulado do caminho desde a origem até `n`
- `h(n)`: estimativa do custo restante até o objetivo (**heurística**)

Implementação: [`ia/navegacao.py`](../ia/navegacao.py) (`buscar_caminho`), com fila de prioridade (`heapq`).

## 3. Heurística oficial: distância de Manhattan

\[
h(n) = |x_n - x_g| + |y_n - y_g|
\]

Código: [`ia/heuristicas.py`](../ia/heuristicas.py) → função `manhattan`.

### Por que Manhattan?

1. **Movimento em vizinhança-4**: o robô não anda na diagonal. A distância Manhattan conta exatamente o número mínimo de passos ortogonais em grade vazia.
2. **Admissível**: nunca superestima o custo ótimo. Como o custo mínimo de uma aresta é `1`, temos \(h(n) \le h^*(n)\).
3. **Consistente (monótona)**: para todo sucessor \(n'\) de \(n\),
   \[
   |h(n) - h(n')| \le 1 \le c(n, n')
   \]
   Isso garante que a primeira vez que o A* expande o objetivo, o caminho é ótimo (no modelo de custo do grafo).

### Por que não usar só “número de passos sem custo”?

Se ignorássemos o custo 2 das armadilhas, o agente atravessaria armadilhas demais. Com `c = 2` em armadilha, o A* **desvia** quando vale a pena — comportamento exigido pelo enunciado.

## 4. Heurística de comparação: Euclidiana

\[
h_e(n) = \sqrt{(x_n - x_g)^2 + (y_n - y_g)^2}
\]

Código: `euclidiana` no mesmo módulo.

### Por que existe, mas não é o padrão do jogo?

- Também é **admissível** sob custo mínimo 1 (linha reta ≤ qualquer caminho).
- Em grade **só com movimentos ortogonais**, a linha reta **subestima mais** (pensa em atalho diagonal que o robô não pode usar).
- Logo Manhattan é **mais informativa**: guia melhor a ordem de expansão e tende a expandir menos nós.

No relatório / experimentos (fase 2), compare nós expandidos A*+Manhattan vs A*+Euclidiana vs BFS.

## 5. Injeção da heurística (como reutilizar / experimentar)

```python
from ia.heuristicas import manhattan, euclidiana
from ia.navegacao import buscar_caminho

# Padrão do jogo
r1 = buscar_caminho(arena, origem, destino)  # usa manhattan

# Experimento
r2 = buscar_caminho(arena, origem, destino, heuristica=euclidiana)
```

A assinatura `buscar_caminho(..., heuristica=manhattan)` permite trocar `h` sem reescrever o A*.

## 6. Baseline sem heurística: BFS

Arquivo: [`ia/busca_baseline.py`](../ia/busca_baseline.py).

- Expande em largura, **sem** `h(n)`.
- Serve para mostrar o **ganho da busca informada**: em geral o A* expande menos nós que o BFS no mesmo mapa.

## 7. Uso da mesma ideia no Minimax

Em [`ia/estrategia.py`](../ia/estrategia.py):

- A função de avaliação usa vantagem de distância estimada com **Manhattan** entre robô, inimigo e minério.
- Nos nós profundos da árvore, distâncias usam Manhattan; nos rasos, pode usar A* real (otimização de custo de busca).

Isso não substitui o A* de navegação: Minimax escolhe **qual alvo**; A* calcula **como chegar**.

## 8. Resumo para a defesa / colegas

| Pergunta | Resposta curta |
|----------|----------------|
| Qual heurística no jogo? | Manhattan |
| Por quê? | Grade 4-vizinhos; admissível e consistente; mais informativa que Euclidiana |
| Onde está? | `ia/heuristicas.py` + `ia/navegacao.py` |
| Como provar admissibilidade? | Custo mínimo de passo = 1 ⇒ \(h \le h^*\) |
| Como comparar? | Contar `nos_expandidos` do A* vs BFS / Euclidiana |

## 9. Referências conceituais

- Russell & Norvig, *Artificial Intelligence: A Modern Approach* — capítulos de busca informada (A*) e propriedades de heurísticas.
- Enunciado PP01 (RUS0086) — Unidade 3A: navegação com A* e Manhattan.
