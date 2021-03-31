import <iostream>;
import <string>;
import <memory>;
import <mutex>;
import <map>;
import <functional>;
#define module module__
#define import import__
#include <Python.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#undef module
#undef import
#include "Seg.hpp"

namespace py = pybind11;

struct Array_ptr {
    Array<double> *ptr;
    Array_ptr() : ptr(nullptr) {}
    Array_ptr(Array<double> *a) : ptr(a) {}
    ~Array_ptr() {}
    Array<double> *operator->() {
        return ptr;
    }
};

PYBIND11_MODULE(clangw, m) {
    py::class_<Array_ptr>(m, "Array", py::buffer_protocol())
        .def_buffer([](Array_ptr& a) -> py::buffer_info {
            return py::buffer_info(
                a->begin(),
                sizeof(double),
                py::format_descriptor<double>::format(),
                1,
                { a->size() },
                { sizeof(double) }
        );
    });
    m.def("allocate_array", [](const std::string& seg_name, const std::string& mem_name,size_t size)->Array_ptr {
        Seg seg(seg_name.c_str());
        Array_ptr mem(seg.allocate_array<double>(mem_name.c_str(), size));
        return std::move(mem);
    });
}
