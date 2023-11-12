#define PY_SSIZE_T_CLEAN 
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <C:\Users\Leo\AppData\Local\Programs\Python\Python310\include\Python.h>

// Steps 
// 1) Open Python IDLE
// 2) import numpy
// 3) Run numpy.get_include()
// 4) From there navigate to arrayobject.h
#include <C:\Users\Leo\AppData\Local\Programs\Python\Python310\Lib\site-packages\numpy\core\include\numpy\arrayobject.h> // You have to check where yours is
#include <limits.h>  // intellisense doesn't seem to think this one is necessary 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

static const int64_t PRIME_X = 0x5205402B9270C86FL;
static const int64_t PRIME_Y = 0x598CD327003817B5L;
static const int64_t HASH_MULTIPLIER = 0x53A3F72DEEC546F5L;

static const double ROOT2OVER2 = 0.7071067811865476;
static const double SKEW_2D = 0.366025403784439;
static const double UNSKEW_2D = -0.21132486540518713;
static const double ROOT3OVER3 = 0.577350269189626;
static const double FALLBACK_ROTATE3 = 2.0 / 3.0;
static const int32_t N_GRADS_2D_EXPONENT = 7;
static const int32_t N_GRADS_2D = 128;
static const double NORMALIZER_2D = 0.05481866495625118;
static const float RSQUARED_2D = 2.0f / 3.0f;
static int32_t seed = 3;

static float GRADIENTS_2D[256];

static float grad2[] = { // length is 48
        0.38268343236509f,   0.923879532511287f,
        0.923879532511287f,  0.38268343236509f,
        0.923879532511287f, -0.38268343236509f,
        0.38268343236509f,  -0.923879532511287f,
        -0.38268343236509f,  -0.923879532511287f,
        -0.923879532511287f, -0.38268343236509f,
        -0.923879532511287f,  0.38268343236509f,
        -0.38268343236509f,   0.923879532511287f,
        //-------------------------------------//
        0.130526192220052f,  0.99144486137381f,
        0.608761429008721f,  0.793353340291235f,
        0.793353340291235f,  0.608761429008721f,
        0.99144486137381f,   0.130526192220051f,
        0.99144486137381f,  -0.130526192220051f,
        0.793353340291235f, -0.60876142900872f,
        0.608761429008721f, -0.793353340291235f,
        0.130526192220052f, -0.99144486137381f,
        -0.130526192220052f, -0.99144486137381f,
        -0.608761429008721f, -0.793353340291235f,
        -0.793353340291235f, -0.608761429008721f,
        -0.99144486137381f,  -0.130526192220052f,
        -0.99144486137381f,   0.130526192220051f,
        -0.793353340291235f,  0.608761429008721f,
        -0.608761429008721f,  0.793353340291235f,
        -0.130526192220052f,  0.99144486137381f,
};

void init(void) {
    static_assert(sizeof(double)*CHAR_BIT == 64, "Unexpected double size");
    static_assert(sizeof(float)*CHAR_BIT == 32, "Unexpected float size");
    for (int i = 0; i < 48; i++) {
        grad2[i] = (float)(grad2[i] / NORMALIZER_2D);
    }
    for (int i = 0, j = 0; i < 256; i++, j++) {
        if (j == 48) j = 0;
        GRADIENTS_2D[i] = grad2[j];
    }
}
static inline int32_t fastFloor(double x) { // check if this is actually faster than builtin floor
    int32_t xi = (int32_t)x;
    return x < xi ? xi - 1 : xi;
}

static float grad(int64_t seed, int64_t xsvp, int64_t ysvp, float dx, float dy) {
    int64_t hash = seed ^ xsvp ^ ysvp;
    hash *= HASH_MULTIPLIER;
    hash ^= hash >> (64 - N_GRADS_2D_EXPONENT + 1);
    int32_t gi = (int32_t)hash & ((N_GRADS_2D - 1) << 1);
    return GRADIENTS_2D[gi | 0] * dx + GRADIENTS_2D[gi | 1] * dy;
}


