#ifndef MATRIXBINDINGHPP
#define MATRIXBINDINGHPP
#include <Python.h>
#include "../matrix/matrix.hpp"
// Double Arrays
using ArrayD1 = Array<double, 1>;
using ArrayD2 = Array<double, 2>;

// Float Arrays
using ArrayF1 = Array<float, 1>;
using ArrayF2 = Array<float, 2>;

// Int Arrays
using ArrayI1 = Array<int, 1>;
using ArrayI2 = Array<int, 2>;

// Long Arrays
using ArrayL1 = Array<long, 1>;
using ArrayL2 = Array<long, 2>;

// Double Arrays
typedef struct {
  PyObject_HEAD
  ArrayD1 *cpp_obj;
} PyArrayD1Object;

typedef struct {
  PyObject_HEAD
  ArrayD2 *cpp_obj;
} PyArrayD2Object;


// Float Py Objects

typedef struct {
  PyObject_HEAD
  ArrayF1 *cpp_obj;
} PyArrayF1Object;

typedef struct {
  PyObject_HEAD
  ArrayF2 *cpp_obj;
} PyArrayF2Object;


// Int Py Objects

typedef struct {
  PyObject_HEAD
  ArrayI1 *cpp_obj;
} PyArrayI1Object;

typedef struct {
  PyObject_HEAD
  ArrayI2 *cpp_obj;
} PyArrayI2Object;


// Long Py Objects

typedef struct {
  PyObject_HEAD
  ArrayL1 *cpp_obj;
} PyArrayL1Object;

typedef struct {
  PyObject_HEAD
  ArrayL2 *cpp_obj;
} PyArrayL2Object;

// Double 1D
static void PyArrayD1_dealloc(PyArrayD1Object *self);
static PyObject* PyArrayD1_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int PyArrayD1_init(PyArrayD1Object *self, PyObject *args, PyObject *kwds);
static PyObject* PyArrayD1_set(PyArrayD1Object *self, PyObject *args);
static PyObject* PyArrayD1_get(PyArrayD1Object *self, PyObject *args);
static Py_ssize_t PyArrayD1_length(PyArrayD1Object *self, PyObject *args);
static PyObject* PyArrayD1_get_ndim(PyArrayD1Object *self, void *);
static PyObject* PyArrayD1_item(PyObject *self, Py_ssize_t idx);
static int PyArrayD1_ass_item(PyObject *self, Py_ssize_t idx, PyObject *value);

// Double 2D
static void PyArrayD2_dealloc(PyArrayD2Object *self);
static PyObject* PyArrayD2_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int PyArrayD2_init(PyArrayD2Object *self, PyObject *args, PyObject *kwds);
static Py_ssize_t PyArrayD2_length(PyArrayD2Object *self, PyObject *args);
static int PyArrayD2_ass_item(PyObject *self, PyObject *args, PyObject *value);
static PyObject* PyArrayD2_item(PyObject *self, PyObject *args);

static void PyArrayI2_dealloc(PyArrayI2Object *self);
static PyObject* PyArrayI2_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int PyArrayI2_init(PyArrayI2Object *self, PyObject *args, PyObject *kwds);
static Py_ssize_t PyArrayI2_length(PyArrayI2Object *self, PyObject *args);
static int PyArrayI2_ass_item(PyObject *self, PyObject *args, PyObject *value);
static PyObject* PyArrayI2_item(PyObject *self, PyObject *args);


extern PyMethodDef PyArrayD1_methods[];
extern PyGetSetDef PyArrayD1_getset[];
extern PyTypeObject PyArrayD1Type;
extern PySequenceMethods PyArrayD1_as_sequence;

extern PyMethodDef PyArrayD2_methods[];
extern PyGetSetDef PyArrayD2_getset[];
extern PyTypeObject PyArrayD2Type;
extern PyMappingMethods PyArrayD2_as_mapping;

extern PyMethodDef PyArrayI2_methods[];
extern PyGetSetDef PyArrayI2_getset[];
extern PyTypeObject PyArrayI2Type;
extern PyMappingMethods PyArrayI2_as_mapping;

#endif
// For anyone trying to understand this file, start by following it for a 1d and 2d double array, once you get that you'll understand the whole thing.

