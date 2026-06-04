with open('arquivo_teste.txt', 'r', encoding='utf-8') as arquivo:
    conteudo = arquivo.readlines()
   
    quantum, qntd_frames_ram, penalidade_io = [int(i) for i in conteudo[0].split()]
 
  
    processos = []
    for linha in conteudo[1:]:
        linha_split = linha.split()
        nome = linha_split[1]
        chegada = int(linha_split[0])
        paginas = [int(i) for i in linha_split[2].split(',')]
        processos.append({
            'nome': nome,
         'chegada': chegada, 
         'paginas': paginas, 
         'indice_atual': 0, 
         'page_faults': 0,
         'tempo_conclusao': None, 
         'estado': 'novo'})

  
        
    
    



