// Copyright (c) 2010-2025 The Regents of the University of Michigan
// This file is from the freud project, released under the BSD 3-Clause License.

#ifndef EXPORT_MANAGED_ARRAY_H
#define EXPORT_MANAGED_ARRAY_H

#include "ManagedArray.h"
#include "VectorMath.h"

#include <cstddef>
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <string>
#include <vector>

namespace freud { namespace util {

namespace wrap {

template<typename T> struct ManagedArrayWrapper
{
    static nanobind::ndarray<nanobind::numpy, const T> toNumpyArray(nanobind::object self)
    {
        ManagedArray<T>* self_cpp = nanobind::cast<ManagedArray<T>*>(self);
        auto dims = self_cpp->shape();
        auto ndim = dims.size();
        auto data_ptr = self_cpp->data();
        return nanobind::ndarray<nanobind::numpy, const T>((void*) data_ptr, ndim, &dims[0], self);
    }
};

/* Need to alter array dimensions when returning an array of vec3*/
template<typename T> struct ManagedArrayWrapper<vec3<T>>
{
    static nanobind::ndarray<nanobind::numpy, const T> toNumpyArray(nanobind::object self)
    {
        ManagedArray<vec3<T>>* self_cpp = nanobind::cast<ManagedArray<vec3<T>>*>(self);

        // get array data like before
        auto dims = self_cpp->shape();
        auto Ndim = dims.size();
        auto data_ptr = self_cpp->data();

        // update the dimensions so it gets exposed to python the right way
        std::vector<size_t> new_dims(dims.begin(), dims.end());
        new_dims.push_back(3);
        auto ndim = Ndim + 1;

        // now return the array
        return nanobind::ndarray<nanobind::numpy, const T>((void*) data_ptr, ndim, new_dims.data(), self);
    }
};

}; // namespace wrap

namespace detail {

template<typename T> void export_ManagedArray(nanobind::module_& module, const std::string& name)
{
    nanobind::class_<ManagedArray<T>>(module, name.c_str())
        .def("toNumpyArray", &wrap::ManagedArrayWrapper<T>::toNumpyArray);
}

}; // namespace detail

}; }; // namespace freud::util

#endif
