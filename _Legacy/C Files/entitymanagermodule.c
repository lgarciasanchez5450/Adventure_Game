#define PY_SSIZE_T_CLEAN 
#include <C:\Users\Leo\AppData\Local\Programs\Python\Python312\include\Python.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>




static PyObject* collide_chunks(PyObject* self, PyObject* arg) {
  double x1,y1,z1,x2,y2,z2;
  int CHUNK_SIZE;
  if (!PyArg_ParseTuple(arg,"ddddddi",&x1,&y1,&z1,&x2,&y2,&z2,&CHUNK_SIZE)) {
    return NULL; // return error if none found
  }

  if (CHUNK_SIZE == 0) {
    PyErr_SetString(PyExc_ValueError,"chunk_size cannot be 0 size first!");
    return NULL;
  }
  int cx1 = (int)floor(x1/CHUNK_SIZE);
  int cy1 = (int)floor(y1/CHUNK_SIZE);
  int cz1 = (int)floor(z1/CHUNK_SIZE);
  int cx2 = (int)ceil(x2/CHUNK_SIZE);
  int cy2 = (int)ceil(y2/CHUNK_SIZE);
  int cz2 = (int)ceil(z2/CHUNK_SIZE);

  if (cx1 > cx2 || cy1 > cy2 || cz1 > cz2) {
    PyErr_SetString(PyExc_ValueError, "Incorrect Argument Values"); 
    return NULL;
  }

  Py_ssize_t chunks_colliding = (cx2-cx1+1) * (cy2-cy1+1) * (cz2-cz1+1);
  PyObject* chunks = PyTuple_New(chunks_colliding);
  if (chunks == NULL) {
    PyErr_SetString(PyExc_RuntimeError,"Error Building Final Tuple");
    return NULL;
  }
  int i = 0;
  for (int y = cy1;y <=cy2; y++) {
    for (int z = cz1;z <= cz2; z++) {
      for (int x = cx1;x <= cx2; x++) {
        PyObject* pos = PyTuple_Pack(3,Py_BuildValue("i",x),Py_BuildValue("i",y),Py_BuildValue("i",z));
        if (pos == NULL) {
          PyErr_SetString(PyExc_RuntimeError,"Error Building Final Coordinate Tuple");
          for (int _i = 0; i < i;i++) {
            Py_DECREF(PyTuple_GET_ITEM(chunks,i));
          }
          Py_DECREF(chunks);
          return NULL;
        }
        PyTuple_SET_ITEM(chunks,i,pos);
        i++;
      }
    }
  }

  return chunks;
}

static PyObject* inclusive_range(PyObject* self, PyObject* arg) {
  int start,stop,step;
  if (!PyArg_ParseTuple(arg,"iii",&start,&stop,&step)) {
    return NULL; // return error if none found
  }
  Py_ssize_t length = 1;// Py_ssize_t is just a macro for __int64 on this machine
  int count = start;
  while (count < stop) {
    count += step;
    length++;
  }


  count = start;
  if (start == stop) {
    PyObject* tup = PyTuple_New(1);
    PyTuple_SET_ITEM(tup,0,Py_BuildValue("i",start));
    return tup;
  }
  PyObject* tup = PyTuple_New(length);
  for (int i = 0; i<length-1;i++){
    PyTuple_SET_ITEM(tup,i,Py_BuildValue("i",count));
    count += step;
  }
  PyTuple_SET_ITEM(tup,length-1,Py_BuildValue("i",stop));
  return tup;
  //x and y will now hold the position of the chunk submitted

}
// will return a "mathematical integer" of type <double>


static PyMethodDef functions[] = {
  //"Python Name"                  C-Function Name     argument presentation      description
  //{"say_hello",                  exmod_say_hello,           METH_VARARGS,         "Say Hello from C and print message"},
  //{"init",                        (PyCFunction) init,                       METH_O,           "compute the nth fibonnaci number"},
  //{"addEntity",                   (PyCFunction) addNewEntity,                  METH_VARARGS,           "ADD BOODY"},
  //{"getEntitiesInChunk",          (PyCFunction) getEntitiesInChunk,         METH_VARARGS,     "ADD BOODY"},


  {"inclusive_range", (PyCFunction) inclusive_range, METH_VARARGS, "just like normal range but also includes the <stop> argument"},
  {"collide_chunks", (PyCFunction) collide_chunks, METH_VARARGS, "dum dum collide dum chunks"},
  {NULL,NULL,0,NULL}  /* Sentinel */
};
static struct PyModuleDef module = { PyModuleDef_HEAD_INIT,"entity_manager2","module docstring",-1,functions};

PyMODINIT_FUNC PyInit_entity_manager2(void) {
  return PyModule_Create(&module);
}
