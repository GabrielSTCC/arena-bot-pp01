"""Encontra situações reais do jogo e mostra o rastreamento da BC."""

from core.partida import criar_partida
from ia import conhecimento as kb


def classificar(fatos, conclusoes, coletou):
    """Diz qual situação da tabela o turno representa (ou None)."""
    if coletou:
        return "Coleta autorizada"
    if kb.SIMBOLO_SMINERIO in fatos and kb.SIMBOLO_ACOLETAR not in conclusoes:
        return "Coleta negada"
    if kb.SIMBOLO_SMINERIO not in fatos and kb.SIMBOLO_CCHEIA not in fatos:
        return "Em trânsito, fora de minério"
    return None


encontradas = {}
for seed in range(1, 31):
    p = criar_partida(seed=seed)
    continua = True
    while continua and len(encontradas) < 3:
        robo = p.agente_da_vez()
        carga_antes = robo.carga
        continua = p.executar_turno()

        fatos = robo.bc.ultimos_observados
        conclusoes = [c for _, c in robo.bc.ultimo_rastreio]
        situacao = classificar(fatos, conclusoes, robo.carga > carga_antes)

        if situacao and situacao not in encontradas:
            encontradas[situacao] = (
                f"semente {seed}, turno {p.turno}, {robo.nome}, "
                f"bateria {robo.bateria}, carga {carga_antes}",
                sorted(fatos),
                list(robo.bc.ultimo_rastreio),
            )
    if len(encontradas) == 3:
        break

for situacao, (contexto, fatos, rastreio) in encontradas.items():
    print(f"=== {situacao} ({contexto})")
    print("  Fatos observados:", ", ".join(fatos))
    for regra, conclusao in rastreio:
        print(f"  {regra}  =>  {conclusao}")
    print()

    
# Cenário montado: a R3 nunca disparou nas partidas reais, porque o filtro
# do Minimax impede o robô de chegar perto do limite de bateria.
bc = kb.construir_base_padrao()
fatos = {kb.SIMBOLO_BALTA, kb.SIMBOLO_BATERIA_CRITICA, kb.SIMBOLO_SMINERIO}
bc.inferir(fatos)
print("=== Bateria crítica (cenário montado)")
print("  Fatos observados:", ", ".join(sorted(fatos)))
for regra, conclusao in bc.ultimo_rastreio:
    print(f"  {regra}  =>  {conclusao}")

