#include "tbcrypto/pywrap.h"

#include "tbcrypto/const.h"
#include "tbcrypto/cuid.h"
#include "tbcrypto/error.h"
#include "tbcrypto/rc442.h"
#include "tbcrypto/sign.h"
#include "tbcrypto/bb64.h"

PyObject* cuid_galaxy2(PyObject* Py_UNUSED(self), PyObject* args) {
    unsigned char dst[TBC_CUID_GALAXY2_SIZE];
    const unsigned char* androidID;
    Py_ssize_t androidIDSize;

    if (!PyArg_ParseTuple(args, "s#", &androidID, &androidIDSize)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse args");
        return NULL;
    }

    if (androidIDSize != 16) {
        PyErr_Format(PyExc_ValueError, "Invalid size of android_id. Expect 16, got %zu", androidIDSize);
        return NULL;
    }

    tbc_cuid_galaxy2(androidID, dst);

    return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBC_CUID_GALAXY2_SIZE);
}

PyObject* c3_aid(PyObject* Py_UNUSED(self), PyObject* args) {
    unsigned char dst[TBC_C3_AID_SIZE];
    const unsigned char* androidID;
    Py_ssize_t androidIDSize;
    const unsigned char* uuid;
    Py_ssize_t uuidSize;

    if (!PyArg_ParseTuple(args, "s#s#", &androidID, &androidIDSize, &uuid, &uuidSize)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse args");
        return NULL;
    }

    if (androidIDSize != 16) {
        PyErr_Format(PyExc_ValueError, "Invalid size of android_id. Expect 16, got %zu", androidIDSize);
        return NULL;
    }
    if (uuidSize != 36) {
        PyErr_Format(PyExc_ValueError, "Invalid size of uuid. Expect 36, got %zu", androidIDSize);
        return NULL;
    }

    tbc_c3_aid(androidID, uuid, dst);

    return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBC_C3_AID_SIZE);
}

PyObject* rc4_42(PyObject* Py_UNUSED(self), PyObject* args) {
    unsigned char dst[TBC_RC4_SIZE];
    const unsigned char* xyusMd5Str;
    Py_ssize_t xyusMd5Size;
    const unsigned char* cbcSecKey;
    Py_ssize_t cbcSecKeySize;

    if (!PyArg_ParseTuple(args, "s#y#", &xyusMd5Str, &xyusMd5Size, &cbcSecKey, &cbcSecKeySize)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse args");
        return NULL;
    }

    if (xyusMd5Size != 32) {
        PyErr_Format(PyExc_ValueError, "Invalid size of xyus_md5. Expect 32, got %zu", xyusMd5Size);
        return NULL;
    }
    if (cbcSecKeySize != 16) {
        PyErr_Format(PyExc_ValueError, "Invalid size of cbc_sec_key. Expect 16, got %zu", cbcSecKeySize);
        return NULL;
    }

    tbc_rc4_42(xyusMd5Str, cbcSecKey, dst);

    return PyBytes_FromStringAndSize((char*)dst, TBC_RC4_SIZE);
}

PyObject* enuid(PyObject* Py_UNUSED(self), PyObject* args)
{
    unsigned char dst[TBC_ENUID_SIZE + 1];  // str ends with '\0'
    const unsigned char* cuid2;
    Py_ssize_t cuid2Size;

    if (!PyArg_ParseTuple(args, "s#", &cuid2, &cuid2Size)) {
        PyErr_SetString(PyExc_TypeError, "Failed to parse args");
        return NULL;
    }

    if (cuid2Size != TBC_CUID_GALAXY2_SIZE) {
        PyErr_Format(PyExc_ValueError, "Invalid size of cuid_galaxy2. Expect %zu, got %zu", TBC_CUID_GALAXY2_SIZE, cuid2Size);
        return NULL;
    }

    tbc_BB64Encode(cuid2, cuid2Size, 0, dst);

    return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, dst, TBC_ENUID_SIZE);
}



static PyMethodDef crypto_methods[] = {
    {"cuid_galaxy2", (PyCFunction)cuid_galaxy2, METH_VARARGS, NULL},
    {"c3_aid", (PyCFunction)c3_aid, METH_VARARGS, NULL},
    {"rc4_42", (PyCFunction)rc4_42, METH_VARARGS, NULL},
    {"sign", (PyCFunction)sign, METH_VARARGS, NULL},
    {"enuid", (PyCFunction)enuid, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL},
};

static PyModuleDef crypto_module = {PyModuleDef_HEAD_INIT, "crypto", NULL, -1, crypto_methods};

PyMODINIT_FUNC PyInit_crypto(void) {
    PyObject* mod = PyModule_Create(&crypto_module);
    if (mod == NULL) {
        return NULL;
    }

#ifdef Py_GIL_DISABLED
    PyUnstable_Module_SetGIL(mod, Py_MOD_GIL_NOT_USED);
#endif

    return mod;
}
