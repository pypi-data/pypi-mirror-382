#ifndef MATRIXBINDING
#define MATRIXBINDING

#include "matrixbinding.hpp"

static void
PyArrayD1_dealloc(PyArrayD1Object *self)
{
    // 1) delete the C++ array
    delete self->cpp_obj;
    // 2) free the Python wrapper
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject *
PyArrayD1_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyArrayD1Object *self = (PyArrayD1Object*)type->tp_alloc(type, 0);
    if (self) {
        self->cpp_obj = nullptr;
    }
    return (PyObject*)self;
}

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

static PyObject *
PyArrayD1_set(PyArrayD1Object *self, PyObject *args){

    Py_ssize_t idx;
    double newval;
    if(!PyArg_ParseTuple(args, "nd", &idx, &newval))
        return NULL;
    size_t size = self->cpp_obj->len;
    if (!self->cpp_obj) {
        PyErr_SetString(PyExc_AttributeError,
                        "ArrayD1 object not initialized");
        return NULL;
    }

    if(idx < 0 || (size_t)idx >= size){
        PyErr_SetString(PyExc_IndexError, "index out of bounds");
        return NULL;
    }
    (*(self->cpp_obj))[(size_t)idx] = newval;
    Py_RETURN_NONE;
}
static Py_ssize_t
PyArrayD1_length(PyArrayD1Object *self, PyObject *args)
{
    // assuming your C++ object has a .len member
    return (Py_ssize_t) self->cpp_obj->len;
}
static PyObject *
PyArrayD1_str(PyArrayD1Object *self)
{
    try {
        const std::string &s = self->cpp_obj->toString();
        return PyUnicode_FromString(s.c_str());   /* new ref */
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }
}

static PyObject *
PyArrayD1_get(PyArrayD1Object *self, PyObject *args)
{
    Py_ssize_t idx;
    // parse one integer argument
    if (!PyArg_ParseTuple(args, "n", &idx))
        return NULL;

    // bounds‐check
    size_t size = self->cpp_obj->len;  
    if (idx < 0 || (size_t)idx >= size) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }

    // fetch from your C++ array
    double value = (*(self->cpp_obj))[(size_t)idx];
    return PyFloat_FromDouble(value);
}

static PyObject *
PyArrayD1_item(PyObject *self, Py_ssize_t idx)
{
    // Build a one-element tuple (idx,) so we can call your existing get
    PyObject *args = Py_BuildValue("(n)", idx);
    if (!args) return NULL;

    PyObject *result = PyArrayD1_get((PyArrayD1Object*)self, args);
    Py_DECREF(args);
    return result;
}

// adapter for __setitem__
static int
PyArrayD1_ass_item(PyObject *self, Py_ssize_t idx, PyObject *value)
{
    // Build a two-element tuple (idx, value) for your existing set
    PyObject *args = Py_BuildValue("(nO)", idx, value);
    if (!args) return -1;

    PyObject *res = PyArrayD1_set((PyArrayD1Object*)self, args);
    Py_DECREF(args);
    if (!res) return -1;
    Py_DECREF(res);
    return 0;
}

PyMethodDef PyArrayD1_methods[] = {
    {"get", (PyCFunction)PyArrayD1_get, METH_VARARGS,
     "get(index) -> float\n\n"
     "Return the element at position `index` (0-based)."},
     {"set", (PyCFunction)PyArrayD1_set, METH_VARARGS, "set(index)->float\n\n"
     "Change the element at position index"},
    {NULL, NULL, 0, NULL}
};

PyGetSetDef PyArrayD1_getset[] = {
    {NULL, NULL, NULL, NULL, NULL}
}; 

PyTypeObject PyArrayD1Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.ArrayD1",               // tp_name
    sizeof(PyArrayD1Object),         // tp_basicsize
    0,                               // tp_itemsize
    (destructor)PyArrayD1_dealloc,   // tp_dealloc
    0,                               // tp_vectorcall_offset  (or tp_print in very old CPython)
    0,                               // tp_getattr
    0,                               // tp_setattr
    0,                               // tp_reserved / tp_compare
    (reprfunc)PyArrayD1_str,         // tp_repr
    0,                               // tp_as_number
    0,                               // tp_as_sequence
    0,                               // tp_as_mapping
    0,                               // tp_hash
    0,                               // tp_call
    (reprfunc)PyArrayD1_str,         // tp_str
    0,                               // tp_getattro
    0,                               // tp_setattro
    0,                               // tp_as_buffer
    Py_TPFLAGS_DEFAULT,              // tp_flags
    "1-D double array",              // tp_doc
    0,                               // tp_traverse
    0,                               // tp_clear
    0,                               // tp_richcompare
    0,                               // tp_weaklistoffset
    0,                               // tp_iter
    0,                               // tp_iternext
    PyArrayD1_methods,               // tp_methods
    0,                               // tp_members
    PyArrayD1_getset,                // tp_getset
    0,                               // tp_base
    0,                               // tp_dict
    0,                               // tp_descr_get
    0,                               // tp_descr_set
    0,                               // tp_dictoffset
    (initproc)PyArrayD1_init,        // tp_init
    0,                               // tp_alloc
    PyArrayD1_new                    // tp_new
};


