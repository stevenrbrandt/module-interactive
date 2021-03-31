export module clangw;
export import <cstddef>;
export import <iostream>;
export import <string>;
export {

double zero(int);

double *get_double(const char *seg,const char *name,int size,double(*func)(int)=zero);

void mem_remove(const char *seg);

#include "Seg.hpp"
}
