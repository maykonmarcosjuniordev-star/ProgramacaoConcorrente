#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

//                          (principal)
//                               |
//              +----------------+--------------+
//              |                               |
//           filho_1                         filho_2
//              |                               |
//    +---------+-----------+          +--------+--------+
//    |         |           |          |        |        |
// neto_1_1  neto_1_2  neto_1_3     neto_2_1 neto_2_2 neto_2_3

// ~~~ printfs  ~~~
//      principal (ao finalizar): "Processo principal %d finalizado\n"
// filhos e netos (ao finalizar): "Processo %d finalizado\n"
//    filhos e netos (ao inciar): "Processo %d, filho de %d\n"

// Obs:
// - netos devem esperar 5 segundos antes de imprmir a mensagem de finalizado (e terminar)
// - pais devem esperar pelos seu descendentes diretos antes de terminar



int main(void) {

    for (int i = 0; i < 2; i++){
        pid_t filho = fork();
        if(filho == 0){//filho
            printf("Processo %d, filho de %d\n",getpid(),getppid());
            fflush(stdout);	
            for (int j = 0; j < 3; j++){
                pid_t neto = fork();
                if (neto == 0){
                    printf("Processo %d, filho de %d\n",getpid(),getppid());  	
            	    fflush(stdout);           
                    sleep(5);
                    printf("Processo %d finalizado\n", getpid());
            	    fflush(stdout);           
                    return 0;
                }
            }
            while(wait(NULL)>=0);//filhos esperam netos terminarem
            printf("Processo %d finalizado\n", getpid());
    	    fflush(stdout);          
            return 0;
        }//pai 

    }
          
    while(wait(NULL)>=0);//pais esperam filhos terminarem
    printf("Processo principal %d finalizado\n",getpid());   
    return 0;
}
