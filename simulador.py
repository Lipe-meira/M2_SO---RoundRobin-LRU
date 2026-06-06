from collections import deque


def todos_finalizados(processos):
    for processo in processos:
        if processo.get("estado") != "finalizado":
            return False
    return True


def imprimir_fila(fila_prontos):
    for processo in fila_prontos:
        print(processo.get("nome"))


def adicionar_chegadas(processos, fila_prontos, tempo):
    for processo in processos:
        if processo.get("chegada") == tempo and processo.get("estado") == "novo":
            processo["estado"] = "pronto"
            fila_prontos.append(processo)
            print(processo.get("nome"), " chegou")

def atualizar_bloqueados(bloqueados, fila_prontos, tempo):
    for item in bloqueados[:]:
        if item.get("tempo_retorno") == tempo:
            processo = item.get("processo")
            processo["estado"] = "pronto"
            fila_prontos.append(processo)
            bloqueados.remove(item)
            print(processo["nome"], "retornou I/O")

def ler_arquivo(nome_arquivo):
    with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.readlines()
        processos = []
        quantum, qntd_frames_ram, penalidade_io = [int(i) for i in conteudo[0].split()]

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

    return quantum, qntd_frames_ram, penalidade_io, processos


# RR sem prioridade
def escolher_processo(fila_prontos):
    processo_cpu = fila_prontos.popleft()
    processo_cpu["estado"] = "executando"
    print(processo_cpu.get("nome"), "começou a executar")
    return processo_cpu


def buscar_pagina_ram(nome_processo, numero_pagina, ram):
    for frame in ram:  # se o frame contem a pagina desejada
        if (
            frame.get("processo") == nome_processo
            and frame.get("pagina") == numero_pagina
        ):
            return frame
    return None

def escolher_indice_lru(ram):
    indice_lru = 0

    for i in range(1, len(ram)):
        if ram[i].get("ultimo_acesso") < ram[indice_lru].get("ultimo_acesso"):
            indice_lru = i

        elif ram[i].get("ultimo_acesso") == ram[indice_lru].get("ultimo_acesso"):
            if ram[i].get("ordem_chegada") < ram[indice_lru].get("ordem_chegada"):
                indice_lru = i

    return indice_lru


    
# LRU ordem_chegada
def carregar_pagina_ram(ram, nome_processo, numero_pagina, tempo, ordem_chegada, qntd_frames_ram):
    dic = {
        "processo": nome_processo,
        "pagina": numero_pagina,
        "ultimo_acesso": tempo,
        "ordem_chegada": ordem_chegada,
    }

    if len(ram) >= qntd_frames_ram:
        indice_lru = escolher_indice_lru(ram)
        pagina_removida = ram.pop(indice_lru)
        print(
            "LRU removeu a pagina",
            pagina_removida["pagina"],
            "do processo",
            pagina_removida["processo"]
        )

    ram.append(dic)
    return ordem_chegada + 1


quantum, qntd_frames_ram, penalidade_io, processos = ler_arquivo("arquivo_teste.txt")
fila_prontos = deque()
tempo = 0
bloqueados = []

print(
    "quantum ",
    quantum,
    "\nquantidade Frames ",
    qntd_frames_ram,
    "\npenalidade I/O ",
    penalidade_io,
    "\n",
)

processo_cpu = None
quantum_usado = 0
ram = []

# LRU ordem_chegada
ordem_chegada = 0

while not todos_finalizados(processos):

    print(tempo, " segundos")
    adicionar_chegadas(processos, fila_prontos, tempo)
    atualizar_bloqueados(bloqueados, fila_prontos, tempo)

    # escalonamento
    if processo_cpu is None and fila_prontos:
        processo_cpu = escolher_processo(fila_prontos)
        quantum_usado = 0

    if processo_cpu:
        # pagina atual que vai ser executada, [1,2,3] ex: indice[0] = [1], indice[1] = [2], indice[2] = [3]
        pagina_desejada = processo_cpu["paginas"][processo_cpu["indice_atual"]]
        hit = buscar_pagina_ram(processo_cpu["nome"], pagina_desejada, ram)

        # page fault
        if hit is None:
            print(
                "\nO processo",
                processo_cpu["nome"],
                "sofreu page fault na pagina ",
                processo_cpu["paginas"][processo_cpu["indice_atual"]],
                "\n",
            )
            processo_cpu["page_faults"] += 1
            ordem_chegada = carregar_pagina_ram(
                ram, processo_cpu["nome"], pagina_desejada, tempo, ordem_chegada, qntd_frames_ram
            )
            processo_cpu["estado"] = "bloqueado"
            bloqueados.append({"processo":processo_cpu, "tempo_retorno":tempo + penalidade_io})
            processo_cpu = None
            quantum_usado = 0

        else:  # hit  is not None
            hit["ultimo_acesso"] = tempo
            print("RAM Hit:", processo_cpu["nome"], "acessou pagina", pagina_desejada)

            print(
                processo_cpu["nome"],
                " executou pagina ",
                processo_cpu["paginas"][processo_cpu["indice_atual"]],
                "\n",
            )
            processo_cpu["indice_atual"] += 1
            quantum_usado += 1

            if processo_cpu["indice_atual"] == len(processo_cpu["paginas"]):
                processo_cpu["estado"] = "finalizado"
                processo_cpu["tempo_conclusao"] = tempo + 1
                print(
                    processo_cpu["nome"],
                    "foi finalizado no tempo",
                    processo_cpu["tempo_conclusao"],
                    "\n",
                )
                processo_cpu = None
                quantum_usado = 0

            elif quantum_usado == quantum:
                processo_cpu["estado"] = "pronto"
                fila_prontos.append(processo_cpu)
                print(
                    processo_cpu["nome"],
                    " esgotou o quantum, foi para a fila de prontos",
                    "\n",
                )
                processo_cpu = None
                quantum_usado = 0

    tempo += 1

print("=== RESULTADOS FINAIS ===")

for processo in processos:
    tempo_retorno = processo["tempo_conclusao"] - processo["chegada"]
    print(processo["nome"],
          " tempo de retorno = ", 
          tempo_retorno,
          ", page faults = ",
          processo["page_faults"])
    
print("\nEstado final da RAM: ")
for i, frame in enumerate(ram):
    print(
        "Frame", i,
        ": ", frame["processo"],
        "pagina ", frame["pagina"]
    )