// Double Arrays
/*using ArrayD1 = Array<double, 1>;
using ArrayD2 = Array<double, 2>;

// Float Arrays
using ArrayF1 = Array<float, 1>;
using ArrayF2 = Array<float, 2>;

// Int Arrays
using ArrayI1 = Array<int, 1>;
using ArrayI2 = Array<int, 2>;

// Long Arrays
using ArrayL1 = Array<long, 1>;
using ArrayL2 = Array<long, 2>;

// Py Objects

// Double Py Objects

typedef struct {
  PyObject_HEAD
  ArrayD1 *cpp_obj;
} PyArrayD1Object;

typedef struct {
  PyObject_HEAD
  ArrayD2 *cpp_obj;
} PyArrayD2Object;


// Float Py Objects

typedef struct {
  PyObject_HEAD
  ArrayF1 *cpp_obj;
} PyArrayF1Object;

typedef struct {
  PyObject_HEAD
  ArrayF2 *cpp_obj;
} PyArrayF2Object;


// Int Py Objects

typedef struct {
  PyObject_HEAD
  ArrayI1 *cpp_obj;
} PyArrayI1Object;

typedef struct {
  PyObject_HEAD
  ArrayI2 *cpp_obj;
} PyArrayI2Object;


// Long Py Objects

typedef struct {
  PyObject_HEAD
  ArrayL1 *cpp_obj;
} PyArrayL1Object;

typedef struct {
  PyObject_HEAD
  ArrayL2 *cpp_obj;
} PyArrayL2Object;


// Function Declarations

// Double 1D
static void PyArrayD1_dealloc(PyArrayD1Object *self);
static PyObject* PyArrayD1_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int PyArrayD1_init(PyArrayD1Object *self, PyObject *args, PyObject *kwds);
static PyObject* PyArrayD1_length(PyArrayD1Object *self, PyObject *);
static PyObject* PyArrayD1_get_ndim(PyArrayD1Object *self, void *);

// Double 2D
static void PyArrayD2_dealloc(PyArrayD2Object *self);
static PyObject* PyArrayD2_new(PyArrayD2Object *type, PyObject *args, PyObject *kwds);
static int PyArrayD2_init(PyArrayD2Object *self, PyObject *args, PyObject *kwds);
static PyObject* PyArrayD2_length(PyArrayD2Object *self, PyObject * unused);
static PyObject* PyArrayD2_get_ndim(PyArrayD2Object *self, void *);

// --- Deallocate: deletes C++ object, then frees the Python object
static void
PyArrayD1_dealloc(PyArrayD1Object *self)
{
    // 1) delete the C++ array
    delete self->cpp_obj;
    // 2) free the Python wrapper
    Py_TYPE(self)->tp_free((PyObject*)self);
}

// --- New: allocates the Python object, sets cpp_obj to nullptr
static PyObject *
PyArrayD1_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyArrayD1Object *self = (PyArrayD1Object*)type->tp_alloc(type, 0);
    if (self) {
        self->cpp_obj = nullptr;
    }
    return (PyObject*)self;
}

// --- Init: called after new; parse “size” and construct the C++ ArrayD1
static int
PyArrayD1_init(PyArrayD1Object *self, PyObject *args, PyObject *kwds)
{
    Py_ssize_t size;
    static char *kwlist[] = { (char*)"size", nullptr };
    // require one integer argument: size
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "n", kwlist, &size))
        return -1;

    try {
        // allocate your C++ object
        self->cpp_obj = new ArrayD1((size_t)size);
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}

static void
PyArrayD2_dealloc(PyArrayD2Object *self)
{
    delete self->cpp_obj;
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject *
PyArrayD2_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyArrayD2Object *self = (PyArrayD2Object*)type->tp_alloc(type, 0);
    if (self) {
        self->cpp_obj = nullptr;
    }
    return (PyObject*)self;
}

static int
PyArrayD2_init(PyArrayD2Object *self, PyObject *args, PyObject *kwds)
{
    Py_ssize_t rows, cols;
    static char *kwlist[] = { (char*)"rows", (char*)"cols", nullptr };
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "nn", kwlist, &rows, &cols))
        return -1;

    // build a two-element size array
    std::size_t dims[2] = { static_cast<std::size_t>(rows),
                            static_cast<std::size_t>(cols) };
    try {
        // call your Array<const size_t*> constructor
        self->cpp_obj = new ArrayD2(dims);
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}

// --- 1-D type definition ----------------------------------------
static PyMethodDef PyArrayD1_methods[] = {
    {"length", (PyCFunction)PyArrayD1_length, METH_NOARGS, "Return number of elements"},
    {NULL, NULL, 0, NULL}
};

static PyGetSetDef PyArrayD1_getset[] = {
    {"ndim", (getter)PyArrayD1_get_ndim, NULL, "Number of dimensions", NULL},
    {NULL, NULL, NULL, NULL, NULL}
};

static PyTypeObject PyArrayD1Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name      = "pypearl.ArrayD1",
    .tp_basicsize = sizeof(PyArrayD1Object),
    .tp_dealloc   = (destructor)PyArrayD1_dealloc,
    .tp_flags     = Py_TPFLAGS_DEFAULT,
    .tp_doc       = "1-D double array",
    .tp_methods   = PyArrayD1_methods,
    .tp_getset    = PyArrayD1_getset,
    .tp_new       = PyArrayD1_new,
    .tp_init      = (initproc)PyArrayD1_init,
};

// --- 2-D type definition ----------------------------------------
static PyMethodDef PyArrayD2_methods[] = {
    {"length", (PyCFunction)PyArrayD2_length, METH_NOARGS, "Return total element count"},
    {NULL, NULL, 0, NULL}
};

static PyGetSetDef PyArrayD2_getset[] = {
    {"ndim", (getter)PyArrayD2_get_ndim, NULL, "Number of dimensions", NULL},
    {NULL, NULL, NULL, NULL, NULL}
};

static PyTypeObject PyArrayD2Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name      = "pypearl.ArrayD2",
    .tp_basicsize = sizeof(PyArrayD2Object),
    .tp_dealloc   = (destructor)PyArrayD2_dealloc,
    .tp_flags     = Py_TPFLAGS_DEFAULT,
    .tp_doc       = "2-D double array",
    .tp_methods   = PyArrayD2_methods,
    .tp_getset    = PyArrayD2_getset,
    .tp_new       = PyArrayD2_new,
    .tp_init      = (initproc)PyArrayD2_init,
};
*/