static float noise2_UnskewedBase(int64_t seed, double xs, double ys) {

    // Get base points and offsets.
    int32_t xsb = fastFloor(xs), ysb = fastFloor(ys);
    float xi = (float)(xs - xsb), yi = (float)(ys - ysb);

    // Prime pre-multiplication for hash.
    int64_t xsbp = xsb * PRIME_X, ysbp = ysb * PRIME_Y;

    // Unskew.
    float t = (xi + yi) * (float)UNSKEW_2D;
    float dx0 = xi + t, dy0 = yi + t;

    // First vertex.
    float a0 = RSQUARED_2D - dx0 * dx0 - dy0 * dy0;
    float value = (a0 * a0) * (a0 * a0) * grad(seed, xsbp, ysbp, dx0, dy0);

    // Second vertex.
    float a1 = (float)(2 * (1 + 2 * UNSKEW_2D) * (1 / UNSKEW_2D + 2)) * t + ((float)(-2 * (1 + 2 * UNSKEW_2D) * (1 + 2 * UNSKEW_2D)) + a0);
    float dx1 = dx0 - (float)(1 + 2 * UNSKEW_2D);
    float dy1 = dy0 - (float)(1 + 2 * UNSKEW_2D);
    value += (a1 * a1) * (a1 * a1) * grad(seed, xsbp + PRIME_X, ysbp + PRIME_Y, dx1, dy1);

    // Third and fourth vertices.
    // Nested conditionals were faster than compact bit logic/arithmetic.
    float xmyi = xi - yi;
    if (t < UNSKEW_2D) {
        if (xi + xmyi > 1) {
            float dx2 = dx0 - (float)(3 * UNSKEW_2D + 2);
            float dy2 = dy0 - (float)(3 * UNSKEW_2D + 1);
            float a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2;
            if (a2 > 0) {
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp + (PRIME_X << 1), ysbp + PRIME_Y, dx2, dy2);
            }
        }
        else
        {
            float dx2 = dx0 - (float)UNSKEW_2D;
            float dy2 = dy0 - (float)(UNSKEW_2D + 1);
            float a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2;
            if (a2 > 0) {
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp, ysbp + PRIME_Y, dx2, dy2);
            }
        }

        if (yi - xmyi > 1) {
            float dx3 = dx0 - (float)(3 * UNSKEW_2D + 1);
            float dy3 = dy0 - (float)(3 * UNSKEW_2D + 2);
            float a3 = RSQUARED_2D - dx3 * dx3 - dy3 * dy3;
            if (a3 > 0) {
                value += (a3 * a3) * (a3 * a3) * grad(seed, xsbp + PRIME_X, ysbp + (PRIME_Y << 1), dx3, dy3);
            }
        }
        else
        {
            float dx3 = dx0 - (float)(UNSKEW_2D + 1);
            float dy3 = dy0 - (float)UNSKEW_2D;
            float a3 = RSQUARED_2D - dx3 * dx3 - dy3 * dy3;
            if (a3 > 0) {
                value += (a3 * a3) * (a3 * a3) * grad(seed, xsbp + PRIME_X, ysbp, dx3, dy3);
            }
        }
    }
    else
    {
        if (xi + xmyi < 0) {
            float dx2 = dx0 + (float)(1 + UNSKEW_2D);
            float dy2 = dy0 + (float)UNSKEW_2D;
            float a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2;
            if (a2 > 0) {
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp - PRIME_X, ysbp, dx2, dy2);
            }
        }
        else
        {
            float dx2 = dx0 - (float)(UNSKEW_2D + 1);
            float dy2 = dy0 - (float)UNSKEW_2D;
            float a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2;
            if (a2 > 0) {
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp + PRIME_X, ysbp, dx2, dy2);
            }
        }

        if (yi < xmyi) {
            float dx2 = dx0 + (float)UNSKEW_2D;
            float dy2 = dy0 + (float)(UNSKEW_2D + 1);
            float a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2;
            if (a2 > 0) {
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp, ysbp - PRIME_Y, dx2, dy2);
            }
        }
        else
        {
            float dx2 = dx0 - (float)UNSKEW_2D;
            float dy2 = dy0 - (float)(UNSKEW_2D + 1);
            float a2 = RSQUARED_2D - dx2 * dx2 - dy2 * dy2;
            if (a2 > 0) {
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp, ysbp + PRIME_Y, dx2, dy2);
            }
        }
    }

    return value;
}

/**
 * 2D OpenSimplex2S/SuperSimplex noise, standard lattice orientation.
 */
static float noise2(int64_t seed, double x, double y) {

    // Get points for A2* lattice
    double s = SKEW_2D * (x + y);
    double xs = x + s, ys = y + s;

    return noise2_UnskewedBase(seed, xs, ys);
}

