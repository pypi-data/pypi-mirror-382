#ifndef MPZ_H
#define MPZ_H

#if defined(__MINGW32__) && defined(__GNUC__)
#  pragma GCC diagnostic push
#  pragma GCC diagnostic ignored "-Warray-bounds"
#endif
#if defined(__clang__)
#  pragma GCC diagnostic push
#  pragma GCC diagnostic ignored "-Wnewline-eof" /* XXX: pypy/pypy#5312 */
#endif
/* For GraalVM: unicodeobject.h, implicit conversion changes
   signedness: 'enum PyUnicode_Kind' to 'int' */
#if defined(__GNUC__) || defined(__clang__)
#  pragma GCC diagnostic push
#  pragma GCC diagnostic ignored "-Wsign-conversion"
#endif

#include "pythoncapi_compat.h"

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#if defined(__GNUC__) || defined(__clang__)
#  pragma GCC diagnostic pop
#endif
#if defined(__clang__)
#  pragma GCC diagnostic pop
#endif
#if defined(__MINGW32__) && defined(__GNUC__)
#  pragma GCC diagnostic pop
#endif

#include "libzz/zz.h"

typedef struct {
    PyObject_HEAD
    Py_hash_t hash_cache;
    zz_t z;
} MPZ_Object;

extern PyTypeObject MPZ_Type;

#define MPZ_CheckExact(u) Py_IS_TYPE((u), &MPZ_Type)
#define MPZ_Check(u) PyObject_TypeCheck((u), &MPZ_Type)

#endif /* MPZ_H */
