import <iostream>;
import <string>;
import <memory>;
import <mutex>;
import <map>;
import <functional>;
#include <boost/interprocess/managed_shared_memory.hpp>
#include "Seg.hpp"
using namespace boost::interprocess;
        
void mem_remove(const char *seg) {
    shared_memory_object::remove(seg); 
}

double zero(int i) { return 0; }

std::map<std::string, managed_shared_memory *> mem_map;

double *get_double(const char *segment_name, const char *name, int size,double (*func)(int)) {
    if(mem_map.find(segment_name) == mem_map.end())
        mem_map[segment_name] = new managed_shared_memory(open_or_create, "MySharedMemory", 65536);
    managed_shared_memory *segment = mem_map[segment_name];
    auto result = segment->find<double>(name);
    if(result.first) {
	std::cout << "Return existing" << std::endl;
        return result.first;
    } else {
	std::cout << "Return new" << std::endl;
        double *d = segment->construct<double>(name)[size](0.0);
        if(func != nullptr)
            for(int i=0;i<size;i++)
                d[i] = func(i);
        return d;
    }
} 

Seg::Seg(const char *segment_name, size_t size) {
    seg = segment_name;
    if(mem_map.find(segment_name) == mem_map.end())
        mem_map[segment_name] = new managed_shared_memory(open_or_create, segment_name, size);
    managed_data = mem_map[segment_name];
}

void *Seg::allocate_(const char *name, size_t size,bool& init) {
    managed_shared_memory *segment = (managed_shared_memory*)managed_data;
    auto result = segment->find<size_t>(name);
    if(result.first) {
        init = false;
        return result.first;
    } else {
        init = true;
        return segment->construct<size_t>(name)[size]('\0');
    }
} 

void Seg::remove_(void *data) {
    managed_shared_memory *segment = (managed_shared_memory*)managed_data;
    segment->destroy_ptr(data);
}

void Seg::remove() {
    shared_memory_object::remove(seg); 
}