static float noise2_layered(int64_t seed, double x, double y,int octaves ,double scale) {
  const double mul_factor = 2.0; // can be tuned
  const float div_factor = 1.4f; // can be tuned
  float data = 0.0f;

  double a = scale; // Must be double b/c it operates on input
  float sum = 0.0f; // Can be float b/c it operates on output
  float b = (float)scale; // Can be float b/c it operates on output-
  for (int i = 0; i < octaves ; i++) {
    data += noise2(seed,x*a,y*a) * b;// TODO: add offset    
    sum += b;
    a *= mul_factor;
    b /= div_factor;
  }
  return data/sum;
}
static inline uint64_t index(unsigned int x, unsigned int y, uint64_t y_size) { // helper function for noise2_array_layered
    return y * y_size + x;
}
static float* noise2_array_layered(int64_t seed, double xs[],const uint64_t xs_size, double ys[],const uint64_t ys_size, const int octaves, double scale) { 

    float *result = malloc(ys_size*xs_size*sizeof(float));

    for (unsigned int y =0; y < ys_size; y++) {
        for (unsigned int x = 0; x < xs_size; x++) {
            result[index(x,y,ys_size)] = noise2_layered(seed,xs[x],ys[y],octaves,scale);
        }
    }
    return result;
}


static PyObject* PyNoise2(PyObject* self, PyObject* args) {
    double x,y;
    if (!PyArg_ParseTuple(args,"dd",&x,&y)) {
        return NULL; // return error if none found
    }
    float noise = noise2(seed,x,y);

    return Py_BuildValue("f",noise);
}

static PyObject* PyNoise2Layered(PyObject* self, PyObject* args) {
    double x,y,scale;
    int octaves;
    if (!PyArg_ParseTuple(args,"dddi",&x,&y,&scale,&octaves)){
        return NULL;
    }
    float noise = noise2_layered(seed,x,y,octaves,scale);
    return Py_BuildValue("f",noise);
}
static PyObject* PySetSeed(PyObject* self, PyObject* args) {
    int32_t newSeed;
    if (!PyArg_ParseTuple(args,"i",&newSeed)) {
        return NULL;
    }
    seed = newSeed;
    Py_RETURN_NONE;
}
static PyObject* PyCreateNumpyArray(PyObject* self,PyObject* args) {

    PyArrayObject *arr; // represents a numpy array
    if (!PyArg_ParseTuple(args,"O",&arr)) {
        return NULL;
    }
    if (!PyArray_Check(arr) || PyArray_TYPE(arr) != NPY_DOUBLE ) { // make sure that the arguement is a np array and is dtype double
        PyErr_SetString(PyExc_TypeError,"Argument must be a numpy array of type double");
        return NULL;
    }
    double *data; // = PyArray_DATA(arr); // This would only work with the type interpreted and we would have to check against it explicitely earlier
    int64_t size  = PyArray_SIZE(arr); // equivalent to len(arr)
    npy_intp dims[] = {[0] = size};
    PyArray_AsCArray((PyObject**)&arr,&data,dims,1,PyArray_DescrFromType(NPY_DOUBLE)); 
    if (PyErr_Occurred()) { // we cant simply check if(!PyArray...) {return NULL;} because it simply doesn't work
        PyErr_SetString(PyExc_RuntimeError,"Argument numpy array could not be read from, make sure that you are not putting in array slices");
        return NULL;
    }

    PyObject* new_arr = PyArray_SimpleNew(1,dims,NPY_DOUBLE); // Could be PyArrayObject* 
    double *new_data = PyArray_DATA((PyArrayObject * )new_arr);

    
    for (int i = 0; i < size; i++) {
        new_data[i] = 2 * data[i];
    }
    return new_arr;
}

static PyObject* PyNumpyTest(PyObject* self,PyObject* args) {
    PyArrayObject *arr; // represents a numpy array
    if (!PyArg_ParseTuple(args,"O",&arr)) {
        return NULL;
    }
    if (!PyArray_Check(arr) || PyArray_TYPE(arr) != NPY_DOUBLE ) { // make sure that the arguement is a np array and is dtype double
        PyErr_SetString(PyExc_TypeError,"Argument must be a numpy array of type double");
        return NULL;
    }
    double *data; // = PyArray_DATA(arr); // This would only work with the type interpreted and we would have to check against it explicitely earlier
    int64_t size  = PyArray_SIZE(arr); // equivalent to len(arr)
    npy_intp dims[] = {[0] = size};
    PyArray_AsCArray((PyObject**)&arr,&data,dims,1,PyArray_DescrFromType(NPY_DOUBLE));
    if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_RuntimeError,"Argument numpy array could not be read from");
        return NULL;
    }

    double total = 0;
    for (unsigned int i = 0; i < size; i++) {
        total += data[i];
    }
    return PyFloat_FromDouble( total);


}

