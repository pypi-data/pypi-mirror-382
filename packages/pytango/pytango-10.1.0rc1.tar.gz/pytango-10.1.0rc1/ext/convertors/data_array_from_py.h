/*
 * SPDX-FileCopyrightText: All Contributors to the PyTango project
 *
 * SPDX-License-Identifier: LGPL-3.0-or-later
 */

// This header file is just some template functions moved apart from
// attribute.cpp, and should only be included there.

#pragma once

#include "types_structs_macros.h"
#include "convertors/generic_from_py.h"

// cppTango "feature": commands expect, that we allocate memory with "allocbuf", while attributes - new[].
// So.....

enum MemoryAllocation {
    ALLOC,
    NEW
};

#define MEMORY_ALLOCATOR(TangoScalarType, TangoArrayType, len, allocation)  \
    TangoScalarType *tg_data;                                               \
    switch(allocation) {                                                    \
    case MemoryAllocation::ALLOC:                                           \
        tg_data = TangoArrayType::allocbuf(static_cast<_CORBA_ULong>(len)); \
        break;                                                              \
    case MemoryAllocation::NEW:                                             \
        tg_data = new TangoScalarType[len];                                 \
        break;                                                              \
    default:                                                                \
        throw std::invalid_argument("Unknown allocation method");           \
    }

template <int tangoArrayTypeConst>
inline void buffer_deleter__(typename TANGO_const2scalartype(tangoArrayTypeConst) * tg_data,
                             MemoryAllocation allocation,
                             [[maybe_unused]] unsigned long processed_elements) {
    using TangoArrayType = typename TANGO_const2type(tangoArrayTypeConst);

    switch(allocation) {
    case MemoryAllocation::ALLOC:
        TangoArrayType::freebuf(tg_data);
        break;
    case MemoryAllocation::NEW:
        delete[] tg_data;
        break;
    default:
        throw std::invalid_argument("Unknown allocation method");
    }
}

template <>
inline void buffer_deleter__<Tango::DEVVAR_STRINGARRAY>(Tango::DevString *tg_data,
                                                        MemoryAllocation allocation,
                                                        unsigned long processed_elements) {
    switch(allocation) {
    case MemoryAllocation::ALLOC:
        Tango::DevVarStringArray::freebuf(tg_data);
        break;
    case MemoryAllocation::NEW: {
        for(unsigned long i = 0; i < processed_elements; ++i) {
            delete[] tg_data[i];
        }
        delete[] tg_data;
        break;
    }
    default:
        throw std::invalid_argument("Unknown allocation method");
    }
}

template <int tangoArrayTypeConst>
    inline typename TANGO_const2scalartype(tangoArrayTypeConst) * python_to_cpp_buffer_generic(py::object &py_val,
                                                                                               MemoryAllocation allocation,
                                                                                               const std::string &fname,
                                                                                               bool isImage,
                                                                                               unsigned long &res_dim_x,
                                                                                               unsigned long &res_dim_y) {
    using TangoScalarType = typename TANGO_const2scalartype(tangoArrayTypeConst);
    using TangoArrayType = typename TANGO_const2type(tangoArrayTypeConst);

    std::string err_msg = isImage
                              ? "Expecting a sequence of sequences (IMAGE attribute)."
                              : "Expecting a sequence (SPECTRUM attribute).";

    if(py::isinstance<py::str>(py_val) || !py::isinstance<py::sequence>(py_val)) {
        Tango::Except::throw_exception("PyDs_WrongParameters",
                                       err_msg,
                                       fname + "()");
    }

    py::list py_list = py::cast<py::list>(py_val);
    unsigned long len = py::len(py_val);

    if(isImage) {
        py::object py_row0 = py_list[0];
        if(!py::isinstance<py::sequence>(py_row0)) {
            Tango::Except::throw_exception("PyDs_WrongParameters",
                                           err_msg,
                                           fname + "()");
        }

        res_dim_y = len;
        res_dim_x = py::len(py_row0);
        len = res_dim_x * res_dim_y;
    } else {
        res_dim_y = 0;
        res_dim_x = len;
    }

    /// @bug Why not TangoArrayType::allocbuf(len)? Because
    /// I will use it in set_value(tg_ptr,...,release=true).
    /// Tango API makes delete[] tg_ptr instead of freebuf(tg_ptr).
    /// This is usually the same, but for Tango::DevStringArray the
    /// behaviour seems different and causes weird troubles..

    MEMORY_ALLOCATOR(TangoScalarType, TangoArrayType, len, allocation);

    TangoScalarType tg_scalar;
    unsigned long idx = 0;
    try {
        if(isImage) {
            for(unsigned long y = 0; y < res_dim_y; y++) {
                py::list py_row = py_list[y];
                for(unsigned long x = 0; x < res_dim_x; x++) {
                    array_element_from_py<tangoArrayTypeConst>::convert(py_row[x], tg_scalar);
                    tg_data[idx] = tg_scalar;
                    idx++;
                }
            }
        } else {
            for(unsigned long x = 0; x < res_dim_x; x++) {
                array_element_from_py<tangoArrayTypeConst>::convert(py_list[x], tg_scalar);
                tg_data[idx] = tg_scalar;
                idx++;
            }
        }
    } catch(...) {
        buffer_deleter__<tangoArrayTypeConst>(tg_data, allocation, idx);
        throw;
    }
    return tg_data;
}

