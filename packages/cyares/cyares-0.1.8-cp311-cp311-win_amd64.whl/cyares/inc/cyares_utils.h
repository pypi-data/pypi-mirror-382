/* 
Using this implementation did not feel wrong at all.
This source code utilizes some of msgspec's implementations for dealing with
buffer extraction of unicode characters into a python buffer...

- Some functions and macros were re-named for the sake of being convienient.

- (
cyares_copy_memory, 
cyares_unicode_from_uchar, 
cyares_unicode_from_uchar_and_size
cyares_htons
cyares_htonl
) is not apart of msgspec but is written by us...

*/

/* 
Copyright (c) 2021, Jim Crist-Harif
All rights reserved.

Redistribution and use in source and binary forcyares, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
  may be used to endorse or promote products derived from this software
  without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


*/

#ifndef __CYARES_UTILS_H__
#define __CYARES_UTILS_H__

#include <string.h>

#include <Python.h>

#ifdef __cplusplus 
extern "C" {
#endif


#ifdef __GNUC__
#define CYARES_LIKELY(pred) __builtin_expect(!!(pred), 1)
#define CYARES_UNLIKELY(pred) __builtin_expect(!!(pred), 0)
#else
#define CYARES_LIKELY(pred) (pred)
#define CYARES_UNLIKELY(pred) (pred)
#endif

#ifdef __GNUC__
#define CYARES_INLINE __attribute__((always_inline)) inline
#define CYARES_NOINLINE __attribute__((noinline))
#elif ((_WIN32) || (_MSVC_VER))
#define CYARES_INLINE __forceinline
#define CYARES_NOINLINE __declspec(noinline)
#else
#define CYARES_INLINE inline
#define CYARES_NOINLINE
#endif

/* msgspec Note: XXX: Optimized `PyUnicode_AsUTF8AndSize` for strs that we know have
 * a cached unicode representation. */
static inline const char *
cyares_unicode_str_and_size_nocheck(PyObject *str, Py_ssize_t *size) {
    if (CYARES_LIKELY(PyUnicode_IS_COMPACT_ASCII(str))) {
        *size = ((PyASCIIObject *)str)->length;
        return (char *)(((PyASCIIObject *)str) + 1);
    }
    *size = ((PyCompactUnicodeObject *)str)->utf8_length;
    return ((PyCompactUnicodeObject *)str)->utf8;
}

/* Msgspec NOTE: XXX: Optimized `PyUnicode_AsUTF8AndSize` */
static inline const char *
cyares_unicode_str_and_size(PyObject *str, Py_ssize_t *size) {
    const char *out = cyares_unicode_str_and_size_nocheck(str, size);
    if (CYARES_LIKELY(out != NULL)) return out;
    return PyUnicode_AsUTF8AndSize(str, size);
}



/* Fill in view.buf & view.len from either a Unicode or buffer-compatible
 * object. */
static int
cyares_get_buffer(PyObject *obj, Py_buffer *view) {
    if (CYARES_UNLIKELY(PyUnicode_CheckExact(obj))) {
        view->buf = (void *)cyares_unicode_str_and_size(obj, &(view->len));
        if (view->buf == NULL) return -1;
        Py_INCREF(obj);
        view->obj = obj;
        return 0;
    }
    return PyObject_GetBuffer(obj, view, PyBUF_CONTIG_RO);
}

static void
cyares_release_buffer(Py_buffer *view) {
    if (CYARES_LIKELY(!PyUnicode_CheckExact(view->obj))) {
        PyBuffer_Release(view);
    }
    else {
        Py_CLEAR(view->obj);
    }
}



static inline PyObject* 
cyares_unicode_from_uchar_and_size(
    const uint8_t* chars, Py_ssize_t size
){
    return PyUnicode_FromKindAndData(
        PyUnicode_1BYTE_KIND, (void*)chars, size
    );
}

static inline PyObject* 
cyares_unicode_from_uchar(
    const uint8_t* chars
){
    return PyUnicode_FromKindAndData(
        PyUnicode_1BYTE_KIND,
        (void*)chars,
        strlen((char*)chars)
    );
}




static int cyares_copy_memory(char** ptr_to, PyObject* ptr_from){
    Py_buffer view;
    if (cyares_get_buffer(ptr_from, &view) < 0) {
        return -1;
    }


    char* s = (char*)PyMem_Malloc(sizeof(char) * view.len);
    if (s == NULL){
        PyErr_NoMemory();
        return -1;
    }
    
    memcpy(s, ptr_from, sizeof(char) * view.len);
    *ptr_to = s;

    cyares_release_buffer(&view);
    return 0;
}

/* To give some more performance benefits to cy-ares (which should be included globally accross all c-ares supported platforms)
    redefinitions of htons and htonl is used...
*/


#define cyares_htons htons
#define cyares_htonl htonl


#ifdef __cplusplus 
}
#endif


#endif // __CYARES_UTILS_H__