static PyObject* PyCreateNoiseArray(PyObject* self, PyObject* args) { // xs, ys 
    PyArrayObject *xs,*ys;
    if (!PyArg_ParseTuple(args,"OO",&xs,&ys)) {
        return NULL;
    }
    if (!(PyArray_Check(xs) && PyArray_Check(ys))) { // Make sure that both xs, and ys are Numpy.ndarray
        PyErr_SetString(PyExc_TypeError,"Arguments must be numpy arrays");
        return NULL;
    }
    if (PyArray_TYPE(xs) != NPY_DOUBLE || PyArray_TYPE(ys) != NPY_DOUBLE) { // make sure that both are NPY_FLOAT type
        PyErr_SetString(PyExc_TypeError,"Numpy arrays must be of type <float>");
        return NULL;
    }
    if (!PyArray_IS_C_CONTIGUOUS(xs) || !PyArray_IS_C_CONTIGUOUS(ys)) {
        PyErr_SetString(PyExc_TypeError,"Numpy Arrays must be C-Contiguous, i.e. cannot be slices of an array");
        return NULL;
    }

    int64_t xs_size = PyArray_SIZE(xs);
    int64_t ys_size = PyArray_SIZE(ys);
    double *xs_data, *ys_data;
    xs_data = PyArray_DATA(xs);
    ys_data = PyArray_DATA(ys);
    npy_intp dims[] = {[0] = ys_size, [1] = xs_size};
    PyObject* result = PyArray_SimpleNew(2,dims,NPY_FLOAT);
    float* data = PyArray_DATA((PyArrayObject*)result);
    for (int y =0; y < ys_size; y++) {
        for (int x = 0; x <xs_size;x++) {
            data[y* ys_size + x] = noise2(seed,xs_data[x],ys_data[y]);
        }
    }
    return result;
}

static PyObject* PyCreateNoiseArrayLayered(PyObject* self, PyObject* args) { // xs, ys 
    PyArrayObject *xs,*ys;
    int octaves;
    double scale;
    if (!PyArg_ParseTuple(args,"OOid",&xs,&ys,&octaves,&scale)) {
        return NULL;
    }
    if (!(PyArray_Check(xs) && PyArray_Check(ys))) { // Make sure that both xs, and ys are Numpy.ndarray
        PyErr_SetString(PyExc_TypeError,"Arguments must be numpy arrays");
        return NULL;
    }
    if (PyArray_TYPE(xs) != NPY_DOUBLE || PyArray_TYPE(ys) != NPY_DOUBLE) { // make sure that both are NPY_FLOAT type
        PyErr_SetString(PyExc_TypeError,"Numpy arrays must be of type <double>");
        return NULL;
    }
    if (!PyArray_IS_C_CONTIGUOUS(xs) || !PyArray_IS_C_CONTIGUOUS(ys)) {
        PyErr_SetString(PyExc_TypeError,"Numpy Arrays must be C-Contiguous, i.e. cannot be slices of an array");
        return NULL;
    }

    int64_t xs_size = PyArray_SIZE(xs);
    int64_t ys_size = PyArray_SIZE(ys);
    double *xs_data, *ys_data;
    xs_data = PyArray_DATA(xs);
    ys_data = PyArray_DATA(ys);
    npy_intp dims[] = {[0] = ys_size, [1] = xs_size};
    PyObject* result = PyArray_SimpleNew(2,dims,NPY_FLOAT);
    float* data = PyArray_DATA((PyArrayObject*)result);
    float ** to_data = &data;
    data = noise2_array_layered(seed,xs_data,xs_size,ys_data,ys_size,octaves,scale);
    for (int y =0; y < ys_size; y++) {
        for (int x = 0; x <xs_size;x++) {
            data[y* ys_size + x] = noise2(seed,xs_data[x],ys_data[y]);
        }
    }
    return result;
}
static PyMethodDef functions[] = {
  //"Python Name"          C-Function Name     argument presentation      description

    {"noise2", (PyCFunction) PyNoise2, METH_VARARGS, "get the noise value at a specific x,y location"},
    {"set_seed", (PyCFunction) PySetSeed, METH_O, "Set the seed value for opensimplex noise"},
    {"noise2_array", (PyCFunction) PyCreateNoiseArray, METH_VARARGS, "Create a 2d ndarray filled with noise"},
    {"npsum",(PyCFunction) PyCreateNumpyArray,METH_VARARGS,"np.sum"},

    {NULL,NULL,0,NULL}  /* Sentinel */
};
static struct PyModuleDef module = { PyModuleDef_HEAD_INIT,"helper_functions","module docstring",-1,functions};

PyMODINIT_FUNC PyInit_Perlin(void) {
    init();
    PyObject* return_val =  PyModule_Create(&module);
    import_array();
    return return_val;
}

