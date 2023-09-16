from multiprocessing import Process
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


class Corretor:
    def __init__(self, linhas: list[str], Nprocessos: int, Nthreads: int):
        # são 9 linhas por jogo mais uma em branco,
        # menos o último, por isso precisa somar 1
        Njogos = (len(linhas) + 1)//10
        cond = [Nprocessos, Njogos]
        # se Nprocessos for maior que
        # o número de jogos, é alterado
        Nprocessos = cond[int(Nprocessos > Njogos)]
        self.Nprocessos = Nprocessos
        self.Nthreads = Nthreads
        cond = [Nthreads, 9]
        # mesma coisa com as threads
        Nthreads = cond[int(Nthreads > 9)]
        jogos_por_processo = Njogos//Nprocessos
        resto_jogos = Njogos % Nprocessos
        slots_por_thread = 9//Nthreads
        resto_threads = 9 % Nthreads
        self.workers = [None]*Nprocessos
        for i in range(Nprocessos):
            self.workers[i] = Process(target=self.__processos,
                                      args=(i+1,
                                            linhas,
                                            Nthreads,
                                            resto_jogos,
                                            resto_threads,
                                            slots_por_thread,
                                            jogos_por_processo))
        for i in self.workers:
            i.start()
        for i in self.workers:
            i.join()

    def __processos(self, P: int, arquivo: list[str],
                    Nthreads: int,
                    resto_jogos: int,
                    resto_threads: int,
                    slots_por_thread: int,
                    jogos_por_processo: int):
        # divisão dos jogos
        inicio = jogos_por_processo*(P - 1)
        fim = jogos_por_processo*P
        if P <= resto_jogos:
            inicio += (P-1)
            fim += P
        else:
            inicio += resto_jogos
            fim += resto_jogos
        indexs = [i for i in range(inicio, fim)]
        Njogos = len(indexs)
        # tudo menos a quebra de linha
        jogos = [[[int(a) for a in arquivo[J*10 + i][:9]]
                  for i in range(9)] for J in indexs]

        # correção pelas threads
        CorretorasPool = ThreadPoolExecutor(max_workers=Nthreads)
        corretoras = [None]*Nthreads
        for i in range(Nthreads):
            # divisão do trabalho
            inicios_t = slots_por_thread*(i)
            finais_t = slots_por_thread*(i+1)
            # equivalente a um if i < resto_threads
            # inicios_t e finais_t += 1
            # para compensar o arredondamento para baixo
            cond = int(i < resto_threads)
            cond_inicios = [resto_threads, i]
            cond_finais = [resto_threads, i+1]
            inicios_t += cond_inicios[cond]
            finais_t += cond_finais[cond]
            corretoras[i] = CorretorasPool.submit(self.__threads,
                                                  inicios_t,
                                                  finais_t,
                                                  indexs,
                                                  jogos,
                                                  i+1)
        CorretorasPool.shutdown()
        PosicoesDosErros = [{} for i in range(Njogos)]
        for J in range(Njogos):
            self.print_inicial(P, indexs[J])
            # saida
            erros = 0
            for i in range(Nthreads):
                # coleta os resultados de cada thread para cada jogo
                matErros, mat_CoorErradas = corretoras[i].result()
                erros += matErros[J]
                PosicoesDosErros[J]["T" + str(i+1)] = mat_CoorErradas[J]
            self.print_final(erros, Nthreads, P, PosicoesDosErros[J])

    def __threads(self, inicio: int, fim: int, indexs: list[int],
                  jogos: list[list[list[int]]], id: int):
        gabarito = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        coluna = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        regiao = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        Njogos = len(indexs)
        vet_Erros = [0]*Njogos
        mat_CoorErradas = [None]*Njogos
        for J in range(Njogos):
            meusErros = 0
            erros_linha = []
            erros_coluna = []
            erros_regiao = []
            # processo para encontrar erros
            for i in range(inicio, fim):
                pos = str(i+1)
                cond_col = [[], ["C" + pos]]
                cond_lin = [[], ["L" + pos]]
                cond_reg = [[], ["R" + pos]]
                # processo para coletar
                # regiões e colunas
                for j in range(3):
                    l = (i//3)*3 + j
                    for k in range(3):
                        c = (i % 3)*3 + k
                        # ii é para ser o
                        # equivalente de
                        # for ii in range(9)
                        ii = 3*j + k
                        coluna[ii] = jogos[J][ii][i]
                        regiao[ii] = jogos[J][l][c]
                # ----------- primeiro a linha i ----------
                cond = int(sorted(jogos[J][i]) != gabarito)
                # extend Li se a condição
                # for verdadeira, se não 0
                erros_linha.extend(cond_lin[cond])
                meusErros += cond
                # -------- depois a coluna i ---------
                cond = int(sorted(coluna) != gabarito)
                # extend Ci se a condição
                # for verdadeira, se não 0
                erros_coluna.extend(cond_col[cond])
                meusErros += cond
                # ------- e por fim a região i -------
                cond = int(sorted(regiao) != gabarito)
                # extend Ri se a condição
                # for verdadeira, se não 0
                erros_regiao.extend(cond_reg[cond])
                meusErros += cond
            # ao final de cada jogo, a seção
            # correspondente recebe os resultados
            mat_CoorErradas[J] = erros_linha + erros_coluna + erros_regiao
            vet_Erros[J] = meusErros
        return vet_Erros, mat_CoorErradas

    def print_inicial(self, P: int, J: int):
        saida = list("Processo " + str(P) + ": ")
        saida.extend(list("resolvendo "))
        saida.extend(list("quebra-cabeças " + str(J+1)))
        print("".join(saida))

    def print_final(self, erros: int, Nthreads: int,
                    P: int, PosicoesDosErros: dict):
        saida = list("Processo " + str(P) + ": " +
                     str(erros) + " erros encontrados")
        if erros > 0:
            saida += [" ", "("]
            for i in range(Nthreads):
                chave = "T" + str(i+1)
                if PosicoesDosErros[chave]:
                    saida += ["T", str(i+1), ":"]
                    for j in PosicoesDosErros[chave]:
                        saida += [" ", j, ","]
                    saida.pop()
                    saida += [";", " "]
            saida.pop()
            saida[-1] = ")"
        print(''.join(saida))
