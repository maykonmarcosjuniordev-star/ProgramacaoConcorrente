from Corretor import Corretor
import time


def escreve_resultado(tempo: float):
    temporizacao = open("temporizacao.txt", 'a')
    temporizacao.write("--------------------\n")
    temporizacao.write(str(Nprocessos) + " Processo(s) " +
                       str(Nthreads) + " Thread(s)\n")
    temporizacao.write("Tempo de execução = " +
                       str(tempo) + '\n')
    temporizacao.close()


entrada = input().split()
if (len(entrada) >= 3):
    NomeArquivo = entrada[0]
    try:
        arquivo = open(NomeArquivo, 'r')
    except:
        print("Arquivo Inválido")
    else:
        linhas = arquivo.readlines()
        arquivo.close()
        try:
            Nprocessos = int(entrada[1])
            Nthreads = int(entrada[2])
        except:
            print("Valores Inválidos Para Nprocessos e Nthreads!!!")
        else:
            if (Nthreads > 0 and Nprocessos > 0):
                # inicio = time.time()
                jogo = Corretor(linhas, Nprocessos, Nthreads)
                # fim = time.time()
                # escreve_resultado(fim - inicio)
            else:
                print("Número Inválido de Threads e Processos")
else:
    print("Valores Insuficientes de entrada")
