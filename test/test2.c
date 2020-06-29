#include <stdio.h>
#include <string.h>
#include <unistd.h>

char target1[8] = "EDITME1\0";
char target2[8] = "EDITME2\0";

int main(){
    char buffer[1024];
    memset(buffer, 0, 1024);
    read(0, buffer, 1024);
    printf(buffer);

    puts("\n----------\n");
    printf("%s\n", target1);
    printf("%s\n", target2);
}