template <int tangoArrayTypeConst>
    inline typename TANGO_const2scalartype(tangoArrayTypeConst) * python_to_cpp_buffer(py::object &py_val,
                                                                                       MemoryAllocation allocation,
                                                                                       const std::string &fname,
                                                                                       bool isImage,
                                                                                       unsigned long &res_dim_x,
                                                                                       unsigned long &res_dim_y) {
    using TangoArrayType = typename TANGO_const2type(tangoArrayTypeConst);
    using TangoScalarType = typename TANGO_const2scalartype(tangoArrayTypeConst);

    if(!py::isinstance<py::array>(py_val)) {
        return python_to_cpp_buffer_generic<tangoArrayTypeConst>(py_val,
                                                                 allocation,
                                                                 fname,
                                                                 isImage,
                                                                 res_dim_x,
                                                                 res_dim_y);
    }

    py::array arr = py_val.cast<py::array>();
    long nd = arr.ndim();
    const unsigned long *dims = reinterpret_cast<const unsigned long *>(arr.shape());
    unsigned long len = 0;

    // Retrieve the NumPy array flags
    int flags = arr.flags();

    // Check if the array is exactly what we need: contiguous, aligned, and correct data type
    const bool exact_array = ((flags & NPY_ARRAY_C_CONTIGUOUS) != 0) &&
                             ((flags & NPY_ARRAY_ALIGNED) != 0) &&
                             arr.dtype().is(pybind11::dtype::of<TangoScalarType>());

    if(isImage) {
        if(nd != 2) {
            Tango::Except::throw_exception("PyDs_WrongNumpyArrayDimensions",
                                           "Expecting a sequence of sequences (IMAGE attribute).",
                                           fname + "()");
        }

        len = dims[0] * dims[1];
        res_dim_x = dims[1];
        res_dim_y = dims[0];

    } else {
        if(nd != 1) {
            Tango::Except::throw_exception("PyDs_WrongNumpyArrayDimensions",
                                           "Expecting a sequence (SPECTRUM attribute).",
                                           fname + "()");
        }
        len = dims[0];
        res_dim_x = dims[0];
    }

    MEMORY_ALLOCATOR(TangoScalarType, TangoArrayType, len, allocation);

    if(exact_array) {
        memcpy(tg_data, arr.data(), len * sizeof(TangoScalarType));
    } else {
        try {
            py::array_t<TangoScalarType, py::array::c_style | py::array::forcecast> arr_casted(arr);

            unsigned long processed_elements = static_cast<unsigned long>(arr_casted.size());
            if(processed_elements < len) {
                buffer_deleter__<tangoArrayTypeConst>(tg_data, allocation, processed_elements);
                throw py::value_error("Array size is smaller than expected.");
            }

            memcpy(tg_data, arr_casted.data(), len * sizeof(TangoScalarType));
        } catch(const py::error_already_set &) {
            buffer_deleter__<tangoArrayTypeConst>(tg_data, allocation, 0);
            throw;
        }
    }

    return tg_data;
}

