#define PY_SSIZE_T_CLEAN 
#include <C:\Users\Leo\AppData\Local\Programs\Python\Python310\include\Python.h>
#include <limits.h>
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
static const int32_t seed = 3;

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
static int32_t fastFloor(double x) {
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

static PyObject* PyNoise2(PyObject* self, PyObject* args) {
    double x,y;
    if (!PyArg_ParseTuple(args,"dd",&x,&y)) {
        return NULL; // return error if none found
    }
    float noise = noise2(seed,x,y);

    return Py_BuildValue("f",noise);

}

static PyMethodDef functions[] = {
  //"Python Name"          C-Function Name     argument presentation      description

    {"noise2", (PyCFunction) PyNoise2, METH_VARARGS, "add a new value to the hash table"},
    //{"ht_get", (PyCFunction) Pyht_get, METH_VARARGS, "get a value from the hash table"},
    //{"ht_del", (PyCFunction) Pyht_del, METH_VARARGS, "delete a value from the hash table"},
    {"init", (PyCFunction) init, METH_NOARGS, "initiate the module"},

    {NULL,NULL,0,NULL}  /* Sentinel */
};
static struct PyModuleDef module = { PyModuleDef_HEAD_INIT,"helper_functions","module docstring",-1,functions};

PyMODINIT_FUNC PyInit_Perlin(void) {
    init();
    return PyModule_Create(&module);
}

