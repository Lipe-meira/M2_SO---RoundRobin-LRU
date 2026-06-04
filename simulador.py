from collections import deque

with open("arquivo_teste.txt", "r", encoding="utf-8") as arquivo:
    conteudo = arquivo.readlines()

    quantum, qntd_frames_ram, penalidade_io = [int(i) for i in conteudo[0].split()]

    processos = []
    for linha in conteudo[1:]:
        linha_split = linha.split()
        nome = linha_split[1]
        chegada = int(linha_split[0])
        paginas = [int(i) for i in linha_split[2].split(",")]
        processos.append(
            {
                "nome": nome,
                "chegada": chegada,
                "paginas": paginas,
                "indice_atual": 0,
                "page_faults": 0,
                "tempo_conclusao": None,
                "estado": "novo",
            }
        )

    fila_prontos = deque()
    tempo = 0
    # print(fila_prontos, tempo)

    processo_cpu = None
    quantum_usado = 0

    while any (processo.get('estado') != 'finalizado' for processo in processos):
        print(tempo, " segundos")
        for processo in processos:
            if processo.get("chegada") == tempo and processo.get("estado") == "novo":
                processo["estado"] = "pronto"
                fila_prontos.append(processo)
                print(processo.get("nome"), " chegou")

        # escalonamento
        if processo_cpu == None and fila_prontos:
            processo_cpu = fila_prontos.popleft()
            processo_cpu["estado"] = "executando"
            quantum_usado = 0
            print(processo_cpu.get("nome"), " começou a executar")

        if processo_cpu:
            print(processo_cpu["nome"], ' executou pagina ', processo_cpu["paginas"][processo_cpu["indice_atual"]])
            processo_cpu["indice_atual"] += 1
            quantum_usado += 1
            
            if processo_cpu["indice_atual"] == len(processo_cpu["paginas"]):
                processo_cpu['estado'] = "finalizado"
                processo_cpu["tempo_conclusao"] = tempo + 1
                print(processo_cpu["nome"], "foi finalizado no tempo", processo_cpu["tempo_conclusao"])
                processo_cpu = None
                quantum_usado = 0

            elif quantum_usado == quantum:
                processo_cpu["estado"] = "pronto"
                fila_prontos.append(processo_cpu)
                print(processo_cpu["nome"], " foi para a fila de prontos")
                processo_cpu = None
                quantum_usado = 0
        

        print("fila de prontos:")
        for processo in fila_prontos:
            print(processo.get("nome"))

        tempo += 1