PySequenceMethods PyArrayD1_as_sequence = {
    /* sq_length    */ (lenfunc)         PyArrayD1_length,
    /* sq_concat    */ 0,
    /* sq_repeat    */ 0,
    /* sq_item      */ (ssizeargfunc)    PyArrayD1_item,      // <— adapter
    /* sq_slice     */ 0,
    /* sq_ass_item  */ (ssizeobjargproc) PyArrayD1_ass_item,  // <— adapter
    /* …rest zero… */
};







static void
PyArrayD2_dealloc(PyArrayD2Object *self)
{
    delete self->cpp_obj;
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
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

static bool
get_two_indices(PyObject *key, Py_ssize_t &i, Py_ssize_t &j) {

    if (!PyTuple_Check(key) || PyTuple_Size(key) != 2) {
        PyErr_SetString(PyExc_TypeError, "Index must be a tuple of two integers");
        return false;
    }

    PyObject *i_obj = PyTuple_GetItem(key, 0);
    PyObject *j_obj = PyTuple_GetItem(key, 1);
    i = PyNumber_AsSsize_t(i_obj, PyExc_IndexError);
    j = PyNumber_AsSsize_t(j_obj, PyExc_IndexError);
    if ((i == -1 && PyErr_Occurred()) || (j == -1 && PyErr_Occurred()))
        return false;
    return true;
}

// __getitem__ for 2D
static PyObject *
PyArrayD2_item(PyObject *self, PyObject *args)
{
    auto *obj = (PyArrayD2Object*)self;
    Py_ssize_t i, j;
    if (!get_two_indices(args, i, j))
        return NULL;
    // bounds check
    if (i < 0 || i >= (Py_ssize_t)obj->cpp_obj->shape[0] ||
        j < 0 || j >= (Py_ssize_t)obj->cpp_obj->shape[1]) {
        PyErr_SetString(PyExc_IndexError, "ArrayD2 index out of range");
        return NULL;
    }

    // assuming operator[](i)[j] works in your C++
    double v = (*obj->cpp_obj)[i][j];
    return PyFloat_FromDouble(v);
}


static int
PyArrayD2_ass_item(PyObject *self, PyObject *args, PyObject *value)
{
    auto *obj = (PyArrayD2Object*)self;
    Py_ssize_t i, j;

    if (!get_two_indices(args, i, j))
        return -1;

    if (i < 0 || i >= (Py_ssize_t)obj->cpp_obj->shape[0] ||
        j < 0 || j >= (Py_ssize_t)obj->cpp_obj->shape[1]) {
        PyErr_SetString(PyExc_IndexError, "ArrayD2 index out of range");
        return -1;
    }

    double dv = PyFloat_AsDouble(value);
    if (PyErr_Occurred()) return -1;
    (*obj->cpp_obj)[i][j] = dv;
    return 0;

}

static Py_ssize_t 
PyArrayD2_length(PyArrayD2Object *self, PyObject *args){
    return (Py_ssize_t) self->cpp_obj->shape[0];
}

static PyObject *
PyArrayD2_str(PyArrayD2Object *self)
{
    try {
        const std::string &s = self->cpp_obj->toString();
        return PyUnicode_FromString(s.c_str());   /* new ref */
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }
}


PyMethodDef PyArrayD2_methods[] = {
    
    {NULL, NULL, 0, NULL}
};

PyGetSetDef PyArrayD2_getset[] = {
    {NULL, NULL, NULL, NULL, NULL}
};

PyTypeObject PyArrayD2Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.ArrayD2",               // tp_name
    sizeof(PyArrayD2Object),         // tp_basicsize
    0,                               // tp_itemsize
    (destructor)PyArrayD2_dealloc,   // tp_dealloc
    0,                               // tp_vectorcall_offset / tp_print
    0,                               // tp_getattr
    0,                               // tp_setattr
    0,                               // tp_reserved / tp_compare
    (reprfunc)PyArrayD2_str,         // tp_repr
    0,                               // tp_as_number
    0,                               // tp_as_sequence
    0,                               // tp_as_mapping
    0,                               // tp_hash
    0,                               // tp_call
    (reprfunc)PyArrayD2_str,         // tp_str
    0,                               // tp_getattro
    0,                               // tp_setattro
    0,                               // tp_as_buffer
    Py_TPFLAGS_DEFAULT,              // tp_flags
    "2-D double array",              // tp_doc
    0,                               // tp_traverse
    0,                               // tp_clear
    0,                               // tp_richcompare
    0,                               // tp_weaklistoffset
    0,                               // tp_iter
    0,                               // tp_iternext
    PyArrayD2_methods,               // tp_methods
    0,                               // tp_members
    PyArrayD2_getset,                // tp_getset
    0,                               // tp_base
    0,                               // tp_dict
    0,                               // tp_descr_get
    0,                               // tp_descr_set
    0,                               // tp_dictoffset
    (initproc)PyArrayD2_init,        // tp_init
    0,                               // tp_alloc
    PyArrayD2_new                    // tp_new
};

