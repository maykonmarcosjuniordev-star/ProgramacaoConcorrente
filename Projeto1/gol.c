/*
 * The Game of Life
 *
 * RULES:
 *  1. A cell is born, if it has exactly three neighbours.
 *  2. A cell dies of loneliness,
 *     if it has less than two neighbours.
 *  3. A cell dies of overcrowding,
 *     if it has more than three neighbours.
 *  4. A cell survives to the next generation,
 *     if it does not die of lonelines or overcrowding.
 *
 * In this version, a 2D array of ints is used.
 * A 1 cell is on, a 0 cell is off.
 * The game plays a number of steps (given by the input),
 * printing to the screen each time.
 * A 'x' printed means on, space means off.
 *
 */

#include <stdlib.h>
#include "gol.h"

cell_t **allocate_board(int size) {
    cell_t **dummyboard = (cell_t **)malloc(sizeof(cell_t *) * (size+2));
    cell_t **board = dummyboard[1];
    for (int i = 1; i <= size; i++)
    {
        dummyboard[i] = (cell_t *)malloc(sizeof(cell_t) * (size+2));
        board[i-1] = dummyboard[i][1];
    }
    dummyboard[0] = (cell_t *)malloc(sizeof(cell_t) * (size+2));
    dummyboard[size+1] = (cell_t *)malloc(sizeof(cell_t) * (size+2));

    return board;
}

void free_board(cell_t **board, int size) {
    for (int i = -1; i <= size; i++) {
        free(board[i]);
    }
    free(board);
}

int adjacent_to(cell_t **board, int size, int i, int j) {
    int count = 0;

    int sk = i - (i > 0);
    int ek = i + (i + 1 < size);
    int sl = j - (j > 0);
    int el = j + (j + 1 < size);

    for (int k = sk; k <= ek; k++) {
        for (int l = sl; l <= el; l++) {
            count += board[k][l];
        }
    }
    count -= board[i][j];

    return count;
}

// alterada para receber o slice que cada thread vai usar
void play(cell_t **board, cell_t **newboard,
             int size, int linhaI, int linhaF,
             int colunaI, int colunaF, int vet[11]) {
    // for each cell, apply the rules of Life
    for (int i = linhaI; i < linhaF; i++) {
        int end = size + (colunaF - size)*(i == (linhaF - 1));
        int j = colunaI;
        for (; j < end; j++) {
            int a = adjacent_to(board, size, i, j);
            // if cell is alive
            if(board[i][j]) {
                // death: loneliness
                if(a < 2) {
                    newboard[i][j] = 0;
                    vet[2]++;
                } else if (a > 3) {
                    // death: overcrowding
                    newboard[i][j] = 0;
                    vet[6]++;
                } else {
                    // survival
                    newboard[i][j] = 1;
                    vet[4]++;
                    }
            } else {
                // if cell is dead
                if(a == 3) { 
                    // new born
                    newboard[i][j] = 1;
                    vet[1]++;
                } else {
                    // stay unchanged
                    newboard[i][j] = 0;
                }
            }
        }
        colunaI = 0;
    }
}

void print_board(cell_t **board, int size) {
    // for each row
    for (int j = 0; j < size; j++) {
        // print each column position...
        for (int i = 0; i < size; i++) {
            printf("%c", board[i][j] ? 'x' : ' ');
        }
        // followed by a carriage return
        printf("\n");
    }
}

void print_stats(stats_t stats) {
    // print final statistics
    printf("Statistics:\n\tBorns..............: "
            "%u\n\tSurvivals..........: "
            "%u\n\tLoneliness deaths..: "
            "%u\n\tOvercrowding deaths: %u\n\n",
            stats.borns, stats.survivals,
            stats.loneliness, stats.overcrowding);
}

void read_file(FILE *f, cell_t **board, int size) {
    char *s = (char *) malloc(size + 10);

    // read the first new line (it will be ignored)
    fgets(s, size + 10, f);

    // read the life board 
    for (int j = 0; j < size; j++) {
        // get a string
        fgets(s, size + 10, f);
        board[j][-1] = 0;
        board[j][size] = 0;

        // copy the string to the life board
        for (int i = 0; i < size; i++) {
            board[i][j] = (s[i] == 'x');
        }
    }

    free(s);
}
