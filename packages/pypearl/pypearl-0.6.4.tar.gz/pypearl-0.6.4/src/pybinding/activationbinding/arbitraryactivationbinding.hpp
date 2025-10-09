#pragma once

#include <Python.h>
#include "../../matrix/matrix.hpp"
#include "../../neuralnetwork/activation/arbitraryactivation.hpp"

using AL64 = ActivationLayer<double>;  

typedef struct {
    PyObject_HEAD
    AL64* data;  
} PyAL64;

static void PyAL64_dealloc(PyAL64 *self);
static PyObject* PyAL64_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int PyAL64_init(PyAL64 *self, PyObject *args, PyObject *kwds);

static int PyReLU64_init(PyAL64 *self, PyObject *args, PyObject *kwds);
static int PyLinear64_init(PyAL64 *self, PyObject *args, PyObject *kwds);
static int PySigmoid64_init(PyAL64 *self, PyObject *args, PyObject *kwds);
static int PyStep64_init(PyAL64 *self, PyObject *args, PyObject *kwds);
static int PyLeakyReLU64_init(PyAL64 *self, PyObject *args, PyObject *kwds);
static int PySoftmax64_init(PyAL64 *self, PyObject *args, PyObject *kwds);
static int PyReverseReLU64_init(PyAL64 *self, PyObject *args, PyObject *kwds);

static PyObject* PyAL64_forward(PyAL64 *self, PyObject *arg);
static PyObject * PyAL64_backward(PyAL64 *self, PyObject *arg);

extern PyMethodDef PyAL64_methods[];
extern PyGetSetDef PyAL64_getset[];
extern PyTypeObject PyAL64Type;

extern PyTypeObject PyRELU64Type;
extern PyTypeObject PyLinear64Type;
extern PyTypeObject PySigmoid64Type;
extern PyTypeObject PyLeakyReLU64Type;
extern PyTypeObject PySoftmax64Type;
extern PyTypeObject PyStep64Type;
extern PyTypeObject PyReverseReLU64Type;

#include "arbitraryactivationbinding.cpp"