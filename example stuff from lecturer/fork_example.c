#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/*
 * Demonstrates the effects of fork.
 * The lecture includes the Python version of this.
 */
int main(int argc, char** argv) {

    int i = 0;
    while (i < 2) {
        fork();
        system("ps -o pid,ppid,comm,stat");
        i++;
    }
    return (EXIT_SUCCESS);
}