template <>
    inline TANGO_const2scalartype(Tango::DEVVAR_STRINGARRAY) *
    python_to_cpp_buffer<Tango::DEVVAR_STRINGARRAY>(py::object &py_val,
                                                    MemoryAllocation allocation,
                                                    const std::string &fname,
                                                    bool isImage,
                                                    unsigned long &res_dim_x,
                                                    unsigned long &res_dim_y) {
    return python_to_cpp_buffer_generic<Tango::DEVVAR_STRINGARRAY>(py_val,
                                                                   allocation,
                                                                   fname,
                                                                   isImage,
                                                                   res_dim_x,
                                                                   res_dim_y);
}

template <int tangoArrayTypeConst>
    inline typename TANGO_const2type(tangoArrayTypeConst) * fast_convert2array(py::object py_value) {
    using TangoScalarType = typename TANGO_const2scalartype(tangoArrayTypeConst);
    using TangoArrayType = typename TANGO_const2type(tangoArrayTypeConst);

    unsigned long res_dim_x, res_dim_y;

    TangoScalarType *array = python_to_cpp_buffer<tangoArrayTypeConst>(py_value,
                                                                       MemoryAllocation ::ALLOC,
                                                                       "array_python_data_to_cpp",
                                                                       false,
                                                                       res_dim_x,
                                                                       res_dim_y);

    try {
        // not a bug: res_dim_y means nothing to us, we are unidimensional
        // here we have max_len and current_len = res_dim_x
        return new TangoArrayType(static_cast<_CORBA_ULong>(res_dim_x),
                                  static_cast<_CORBA_ULong>(res_dim_x),
                                  array,
                                  true);
    } catch(...) {
        TangoArrayType::freebuf(array);
        throw;
    }
}

template <>
    inline TANGO_const2type(Tango::DEVVAR_LONGSTRINGARRAY) * fast_convert2array<Tango::DEVVAR_LONGSTRINGARRAY>(py::object py_value) {
    py::object py_long, py_str;

    __long_double_string_array_helper(py_value,
                                      DevVarNumericStringArray::LONG_STRING,
                                      "fast_convert2array()",
                                      py_long,
                                      py_str);

    std::unique_ptr<Tango::DevVarLongArray> a_long(fast_convert2array<Tango::DEVVAR_LONGARRAY>(py_long));
    std::unique_ptr<Tango::DevVarStringArray> a_str(fast_convert2array<Tango::DEVVAR_STRINGARRAY>(py_str));
    std::unique_ptr<Tango::DevVarLongStringArray> result(new Tango::DevVarLongStringArray());

    result->lvalue = *a_long;
    result->svalue = *a_str;

    return result.release();
}

template <>
    inline TANGO_const2type(Tango::DEVVAR_DOUBLESTRINGARRAY) * fast_convert2array<Tango::DEVVAR_DOUBLESTRINGARRAY>(py::object py_value) {
    py::object py_double, py_str;

    __long_double_string_array_helper(py_value,
                                      DevVarNumericStringArray::LONG_STRING,
                                      "fast_convert2array()",
                                      py_double,
                                      py_str);

    std::unique_ptr<Tango::DevVarDoubleArray> a_double(fast_convert2array<Tango::DEVVAR_DOUBLEARRAY>(py_double));
    std::unique_ptr<Tango::DevVarStringArray> a_str(fast_convert2array<Tango::DEVVAR_STRINGARRAY>(py_str));
    std::unique_ptr<Tango::DevVarDoubleStringArray> result(new Tango::DevVarDoubleStringArray());

    result->dvalue = *a_double;
    result->svalue = *a_str;

    return result.release();
}
