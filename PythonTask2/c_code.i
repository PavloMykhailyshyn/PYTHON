%module c_code
%{
#define SWIG_FILE_WITH_INIT
#include "c_code.h"
%}

const char * ReadData(const char *);
