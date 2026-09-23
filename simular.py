from core.partida import criar_partida

mortes=0
for seed in range (1, 31):
    p= criar_partida(seed=seed)
    while p.executar_turno() and p.turno < 2000:
        pass
    for robo in p.agentes:
        if robo.bateria <=0:
            mortes += 1
            print(f"seed {seed}: {robo.nome} morreu com carga {robo.carga}")
print("total de mortes:", mortes)
