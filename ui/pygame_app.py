"""
Aplicação Pygame: menu, opções, torneio, partida, pausa e fim.
"""

from __future__ import annotations

import random
from enum import Enum, auto
from typing import Optional

import pygame

import config
from core.config_partida import ConfigPartida
from core.partida import Partida, ResultadoPartida, criar_partida
from ui.renderer import Renderer


class EstadoUI(Enum):
    """Máquina de estados da interface."""

    MENU = auto()
    OPCOES = auto()
    REGRAS = auto()
    JOGANDO = auto()
    PAUSADO = auto()
    FIM_PARTIDA = auto()
    RESUMO_TORNEIO = auto()


class Aplicacao:
    """Controla o loop principal da interface gráfica.

    Attributes:
        cfg: Parâmetros editáveis (defaults do enunciado).
        round_atual: Índice 1-based do round corrente.
        placar_torneio: Contagem de vitórias/empates no torneio.
    """

    def __init__(self) -> None:
        """Inicializa Pygame e cria a janela dimensionada pela grade."""
        pygame.init()
        self.largura_normal = config.LARGURA_GRADE * config.TAMANHO_CELULA
        self.altura_normal = (
            config.ALTURA_BARRA_JANELA
            + config.ALTURA_GRADE * config.TAMANHO_CELULA
            + config.ALTURA_HUD
            + config.ALTURA_AREA
        )
        self.largura_janela = self.largura_normal
        self.altura_janela = self.altura_normal
        self.tela = pygame.display.set_mode(
            (self.largura_janela, self.altura_janela), pygame.RESIZABLE
        )
        pygame.display.set_caption("Arena Bot — PP01")
        self.relogio = pygame.time.Clock()
        self.renderer = Renderer(self.tela)
        self.estado = EstadoUI.MENU
        self.partida: Optional[Partida] = None
        self.botoes: dict[str, pygame.Rect] = {}
        self.tempo_proximo_turno = 0
        self._rodando = True
        self.cfg = ConfigPartida()
        self.round_atual = 1
        self.placar_torneio = {"alfa": 0, "beta": 0, "empates": 0}
        self._maximizado = False

    def iniciar_torneio(self) -> None:
        """Reinicia placar e começa o round 1."""
        self.cfg.normalizar()
        self.round_atual = 1
        self.placar_torneio = {"alfa": 0, "beta": 0, "empates": 0}
        self.nova_partida()
        self.estado = EstadoUI.JOGANDO

    def nova_partida(self, seed: Optional[int] = None) -> None:
        """Cria uma nova partida com a configuração atual.

        Args:
            seed: Semente opcional; se None, sorteia.
        """
        if seed is None:
            seed = random.randint(1, 10_000_000)
        self.partida = criar_partida(seed=seed, cfg=self.cfg)
        self.tempo_proximo_turno = pygame.time.get_ticks()

    def _registrar_resultado_round(self) -> None:
        """Atualiza o placar do torneio com o resultado da partida atual."""
        if self.partida is None:
            return
        res = self.partida.resultado()
        if res == ResultadoPartida.VITORIA_ALFA:
            self.placar_torneio["alfa"] += 1
        elif res == ResultadoPartida.VITORIA_BETA:
            self.placar_torneio["beta"] += 1
        elif res == ResultadoPartida.EMPATE:
            self.placar_torneio["empates"] += 1

    def _ha_proximo_round(self) -> bool:
        """Indica se ainda restam rounds após o atual."""
        return self.round_atual < self.cfg.num_rounds

    def _avancar_round(self) -> None:
        """Inicia o próximo round do torneio."""
        self.round_atual += 1
        self.nova_partida()
        self.estado = EstadoUI.JOGANDO

    def executar(self) -> None:
        """Loop principal até o usuário sair."""
        while self._rodando:
            mouse = pygame.mouse.get_pos()
            self._processar_eventos()
            self._atualizar()
            self._desenhar(mouse)
            pygame.display.flip()
            self.relogio.tick(config.FPS)
        pygame.quit()

    def _aplicar_modo_janela(self) -> None:
        """Recria o display no tamanho normal ou maximizado (sem loop de resize)."""
        if self._maximizado:
            info = pygame.display.Info()
            # Usa tamanho da tela sem FULLSCREEN para evitar flicker no Wayland.
            self.tela = pygame.display.set_mode((info.current_w, info.current_h))
        else:
            self.tela = pygame.display.set_mode(
                (self.largura_normal, self.altura_normal)
            )
        self.largura_janela, self.altura_janela = self.tela.get_size()
        self.renderer.atualizar_superficie(self.tela)

    def _minimizar_janela(self) -> None:
        """Minimiza a janela do sistema operacional."""
        pygame.display.iconify()

    def _alternar_maximizar(self) -> None:
        """Alterna entre tamanho normal e maximizado."""
        self._maximizado = not self._maximizado
        self._aplicar_modo_janela()

    def _fechar_aplicacao(self) -> None:
        """Encerra o loop principal e libera o Pygame."""
        self._rodando = False

    def _processar_eventos(self) -> None:
        """Trata teclado e cliques."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self._fechar_aplicacao()
            elif evento.type == pygame.KEYDOWN:
                self._tecla(evento.key)
            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                self._clique(evento.pos)
            elif evento.type == pygame.VIDEORESIZE:
                self.largura_janela, self.altura_janela = evento.size
                self.tela = pygame.display.set_mode(
                    (self.largura_janela, self.altura_janela), pygame.RESIZABLE
                )
                self.renderer.atualizar_superficie(self.tela)

    def _tecla(self, tecla: int) -> None:
        """Atalhos de teclado.

        Args:
            tecla: Código da tecla Pygame.
        """
        if tecla == pygame.K_ESCAPE:
            if self._maximizado:
                self._alternar_maximizar()
            else:
                self.estado = EstadoUI.MENU
        elif tecla == pygame.K_F11:
            self._alternar_maximizar()
        elif tecla == pygame.K_p and self.estado == EstadoUI.JOGANDO:
            self.estado = EstadoUI.PAUSADO
        elif tecla == pygame.K_p and self.estado == EstadoUI.PAUSADO:
            self.estado = EstadoUI.JOGANDO
            self.tempo_proximo_turno = pygame.time.get_ticks()
        elif tecla == pygame.K_r and self.estado in (
            EstadoUI.JOGANDO,
            EstadoUI.PAUSADO,
            EstadoUI.FIM_PARTIDA,
        ):
            self.nova_partida()
            self.estado = EstadoUI.JOGANDO

    def _clique(self, pos: tuple[int, int]) -> None:
        """Resolve clique nos botões da tela atual.

        Args:
            pos: Coordenada do clique.
        """
        for nome, rect in self.botoes.items():
            if not rect.collidepoint(pos):
                continue

            # Controles da janela (qualquer tela)
            if nome == "win_minimizar":
                self._minimizar_janela()
                return
            if nome == "win_maximizar":
                self._alternar_maximizar()
                return
            if nome == "win_fechar":
                self._fechar_aplicacao()
                return

            if self.estado == EstadoUI.MENU:
                if nome == "jogar":
                    self.iniciar_torneio()
                elif nome == "opcoes":
                    self.estado = EstadoUI.OPCOES
                elif nome == "regras":
                    self.estado = EstadoUI.REGRAS
                elif nome == "sair":
                    self._fechar_aplicacao()

            elif self.estado == EstadoUI.OPCOES:
                if nome == "voltar":
                    self.cfg.normalizar()
                    self.estado = EstadoUI.MENU
                elif nome == "restaurar":
                    self.cfg.restaurar_padroes()
                elif nome.startswith("menos_"):
                    self.cfg.ajustar(nome[len("menos_") :], -1)
                elif nome.startswith("mais_"):
                    self.cfg.ajustar(nome[len("mais_") :], 1)

            elif self.estado == EstadoUI.REGRAS:
                if nome == "voltar":
                    self.estado = EstadoUI.MENU

            elif self.estado == EstadoUI.JOGANDO:
                if nome == "pausar":
                    self.estado = EstadoUI.PAUSADO

            elif self.estado == EstadoUI.PAUSADO:
                if nome == "continuar":
                    self.estado = EstadoUI.JOGANDO
                    self.tempo_proximo_turno = pygame.time.get_ticks()
                elif nome == "reiniciar":
                    self.nova_partida()
                    self.estado = EstadoUI.JOGANDO
                elif nome == "menu":
                    self.estado = EstadoUI.MENU

            elif self.estado == EstadoUI.FIM_PARTIDA:
                if nome == "proximo":
                    self._avancar_round()
                elif nome == "resumo":
                    self.estado = EstadoUI.RESUMO_TORNEIO
                elif nome == "menu":
                    self.estado = EstadoUI.MENU

            elif self.estado == EstadoUI.RESUMO_TORNEIO:
                if nome == "reiniciar":
                    self.iniciar_torneio()
                elif nome == "menu":
                    self.estado = EstadoUI.MENU
                elif nome == "sair":
                    self._fechar_aplicacao()
            break

    def _atualizar(self) -> None:
        """Avança turnos automaticamente durante o jogo."""
        if self.estado != EstadoUI.JOGANDO or self.partida is None:
            return
        agora = pygame.time.get_ticks()
        if agora < self.tempo_proximo_turno:
            return
        continua = self.partida.executar_turno()
        self.tempo_proximo_turno = agora + config.DELAY_TURNO_MS
        if not continua or self.partida.terminou():
            self._registrar_resultado_round()
            self.estado = EstadoUI.FIM_PARTIDA

    def _desenhar(self, mouse_pos: tuple[int, int]) -> None:
        """Desenha a tela correspondente ao estado.

        Args:
            mouse_pos: Posição do mouse para hover.
        """
        if self.estado == EstadoUI.MENU:
            self.botoes = self.renderer.tela_menu(mouse_pos)

        elif self.estado == EstadoUI.OPCOES:
            self.botoes = self.renderer.tela_opcoes(self.cfg, mouse_pos)

        elif self.estado == EstadoUI.REGRAS:
            self.botoes = self.renderer.tela_regras(mouse_pos)

        elif self.estado in (EstadoUI.JOGANDO, EstadoUI.PAUSADO) and self.partida:
            self.renderer.desenhar_arena(self.partida.arena, self.partida.agentes)
            self.renderer.desenhar_hud(
                self.partida,
                round_atual=self.round_atual,
                num_rounds=self.cfg.num_rounds,
                placar=self.placar_torneio,
            )
            self.botoes = {
                "pausar": self.renderer.botao(
                    "Pausar",
                    (self.largura_janela - 200, config.ALTURA_BARRA_JANELA // 2),
                    tamanho=(90, 26),
                    mouse_pos=mouse_pos,
                )
            }
            if self.estado == EstadoUI.PAUSADO:
                self.botoes.update(self.renderer.tela_pausa(mouse_pos))

        elif self.estado == EstadoUI.FIM_PARTIDA and self.partida:
            self.renderer.desenhar_arena(self.partida.arena, self.partida.agentes)
            self.renderer.desenhar_hud(
                self.partida,
                round_atual=self.round_atual,
                num_rounds=self.cfg.num_rounds,
                placar=self.placar_torneio,
            )
            self.botoes = self.renderer.tela_fim_partida(
                self.partida,
                mouse_pos,
                round_atual=self.round_atual,
                num_rounds=self.cfg.num_rounds,
                tem_proximo=self._ha_proximo_round(),
            )

        elif self.estado == EstadoUI.RESUMO_TORNEIO:
            self.botoes = self.renderer.tela_resumo_torneio(
                self.placar_torneio, mouse_pos
            )
        else:
            self.botoes = {}

        self.botoes.update(
            self.renderer.desenhar_controles_janela(
                mouse_pos, maximizado=self._maximizado
            )
        )
