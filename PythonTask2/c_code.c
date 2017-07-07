#include <stdio.h>
#include <stdlib.h>
#include "c_code.h"

const char * ReadData(const char * file_name)
{
    FILE * file_hdl = fopen(file_name, "r");

    char * file_content = NULL;
    int file_size = 0;

    if(file_hdl) 
    {
        fseek(file_hdl, 0, SEEK_END);
        file_size = ftell(file_hdl);
        rewind(file_hdl);

        file_content = (char*) malloc(sizeof(char) * file_size);
        fread(file_content, 1, file_size, file_hdl);
    }

    fclose(file_hdl);

    return file_content;
}