PyMappingMethods PyArrayD2_as_mapping = {
    /* mp_length        */ (lenfunc)       PyArrayD2_length,       // len(x) → rows
    /* mp_subscript     */ (binaryfunc)    PyArrayD2_item,         // x[key]
    /* mp_ass_subscript */ (objobjargproc) PyArrayD2_ass_item,    // x[key] = val
};

static void
PyArrayI2_dealloc(PyArrayI2Object *self)
{
    delete self->cpp_obj;
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
PyArrayI2_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyArrayI2Object *self = (PyArrayI2Object*)type->tp_alloc(type, 0);
    if (self) {
        self->cpp_obj = nullptr;
    }
    return (PyObject*)self;
}

static int
PyArrayI2_init(PyArrayI2Object *self, PyObject *args, PyObject *kwds)
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
        self->cpp_obj = new ArrayI2(dims);
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}


// __getitem__ for 2D
static PyObject *
PyArrayI2_item(PyObject *self, PyObject *args)
{
    auto *obj = (PyArrayI2Object*)self;
    Py_ssize_t i, j;
    if (!get_two_indices(args, i, j))
        return NULL;
    // bounds check
    if (i < 0 || i >= (Py_ssize_t)obj->cpp_obj->shape[0] ||
        j < 0 || j >= (Py_ssize_t)obj->cpp_obj->shape[1]) {
        PyErr_SetString(PyExc_IndexError, "ArrayI2 index out of range");
        return NULL;
    }

    // assuming operator[](i)[j] works in your C++
    int v = (*obj->cpp_obj)[i][j];
    return PyLong_FromLong((long)v);
}


static int
PyArrayI2_ass_item(PyObject *self, PyObject *args, PyObject *value)
{
    auto *obj = (PyArrayI2Object*)self;
    Py_ssize_t i, j;

    if (!get_two_indices(args, i, j))
        return -1;

    if (i < 0 || i >= (Py_ssize_t)obj->cpp_obj->shape[0] ||
        j < 0 || j >= (Py_ssize_t)obj->cpp_obj->shape[1]) {
        PyErr_SetString(PyExc_IndexError, "ArrayI2 index out of range");
        return -1;
    }

    long tmp = PyLong_AsLong(value);
    if (tmp < INT_MIN || tmp > INT_MAX) {    
        PyErr_SetString(PyExc_OverflowError,
                        "value out of range for C int");
        return NULL;
    }

    int dv = (int)tmp;                       

    if (PyErr_Occurred()) return -1;
    (*obj->cpp_obj)[i][j] = dv;
    return 0;

}

static Py_ssize_t 
PyArrayI2_length(PyArrayI2Object *self, PyObject *args){
    return (Py_ssize_t) self->cpp_obj->shape[0];
}

static PyObject *
PyArrayI2_str(PyArrayI2Object *self)
{
    try {
        const std::string &s = self->cpp_obj->toString();
        return PyUnicode_FromString(s.c_str());   /* new ref */
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }
}


PyMethodDef PyArrayI2_methods[] = {
    
    {NULL, NULL, 0, NULL}
};

PyGetSetDef PyArrayI2_getset[] = {
    {NULL, NULL, NULL, NULL, NULL}
};

PyTypeObject PyArrayI2Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.ArrayI2",               // tp_name
    sizeof(PyArrayI2Object),        // tp_basicsize
    0,                               // tp_itemsize
    (destructor)PyArrayI2_dealloc,  // tp_dealloc
    0,                               // tp_vectorcall_offset or tp_print
    0,                               // tp_getattr
    0,                               // tp_setattr
    0,                               // tp_reserved / tp_compare
    (reprfunc)PyArrayI2_str,         // tp_repr
    0,                               // tp_as_number
    0,                               // tp_as_sequence
    0,                               // tp_as_mapping
    0,                               // tp_hash 
    0,                               // tp_call
    (reprfunc)PyArrayI2_str,         // tp_str
    0,                               // tp_getattro
    0,                               // tp_setattro
    0,                               // tp_as_buffer
    Py_TPFLAGS_DEFAULT,              // tp_flags
    "2-D int array",                 // tp_doc
    0,                               // tp_traverse
    0,                               // tp_clear
    0,                               // tp_richcompare
    0,                               // tp_weaklistoffset
    0,                               // tp_iter
    0,                               // tp_iternext
    PyArrayI2_methods,               // tp_methods
    0,                               // tp_members
    PyArrayI2_getset,                // tp_getset
    0,                               // tp_base
    0,                               // tp_dict
    0,                               // tp_descr_get
    0,                               // tp_descr_set
    0,                               // tp_dictoffset
    (initproc)PyArrayI2_init,        // tp_init
    0,                               // tp_alloc
    PyArrayI2_new                    // tp_new
};

PyMappingMethods PyArrayI2_as_mapping = {
    /* mp_length        */ (lenfunc)       PyArrayI2_length,       // len(x) → rows
    /* mp_subscript     */ (binaryfunc)    PyArrayI2_item,         // x[key]
    /* mp_ass_subscript */ (objobjargproc) PyArrayI2_ass_item,    // x[key] = val
};

 
#endif