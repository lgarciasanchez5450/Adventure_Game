#define PY_SSIZE_T_CLEAN
#include <C:\Users\Leo\AppData\Local\Programs\Python\Python310\include\Python.h> // TO_BE_CHANGED
#include <math.h>
#include <stdbool.h>
#define PI 3.14159265358979
//LCG 

unsigned int m, a, c;
m = 0;
a = 0;
c = 0;
unsigned int lcg_state;
static PyObject* lcg_set_seed(PyObject* self, PyObject* arg) {
    unsigned int seed;
    if (!PyArg_Parse(arg,"I",&seed)) {
        return NULL;
    }
    lcg_state = seed;
    Py_RETURN_NONE;
}
static PyObject* lcg_set_m(PyObject* self, PyObject* arg) {
    signed int new_m;
    if (!PyArg_Parse(arg,"I",&new_m)) {
        return NULL;
    }
    m = new_m;
    Py_RETURN_NONE;
}
static PyObject* lcg_set_a(PyObject* self, PyObject* arg) {
    signed int new_a;
    if (!PyArg_Parse(arg,"I",&new_a)) {
        return NULL;
    }
    a = new_a;
    Py_RETURN_NONE;
}
static PyObject* lcg_set_c(PyObject* self, PyObject* arg) {
    signed int new_c;
    if (!PyArg_Parse(arg,"I",&new_c)) {
        return NULL;
    }
    c = new_c;
    Py_RETURN_NONE;
}
static PyObject* lcg(PyObject* self, PyObject* Py_UNUSED(arg) ){
    lcg_state = (a*lcg_state + c) % m;
    return Py_BuildValue("I",lcg_state);
}
static PyObject* lcg_normalized(PyObject* self, PyObject* Py_UNUSED(arg) ){
    lcg_state = (a*lcg_state + c) % m;
    return Py_BuildValue("d",(double)lcg_state/((double) m));
}

//PCG

unsigned int pcg_state;
static PyObject* pcg_set_seed(PyObject* self, PyObject* arg) {
    unsigned int seed;
    if (!PyArg_Parse(arg,"I",&seed)) {
        return NULL;
    }
    pcg_state = seed;
    Py_RETURN_NONE;
}
static PyObject* pcg(PyObject* self, PyObject* Py_UNUSED(arg)) {
    pcg_state = pcg_state * 747796405 + 2891336453;
    unsigned int result = ((pcg_state >> ((pcg_state >> 28) + 4)) ^ pcg_state) * 277803737;
    result = (result >> 22) ^ result;
    return Py_BuildValue("I",result);
}
static PyObject* pcg_normalized(PyObject* self, PyObject* Py_UNUSED(arg)) {
    pcg_state = pcg_state * 747796405 + 2891336453;
    unsigned int result = ((pcg_state >> ((pcg_state >> 28) + 4)) ^ pcg_state) * 277803737;
    result = (result >> 22) ^ result;
    return Py_BuildValue("d",(double)result/4294967295.0);
}
static PyObject* pcg_less_than(PyObject* self, PyObject* arg) {
    unsigned int mod;
    if (!PyArg_Parse(arg,"I",&mod)) {
        return NULL;
    }
    pcg_state = pcg_state * 747796405 + 2891336453;
    unsigned int result = ((pcg_state >> ((pcg_state >> 28) + 4)) ^ pcg_state) * 277803737;
    result = (result >> 22) ^ result;
    result = result % mod;
    return Py_BuildValue("I",result);  
}
static PyObject* pcg_unit_dist(PyObject* self, PyObject* Py_UNUSED(arg)) {
    pcg_state = pcg_state * 747796405 + 2891336453;
    unsigned int result = ((pcg_state >> ((pcg_state >> 28) + 4)) ^ pcg_state) * 277803737;
    result = (result >> 22) ^ result;
    return Py_BuildValue("d",((double)result/2147483647.0) - 1.0);
}



static PyMethodDef functions[] = {
    //"Python Name"                  C-Function Name     argument presentation      description
    //{"say_hello",                  exmod_say_hello,           METH_VARARGS,         "Say Hello from C and print message"},
    {"lcg_set_m",                   (PyCFunction) lcg_set_m,                  METH_O,                ""},
    {"lcg_set_a",                   (PyCFunction) lcg_set_a,                  METH_O,                ""},
    {"lcg_set_c",                   (PyCFunction) lcg_set_c,                  METH_O,                ""},
    {"lcg_set_seed",                (PyCFunction) lcg_set_seed,               METH_O,                ""},
    {"lcg",                         (PyCFunction) lcg,                        METH_NOARGS,           ""},
    {"lcg_normalized",              (PyCFunction) lcg_normalized,             METH_NOARGS,           ""},


    {"pcg_set_seed",                (PyCFunction) pcg_set_seed,               METH_O,                ""},
    {"pcg",                         (PyCFunction) pcg,                        METH_NOARGS,           ""},
    {"pcg_normalized",              (PyCFunction) pcg_normalized,             METH_NOARGS,           ""},
    {"pcg_less_than",               (PyCFunction) pcg_less_than,              METH_O,                ""},
    {"pcg_unit_dist",               (PyCFunction) pcg_unit_dist,              METH_NOARGS,           ""},
    


    {NULL,NULL,0,NULL}  /* Sentinel */
};
static struct PyModuleDef module = { PyModuleDef_HEAD_INIT,"rng","module docstring",-1,functions};

PyMODINIT_FUNC PyInit_rng(void) {

    return PyModule_Create(&module);
}
