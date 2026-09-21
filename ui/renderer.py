"""
Renderização da arena com sprites autorais (fallback geométrico se faltar PNG).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pygame

import config
from core.agente import Agente
from core.arena import Arena
from core.config_partida import ConfigPartida
from core.partida import Partida, ResultadoPartida

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class Renderer:
    """Desenha grade, HUD, menus e opções; usa sprites de ``assets/`` quando houver.

    Attributes:
        superficie: Surface principal do Pygame.
        fonte: Fonte padrão.
        fonte_titulo: Fonte de títulos.
        fonte_hud: Fonte compacta do HUD.
        sprites: Mapa nome → Surface escalada (vazio se o arquivo não existir).
    """

    def __init__(self, superficie: pygame.Surface) -> None:
        """Inicializa fontes, sprites e referência à superfície.

        Args:
            superficie: Janela do jogo.
        """
        self.superficie = superficie
        pygame.font.init()
        self.fonte = pygame.font.SysFont("DejaVu Sans", 18)
        self.fonte_titulo = pygame.font.SysFont("DejaVu Sans", 40, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("DejaVu Sans", 20)
        self.fonte_hud = pygame.font.SysFont("DejaVu Sans", 15)
        self.fonte_pequena = pygame.font.SysFont("DejaVu Sans", 13)
        self.fonte_janela = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
        self.sprites = self._carregar_sprites()

    def atualizar_superficie(self, superficie: pygame.Surface) -> None:
        """Atualiza a surface após redimensionar / maximizar a janela.

        Args:
            superficie: Nova surface do display.
        """
        self.superficie = superficie

    def _carregar_sprites(self) -> dict[str, pygame.Surface]:
        """Carrega PNGs de ``assets/`` escalados para ``TAMANHO_CELULA``.

        Returns:
            Dicionário só com arquivos encontrados (chave = nome sem extensão
            para tiles/robôs; minerais usam o tipo: diamante, rubi, …).
        """
        nomes = (
            "robo_alfa",
            "robo_beta",
            "tile_wall",
            "tile_blocked",
            "diamante",
            "rubi",
            "ouro",
            "prata",
            "bronze",
        )
        t = config.TAMANHO_CELULA
        carregados: dict[str, pygame.Surface] = {}
        for nome in nomes:
            caminho = _ASSETS_DIR / f"{nome}.png"
            if not caminho.is_file():
                continue
            try:
                img = pygame.image.load(str(caminho)).convert_alpha()
                if img.get_size() != (t, t):
                    img = pygame.transform.smoothscale(img, (t, t))
                carregados[nome] = img
            except pygame.error:
                continue
        return carregados

    def desenhar_controles_janela(
        self, mouse_pos: tuple[int, int], maximizado: bool = False
    ) -> dict[str, pygame.Rect]:
        """Barra superior com Minimizar, Maximizar/Restaurar e Fechar.

        Ícones desenhados com primitivas (não dependem de glifos Unicode).

        Args:
            mouse_pos: Posição do cursor para hover.
            maximizado: Se True, o botão do meio mostra restaurar.

        Returns:
            Mapa ``win_minimizar`` / ``win_maximizar`` / ``win_fechar`` → Rect.
        """
        w = self.superficie.get_size()[0]
        barra_h = config.ALTURA_BARRA_JANELA
        pygame.draw.rect(
            self.superficie,
            (18, 26, 36),
            pygame.Rect(0, 0, w, barra_h),
        )
        pygame.draw.line(
            self.superficie,
            config.COR_GRADE,
            (0, barra_h - 1),
            (w, barra_h - 1),
            1,
        )

        titulo = self.fonte_pequena.render("Arena Bot", True, config.COR_TEXTO_SUAVE)
        self.superficie.blit(titulo, (12, (barra_h - titulo.get_height()) // 2))

        tamanho = 26
        gap = 6
        y = (barra_h - tamanho) // 2
        x_fechar = w - tamanho - 8
        x_max = x_fechar - tamanho - gap
        x_min = x_max - tamanho - gap

        defs = (
            ("win_minimizar", x_min, config.COR_BTN_MIN),
            ("win_maximizar", x_max, config.COR_BTN_MAX),
            ("win_fechar", x_fechar, config.COR_BTN_FECHAR),
        )
        botoes: dict[str, pygame.Rect] = {}
        for nome, x, cor_base in defs:
            rect = pygame.Rect(x, y, tamanho, tamanho)
            hover = rect.collidepoint(mouse_pos)
            cor = tuple(min(255, c + 40) for c in cor_base) if hover else cor_base
            pygame.draw.rect(self.superficie, cor, rect, border_radius=6)
            if hover:
                pygame.draw.rect(
                    self.superficie, config.COR_BTN_JANELA_HOVER, rect, 1, border_radius=6
                )
            self._desenhar_icone_janela(nome, rect, maximizado)
            botoes[nome] = rect
        return botoes

    def _desenhar_icone_janela(
        self, nome: str, rect: pygame.Rect, maximizado: bool
    ) -> None:
        """Desenha o ícone interno do botão de janela.

        Args:
            nome: Identificador do botão.
            rect: Área do botão.
            maximizado: Estado atual da janela (para ícone restaurar).
        """
        cor = config.COR_TEXTO
        cx, cy = rect.centerx, rect.centery
        if nome == "win_minimizar":
            # Traço horizontal (minimizar)
            pygame.draw.line(
                self.superficie, cor, (cx - 6, cy), (cx + 6, cy), 2
            )
        elif nome == "win_maximizar":
            if maximizado:
                # Dois quadrados sobrepostos (restaurar)
                pygame.draw.rect(
                    self.superficie, cor, pygame.Rect(cx - 3, cy - 6, 9, 9), 2
                )
                pygame.draw.rect(
                    self.superficie, cor, pygame.Rect(cx - 7, cy - 2, 9, 9), 2
                )
            else:
                # Quadrado (maximizar)
                pygame.draw.rect(
                    self.superficie, cor, pygame.Rect(cx - 6, cy - 6, 12, 12), 2
                )
        elif nome == "win_fechar":
            # X (fechar)
            pygame.draw.line(
                self.superficie, cor, (cx - 5, cy - 5), (cx + 5, cy + 5), 2
            )
            pygame.draw.line(
                self.superficie, cor, (cx + 5, cy - 5), (cx - 5, cy + 5), 2
            )

    @property
    def offset_y(self) -> int:
        """Deslocamento vertical da grade (barra da janela + HUD)."""
        return config.ALTURA_BARRA_JANELA + config.ALTURA_HUD

    def celula_para_pixel(self, celula: tuple[int, int]) -> tuple[int, int]:
        """Converte coordenada da grade para canto superior esquerdo em pixels.

        Args:
            celula: (x, y) da grade.

        Returns:
            Posição em pixels.
        """
        x, y = celula
        return x * config.TAMANHO_CELULA, self.offset_y + y * config.TAMANHO_CELULA

    def _preencher_gradiente(self) -> None:
        """Fundo com gradiente vertical suave."""
        w, h = self.superficie.get_size()
        for y in range(h):
            t = y / max(1, h - 1)
            r = int(
                config.COR_FUNDO_TOPO[0] * (1 - t) + config.COR_FUNDO[0] * t
            )
            g = int(
                config.COR_FUNDO_TOPO[1] * (1 - t) + config.COR_FUNDO[1] * t
            )
            b = int(
                config.COR_FUNDO_TOPO[2] * (1 - t) + config.COR_FUNDO[2] * t
            )
            pygame.draw.line(self.superficie, (r, g, b), (0, y), (w, y))

    def _desenhar_parede_geometrica(self, px: int, py: int, t: int) -> None:
        """Fallback de parede sem sprite."""
        rect = pygame.Rect(px, py, t, t)
        pygame.draw.rect(self.superficie, config.COR_PAREDE, rect)
        pygame.draw.line(
            self.superficie, config.COR_PAREDE_LUZ, (px, py), (px + t - 1, py), 2
        )
        pygame.draw.line(
            self.superficie, config.COR_PAREDE_LUZ, (px, py), (px, py + t - 1), 2
        )
        pygame.draw.line(
            self.superficie,
            config.COR_PAREDE_SOMBRA,
            (px, py + t - 1),
            (px + t - 1, py + t - 1),
            2,
        )

    def _desenhar_armadilha_geometrica(self, rect: pygame.Rect) -> None:
        """Fallback de armadilha sem sprite."""
        trap = rect.inflate(-12, -12)
        pygame.draw.rect(
            self.superficie, config.COR_ARMADILHA, trap, border_radius=5
        )
        pygame.draw.line(
            self.superficie,
            (255, 210, 90),
            (trap.left + 4, trap.top + 4),
            (trap.right - 4, trap.bottom - 4),
            2,
        )
        pygame.draw.line(
            self.superficie,
            (255, 210, 90),
            (trap.right - 4, trap.top + 4),
            (trap.left + 4, trap.bottom - 4),
            2,
        )

    def _desenhar_minerio_geometrico(
        self, px: int, py: int, t: int, tipo: str
    ) -> None:
        """Fallback de minério sem sprite."""
        cor = config.CORES_MINERIO.get(tipo, (255, 255, 255))
        centro = (px + t // 2, py + t // 2)
        pygame.draw.circle(self.superficie, (20, 24, 30), centro, t // 3 + 1)
        pygame.draw.circle(self.superficie, cor, centro, t // 3)
        pygame.draw.circle(self.superficie, (255, 255, 255), centro, t // 3, 1)
        pygame.draw.circle(
            self.superficie, (255, 255, 255), (centro[0] - 3, centro[1] - 4), 2
        )

    def _chave_sprite_robo(self, agente: Agente) -> str:
        """Nome do arquivo de robô para o agente (alfa/beta)."""
        nome = agente.nome.strip().lower()
        if "beta" in nome:
            return "robo_beta"
        return "robo_alfa"

    def desenhar_arena(self, arena: Arena, agentes: list[Agente]) -> None:
        """Desenha chão, paredes, armadilhas, minérios e robôs.

        Args:
            arena: Ambiente corrente.
            agentes: Lista de agentes a plotar.
        """
        self.superficie.fill(config.COR_FUNDO)
        t = config.TAMANHO_CELULA
        spr_parede = self.sprites.get("tile_wall")
        spr_armadilha = self.sprites.get("tile_blocked")

        for y in range(arena.altura):
            for x in range(arena.largura):
                px, py = self.celula_para_pixel((x, y))
                rect = pygame.Rect(px, py, t, t)
                if (x, y) in arena.paredes:
                    if spr_parede is not None:
                        self.superficie.blit(spr_parede, (px, py))
                    else:
                        self._desenhar_parede_geometrica(px, py, t)
                else:
                    chao = (
                        config.COR_CHAO_ALT
                        if (x + y) % 2 == 0
                        else config.COR_CHAO
                    )
                    pygame.draw.rect(self.superficie, chao, rect)
                    pygame.draw.rect(self.superficie, config.COR_GRADE, rect, 1)
                    if (x, y) in arena.armadilhas:
                        if spr_armadilha is not None:
                            self.superficie.blit(spr_armadilha, (px, py))
                        else:
                            self._desenhar_armadilha_geometrica(rect)

        for pos, minerio in arena.minerios.items():
            px, py = self.celula_para_pixel(pos)
            spr = self.sprites.get(minerio.tipo)
            if spr is not None:
                self.superficie.blit(spr, (px, py))
            else:
                self._desenhar_minerio_geometrico(px, py, t, minerio.tipo)

        for base, cor in (
            (config.BASE_ALFA, config.COR_ALFA),
            (config.BASE_BETA, config.COR_BETA),
        ):
            px, py = self.celula_para_pixel(base)
            pygame.draw.rect(
                self.superficie,
                cor,
                pygame.Rect(px + 4, py + 4, t - 8, t - 8),
                width=2,
                border_radius=6,
            )

        for agente in agentes:
            px, py = self.celula_para_pixel(agente.posicao)
            centro = (px + t // 2, py + t // 2)
            spr = self.sprites.get(self._chave_sprite_robo(agente))
            anel = (
                config.COR_BARRA_CRITICA
                if agente.bateria <= 20
                else (
                    config.COR_BARRA_BAIXA
                    if agente.bateria <= 40
                    else (255, 255, 255)
                )
            )
            if spr is not None:
                pygame.draw.circle(self.superficie, anel, centro, t // 2 - 2, 2)
                self.superficie.blit(spr, (px, py))
            else:
                raio = t // 3
                pygame.draw.circle(self.superficie, anel, centro, raio + 3, 3)
                pygame.draw.circle(self.superficie, agente.cor, centro, raio)
                pygame.draw.circle(self.superficie, (255, 255, 255), centro, raio, 2)
                inicial = self.fonte_hud.render(agente.nome[0], True, (12, 16, 22))
                self.superficie.blit(
                    inicial,
                    (
                        centro[0] - inicial.get_width() // 2,
                        centro[1] - inicial.get_height() // 2,
                    ),
                )

    def _barra_bateria(self, x: int, y: int, w: int, h: int, bateria: int) -> None:
        """Desenha barra de bateria proporcional.

        Args:
            x: Esquerda.
            y: Topo.
            w: Largura.
            h: Altura.
            bateria: Valor 0–100.
        """
        pygame.draw.rect(
            self.superficie, config.COR_BARRA_BG, pygame.Rect(x, y, w, h), border_radius=3
        )
        frac = max(0.0, min(1.0, bateria / config.BATERIA_INICIAL))
        if bateria <= 20:
            cor = config.COR_BARRA_CRITICA
        elif bateria <= 40:
            cor = config.COR_BARRA_BAIXA
        else:
            cor = config.COR_BARRA_OK
        if frac > 0:
            pygame.draw.rect(
                self.superficie,
                cor,
                pygame.Rect(x, y, int(w * frac), h),
                border_radius=3,
            )

    def desenhar_hud(
        self,
        partida: Partida,
        round_atual: int = 1,
        num_rounds: int = 1,
        placar: Optional[dict[str, int]] = None,
    ) -> None:
        """Desenha painel superior com cards dos robôs e info do torneio.

        Args:
            partida: Partida em andamento.
            round_atual: Round corrente (1-indexado).
            num_rounds: Total de rounds do torneio.
            placar: Placar acumulado do torneio.
        """
        top = config.ALTURA_BARRA_JANELA
        pygame.draw.rect(
            self.superficie,
            config.COR_PAINEL,
            pygame.Rect(0, top, self.superficie.get_width(), config.ALTURA_HUD),
        )
        pygame.draw.line(
            self.superficie,
            config.COR_GRADE,
            (0, top + config.ALTURA_HUD - 1),
            (self.superficie.get_width(), top + config.ALTURA_HUD - 1),
            1,
        )

        info = f"Turno {partida.turno}  ·  Seed {partida.seed}"
        if num_rounds > 1:
            info = f"Round {round_atual}/{num_rounds}  ·  " + info
            if placar:
                info += (
                    f"  ·  Placar A {placar.get('alfa', 0)}"
                    f"–{placar.get('beta', 0)}"
                    f" (E {placar.get('empates', 0)})"
                )
        titulo = self.fonte_hud.render(info, True, config.COR_TEXTO_SUAVE)
        self.superficie.blit(titulo, (14, top + 8))

        largura = self.superficie.get_width()
        card_w = (largura - 40) // 2
        for i, agente in enumerate(partida.agentes):
            cx = 12 + i * (card_w + 16)
            card = pygame.Rect(cx, top + 30, card_w, 78)
            pygame.draw.rect(self.superficie, (28, 40, 54), card, border_radius=8)
            pygame.draw.rect(self.superficie, agente.cor, card, 2, border_radius=8)

            nome = self.fonte.render(
                f"{agente.nome}  ·  {agente.pontuacao} pts", True, agente.cor
            )
            self.superficie.blit(nome, (cx + 12, top + 36))

            self._barra_bateria(
                cx + 12, top + 62, card_w - 24, 10, max(0, agente.bateria)
            )
            bat = self.fonte_pequena.render(
                f"Bateria {max(0, agente.bateria)}", True, config.COR_TEXTO_SUAVE
            )
            self.superficie.blit(bat, (cx + 12, top + 76))

            alvo = "—" if agente.alvo is None else str(agente.alvo)
            det = self.fonte_pequena.render(
                f"Carga {agente.carga}/{config.CAPACIDADE_CARGA}  ·  Alvo {alvo}",
                True,
                config.COR_TEXTO,
            )
            self.superficie.blit(det, (cx + 12, top + 92))

    def botao(
        self,
        texto: str,
        centro: tuple[int, int],
        tamanho: tuple[int, int] = (220, 48),
        mouse_pos: Optional[tuple[int, int]] = None,
    ) -> pygame.Rect:
        """Desenha um botão e devolve seu retângulo de colisão.

        Args:
            texto: Rótulo do botão.
            centro: Centro do botão em pixels.
            tamanho: Largura e altura.
            mouse_pos: Posição do mouse para hover.

        Returns:
            ``pygame.Rect`` clicável.
        """
        rect = pygame.Rect(0, 0, tamanho[0], tamanho[1])
        rect.center = centro
        hover = mouse_pos is not None and rect.collidepoint(mouse_pos)
        cor = config.COR_BOTAO_HOVER if hover else config.COR_BOTAO
        sombra = rect.move(0, 3)
        pygame.draw.rect(self.superficie, (10, 14, 20), sombra, border_radius=10)
        pygame.draw.rect(self.superficie, cor, rect, border_radius=10)
        pygame.draw.rect(self.superficie, config.COR_TEXTO, rect, 2, border_radius=10)
        label = self.fonte.render(texto, True, config.COR_TEXTO)
        self.superficie.blit(
            label,
            (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2),
        )
        return rect

    def tela_menu(self, mouse_pos: tuple[int, int]) -> dict[str, pygame.Rect]:
        """Desenha o menu principal.

        Args:
            mouse_pos: Posição do cursor.

        Returns:
            Mapa nome → retângulo dos botões.
        """
        self._preencher_gradiente()
        w, h = self.superficie.get_size()

        # Layout fixo centrado: painel dimensionado ao conteúdo (evita botão vazando).
        btn_h = 48
        btn_gap = 14
        n_botoes = 4
        titulo_bloco = 90
        padding_top = 28
        padding_bottom = 28
        padding_x = 36
        painel_w = 380
        painel_h = (
            padding_top
            + titulo_bloco
            + n_botoes * btn_h
            + (n_botoes - 1) * btn_gap
            + padding_bottom
        )
        painel = pygame.Rect(0, 0, painel_w, painel_h)
        painel.center = (w // 2, h // 2)

        pygame.draw.rect(self.superficie, config.COR_PAINEL, painel, border_radius=16)
        pygame.draw.rect(self.superficie, config.COR_GRADE, painel, 2, border_radius=16)

        titulo = self.fonte_titulo.render("ARENA BOT", True, config.COR_TEXTO)
        sub = self.fonte_subtitulo.render(
            "A*  ·  Minimax  ·  Lógica", True, config.COR_TEXTO_SUAVE
        )
        self.superficie.blit(
            titulo,
            (painel.centerx - titulo.get_width() // 2, painel.top + padding_top),
        )
        self.superficie.blit(
            sub,
            (painel.centerx - sub.get_width() // 2, painel.top + padding_top + 48),
        )

        primeiro_btn_y = painel.top + padding_top + titulo_bloco + btn_h // 2
        labels = (
            ("jogar", "Jogar"),
            ("opcoes", "Opções"),
            ("regras", "Regras"),
            ("sair", "Sair"),
        )
        botoes: dict[str, pygame.Rect] = {}
        for i, (chave, texto) in enumerate(labels):
            cy = primeiro_btn_y + i * (btn_h + btn_gap)
            botoes[chave] = self.botao(
                texto,
                (painel.centerx, cy),
                tamanho=(painel_w - 2 * padding_x, btn_h),
                mouse_pos=mouse_pos,
            )
        return botoes

    def tela_opcoes(
        self, cfg: ConfigPartida, mouse_pos: tuple[int, int]
    ) -> dict[str, pygame.Rect]:
        """Tela de parâmetros editáveis com botões − / +.

        Args:
            cfg: Configuração corrente.
            mouse_pos: Posição do cursor.

        Returns:
            Botões clicáveis (incluindo ``menos_*`` / ``mais_*``).
        """
        self._preencher_gradiente()
        w, h = self.superficie.get_size()
        titulo = self.fonte_titulo.render("Opções", True, config.COR_TEXTO)
        self.superficie.blit(titulo, (w // 2 - titulo.get_width() // 2, 28))
        dica = self.fonte_pequena.render(
            "Padrões do enunciado até você alterar", True, config.COR_TEXTO_SUAVE
        )
        self.superficie.blit(dica, (w // 2 - dica.get_width() // 2, 74))

        linhas = [
            ("num_rounds", "Rounds do torneio", cfg.num_rounds),
            ("num_paredes", "Paredes (obstáculos)", cfg.num_paredes),
            ("num_armadilhas", "Armadilhas", cfg.num_armadilhas),
            (
                "custo_passo_armadilha",
                "Dano da armadilha (bateria)",
                cfg.custo_passo_armadilha,
            ),
        ]
        botoes: dict[str, pygame.Rect] = {}
        y0 = 120
        for i, (campo, rotulo, valor) in enumerate(linhas):
            y = y0 + i * 58
            painel = pygame.Rect(60, y - 8, w - 120, 48)
            pygame.draw.rect(self.superficie, config.COR_PAINEL, painel, border_radius=8)
            pygame.draw.rect(self.superficie, config.COR_GRADE, painel, 1, border_radius=8)

            lab = self.fonte.render(rotulo, True, config.COR_TEXTO)
            self.superficie.blit(lab, (80, y + 6))
            val = self.fonte.render(str(valor), True, config.COR_ALFA)
            self.superficie.blit(val, (w // 2 + 40, y + 6))

            botoes[f"menos_{campo}"] = self.botao(
                "−", (w - 160, y + 16), tamanho=(44, 36), mouse_pos=mouse_pos
            )
            botoes[f"mais_{campo}"] = self.botao(
                "+", (w - 100, y + 16), tamanho=(44, 36), mouse_pos=mouse_pos
            )

        botoes["restaurar"] = self.botao(
            "Restaurar padrões", (w // 2, h - 100), tamanho=(240, 44), mouse_pos=mouse_pos
        )
        botoes["voltar"] = self.botao(
            "Voltar", (w // 2, h - 48), tamanho=(200, 44), mouse_pos=mouse_pos
        )
        return botoes

    def tela_regras(self, mouse_pos: tuple[int, int]) -> dict[str, pygame.Rect]:
        """Exibe resumo das regras do jogo.

        Args:
            mouse_pos: Posição do cursor.

        Returns:
            Botões clicáveis.
        """
        self._preencher_gradiente()
        linhas = [
            "Dois robôs (Alfa e Beta) coletam minérios em uma grade 15x9.",
            "A* com heurística Manhattan calcula rotas evitando armadilhas.",
            "Minimax com poda alfa-beta escolhe o alvo estratégico.",
            "Base de conhecimento proposicional autoriza a coleta.",
            "Vence quem tiver mais pontos ao fim da partida.",
            "Em Opções: rounds, paredes, armadilhas e dano na bateria.",
            "P: pausar  |  R: reiniciar round  |  ESC: menu",
        ]
        y = 70
        for linha in linhas:
            surf = self.fonte.render(linha, True, config.COR_TEXTO)
            self.superficie.blit(surf, (36, y))
            y += 34
        w, h = self.superficie.get_size()
        return {"voltar": self.botao("Voltar", (w // 2, h - 60), mouse_pos=mouse_pos)}

    def tela_pausa(self, mouse_pos: tuple[int, int]) -> dict[str, pygame.Rect]:
        """Overlay de pausa.

        Args:
            mouse_pos: Posição do cursor.

        Returns:
            Botões da pausa.
        """
        overlay = pygame.Surface(self.superficie.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.superficie.blit(overlay, (0, 0))
        w, h = self.superficie.get_size()
        titulo = self.fonte_titulo.render("PAUSADO", True, config.COR_TEXTO)
        self.superficie.blit(titulo, (w // 2 - titulo.get_width() // 2, h // 3))
        return {
            "continuar": self.botao("Continuar", (w // 2, h // 2), mouse_pos=mouse_pos),
            "reiniciar": self.botao("Reiniciar", (w // 2, h // 2 + 70), mouse_pos=mouse_pos),
            "menu": self.botao("Menu", (w // 2, h // 2 + 140), mouse_pos=mouse_pos),
        }

    def tela_fim_partida(
        self,
        partida: Partida,
        mouse_pos: tuple[int, int],
        *,
        round_atual: int,
        num_rounds: int,
        tem_proximo: bool,
    ) -> dict[str, pygame.Rect]:
        """Tela ao fim de um round (antes do próximo ou do resumo).

        Args:
            partida: Partida encerrada.
            mouse_pos: Cursor.
            round_atual: Round atual.
            num_rounds: Total.
            tem_proximo: Se ainda há rounds no torneio.

        Returns:
            Botões disponíveis.
        """
        overlay = pygame.Surface(self.superficie.get_size(), pygame.SRCALPHA)
        overlay.fill((8, 12, 18, 200))
        self.superficie.blit(overlay, (0, 0))
        w, h = self.superficie.get_size()
        resultado = partida.resultado()
        if resultado == ResultadoPartida.VITORIA_ALFA:
            msg, cor = "Alfa venceu o round!", config.COR_ALFA
        elif resultado == ResultadoPartida.VITORIA_BETA:
            msg, cor = "Beta venceu o round!", config.COR_BETA
        else:
            msg, cor = "Empate no round!", config.COR_TEXTO

        titulo = self.fonte_titulo.render(msg, True, cor)
        self.superficie.blit(titulo, (w // 2 - titulo.get_width() // 2, h // 5))
        placar = self.fonte.render(
            f"Alfa {partida.alfa.pontuacao}  ×  {partida.beta.pontuacao} Beta",
            True,
            config.COR_TEXTO,
        )
        self.superficie.blit(placar, (w // 2 - placar.get_width() // 2, h // 5 + 55))
        meta = self.fonte_hud.render(
            f"Round {round_atual}/{num_rounds}  ·  {partida.turno} turnos",
            True,
            config.COR_TEXTO_SUAVE,
        )
        self.superficie.blit(meta, (w // 2 - meta.get_width() // 2, h // 5 + 90))

        botoes: dict[str, pygame.Rect] = {}
        y = h // 2 + 20
        if tem_proximo:
            botoes["proximo"] = self.botao(
                "Próximo round", (w // 2, y), mouse_pos=mouse_pos
            )
            y += 70
        else:
            botoes["resumo"] = self.botao(
                "Ver resultado do torneio", (w // 2, y), tamanho=(280, 48), mouse_pos=mouse_pos
            )
            y += 70
        botoes["menu"] = self.botao("Menu", (w // 2, y), mouse_pos=mouse_pos)
        return botoes

    def tela_resumo_torneio(
        self,
        placar: dict[str, int],
        mouse_pos: tuple[int, int],
    ) -> dict[str, pygame.Rect]:
        """Resumo final do torneio.

        Args:
            placar: Contagem de vitórias/empates.
            mouse_pos: Cursor.

        Returns:
            Botões da tela.
        """
        self._preencher_gradiente()
        w, h = self.superficie.get_size()
        titulo = self.fonte_titulo.render("Torneio encerrado", True, config.COR_TEXTO)
        self.superficie.blit(titulo, (w // 2 - titulo.get_width() // 2, h // 5))

        linhas = [
            (f"Vitórias Alfa: {placar.get('alfa', 0)}", config.COR_ALFA),
            (f"Vitórias Beta: {placar.get('beta', 0)}", config.COR_BETA),
            (f"Empates: {placar.get('empates', 0)}", config.COR_TEXTO_SUAVE),
        ]
        y = h // 5 + 70
        for texto, cor in linhas:
            surf = self.fonte_subtitulo.render(texto, True, cor)
            self.superficie.blit(surf, (w // 2 - surf.get_width() // 2, y))
            y += 36

        a, b = placar.get("alfa", 0), placar.get("beta", 0)
        if a > b:
            campeao, cor_c = "Campeão: Alfa", config.COR_ALFA
        elif b > a:
            campeao, cor_c = "Campeão: Beta", config.COR_BETA
        else:
            campeao, cor_c = "Torneio empatado", config.COR_TEXTO
        camp = self.fonte.render(campeao, True, cor_c)
        self.superficie.blit(camp, (w // 2 - camp.get_width() // 2, y + 20))

        return {
            "reiniciar": self.botao(
                "Jogar de novo", (w // 2, h // 2 + 80), mouse_pos=mouse_pos
            ),
            "menu": self.botao("Menu", (w // 2, h // 2 + 150), mouse_pos=mouse_pos),
            "sair": self.botao("Sair", (w // 2, h // 2 + 220), mouse_pos=mouse_pos),
        }
