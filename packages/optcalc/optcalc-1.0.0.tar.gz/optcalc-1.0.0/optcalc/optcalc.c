#include <Python.h>
#include <numpy/arrayobject.h>
#include "calc.h"

// extern så vi kan kolla om data genererats
extern bool getGeneratedFlag(void);

// --- getCallArr ---
static PyObject* py_getCallArr(PyObject* self, PyObject* args) {
    if (!getGeneratedFlag()) {
        PyErr_SetString(PyExc_RuntimeError,
            "Option data not generated yet. Call genOptionSer() first.");
        return NULL;
    }

    int n = getMaturity();
    double* arr = getCallArr();

    // Skapa NumPy-array som pekar på C-minnet
    npy_intp dims[1] = { n };
    PyObject* np_array = PyArray_SimpleNewFromData(1, dims, NPY_DOUBLE, arr);

    // Kopiera datan så NumPy äger sin egen kopia (säkrare)
    PyObject* np_copy = PyArray_NewCopy((PyArrayObject*)np_array, NPY_ANYORDER);
    Py_DECREF(np_array);

    return np_copy;
}

// --- getPutArr ---
static PyObject* py_getPutArr(PyObject* self, PyObject* args) {
    if (!getGeneratedFlag()) {
        PyErr_SetString(PyExc_RuntimeError,
            "Option data not generated yet. Call genOptionSer() first.");
        return NULL;
    }

    int n = getMaturity();
    double* arr = getPutArr();

    npy_intp dims[1] = { n };
    PyObject* np_array = PyArray_SimpleNewFromData(1, dims, NPY_DOUBLE, arr);

    PyObject* np_copy = PyArray_NewCopy((PyArrayObject*)np_array, NPY_ANYORDER);
    Py_DECREF(np_array);

    return np_copy;
}

// --- setParams ---
static PyObject* py_setParams(PyObject* self, PyObject* args) {
    double asset, strike, volatility, interest;
    int time;

    if (!PyArg_ParseTuple(args, "ddidd", &asset, &strike, &time, &volatility, &interest))
        return NULL;

    set_params(asset, strike, time, volatility, interest);
    Py_RETURN_NONE;
}

// --- genOptionSer ---
static PyObject* py_genOptionSer(PyObject* self, PyObject* args) {
    genOptionSer();
    Py_RETURN_NONE;
}

// info
static PyObject* py_getInfo(PyObject* self, PyObject* args) {
    const char* info = getInfo();
    return Py_BuildValue("s", info);
}




// --- clean ---
static PyObject* py_clean(PyObject* self, PyObject* args) {
    clean();
    Py_RETURN_NONE;
}

// --- Cleanup-funktion ---
static void optcalc_free(void* m) {
    clean();
}

// --- Metodtabell ---
static PyMethodDef Methods[] = {
    {"set_params",  py_setParams,  METH_VARARGS, "Set option parameters"},
    {"genOptionSer", py_genOptionSer, METH_NOARGS, "Generate option series"},
    {"getCallArr",  py_getCallArr, METH_NOARGS, "Return call option prices"},
    {"getPutArr",   py_getPutArr,  METH_NOARGS, "Return put option prices"},
    {"clean",       py_clean,      METH_NOARGS, "Free allocated arrays"},
    {"getInfo", py_getInfo, METH_NOARGS, "Return general information about the Black–Scholes model."},

    {NULL, NULL, 0, NULL}
};

// --- Moduldefinition ---
static struct PyModuleDef OptCalcModule = {
    PyModuleDef_HEAD_INIT,
    "optcalc",
    "Black-Scholes option calculator",
    -1,
    Methods,
    NULL, NULL, NULL,
    optcalc_free
};

// --- Init-funktion ---
PyMODINIT_FUNC PyInit_optcalc(void) {
    import_array();  // <-- aktiverar NumPy C API
    return PyModule_Create(&OptCalcModule);
}
