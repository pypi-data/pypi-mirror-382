#ifndef ArbitraryBindingTPP
#define ArbitraryBindingTPP

#include "arbitraryactivationbinding.hpp"

static void PyAL64_dealloc(PyAL64 *self)
{
    delete self->data->saved_inputs;

    delete self->data->dinputs;

    delete self->data->outputs;

    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject* PyAL64_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyAL64 *self = (PyAL64*)type->tp_alloc(type, 0);
    if (self) {
        self->data = nullptr;
    }
    return (PyObject*)self;
}

static int PyAL64_init(PyAL64 *self, PyObject *args, PyObject *kwds)
{
    Py_ssize_t prev, cur;
    try {
        self->data = new ActivationLayer<double>{0x0, nullptr, nullptr, 0.0f, nullptr, false, 0.0f, 0.0f};
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}

static int PyReLU64_init(PyAL64 *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"minimum", NULL};  
    double alpha = 0.0;  

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|d", kwlist, &alpha)) {
        return -1;  
    }

    Py_ssize_t prev, cur;
    try {
        // Obscure the hardcoded 0.0 branch micro optimization behind something no one ever has to see in Python because no Python programmer will ever use this on their own
        if(alpha == 0.0){
            self->data = new ActivationLayer<double>{0x1, nullptr, nullptr, 0.0f, nullptr, false, 0.0f, 0.0f};
        }
        else{
            self->data = new ActivationLayer<double>{0x0, nullptr, nullptr, alpha, nullptr, false, 0.0f, 0.0f};
        }
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}

static int PyLinear64_init(PyAL64 *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"m", "b", "flow", NULL};  
    double m = 1.0;
    double b = 0.0;
    int flowint = 1;  
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ddp", kwlist, &m, &b, &flowint)) {
        return -1;  
    }
    bool flow = false;
    if(kwds && PyDict_GetItemString(kwds, "flow")) flow = (flowint != 0);

    Py_ssize_t prev, cur;
    try {
        // Obscure the hardcoded 0.0 branch micro optimization behind something no one ever has to see in Python because no Python programmer will ever use this on their own
        if(b == 0.0){
            if(m == 1.0){
                if(flow==true){
                    // Optimized Linear with no logits (literally just a foward and backward return the EXACT ADDRESS that was inputted)
                    self->data = new ActivationLayer<double>{0x5, nullptr, nullptr, 0.0f, nullptr, false, 1.0f, 0.0f};
                }
                else{
                    // Copies a saved inputs, copies an outputs copies a dvalues -> dinputs. Literally the worst and most evil function ever. Do nothing in O(n^2) time. The fact I am supporting this for someone who might want it should warrant a nobel peace prize if this library ever gets more than 5 users.
                    self->data = new ActivationLayer<double>{0x4, nullptr, nullptr, 0.0f, nullptr, false, 1.0f, 0.0f};
                }
            }
            else{
                // Linear with a slope. Needs some optimization, but your welcome for saving a variable load and add instruction per value.
                self->data = new ActivationLayer<double>{0xa, nullptr, nullptr, 0.0f, nullptr, false, m, 0.0f};
            }
        }
        else{
            // Linear with a slope and an offset. Backpass for 0xa and 0xb are the same branch
            self->data = new ActivationLayer<double>{0xb, nullptr, nullptr, 0.0f, nullptr, false, m, b};
        }
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}

static int PySigmoid64_init(PyAL64 *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {NULL};  

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist)) {
        return -1;  
    }

    Py_ssize_t prev, cur;
    try {
        // Why is this simpler than linear
        self->data = new ActivationLayer<double>{0x6, nullptr, nullptr, 0.0f, nullptr, false, 0.0f, 0.0f};

    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}

static int PyLeakyReLU64_init(PyAL64 *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"minimum", "alpha", NULL};  
    double minimum = 0.0;
    double alpha = 0.0;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|dd", kwlist, &minimum, &alpha)) {
        return -1;  
    }

    Py_ssize_t prev, cur;
    try {
        // Check if it's even leaky
        if(alpha == 0.0){
            if(minimum == 0.0){
                // Put in a 0 ReLU
                self->data = new ActivationLayer<double>{0x1, nullptr, nullptr, 0.0f, nullptr, false, 0.0f, 0.0f};
            }
            else{
                // Put in an arbitrary minimum ReLU
                self->data = new ActivationLayer<double>{0x0, nullptr, nullptr, minimum, nullptr, false, 0.0f, 0.0f};
            }
        }
        else{
            // Actual Leaky ReLU
            self->data = new ActivationLayer<double>{0x3, nullptr, nullptr, minimum, nullptr, false, alpha, 0.0f};
        }
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}

static int PyStep64_init(PyAL64 *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"minimum", "maximum", "flip", NULL};  
    double minimum = 1.0f;
    double maximum = 0.0f;
    double flip = 0.0f;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ddd", kwlist, &minimum, &maximum, &flip)) {
        return -1;  
    }

    Py_ssize_t prev, cur;

    try {
        self->data = new ActivationLayer<double>{0x7, nullptr, nullptr, flip, nullptr, false, minimum, maximum};
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}

static int PySoftmax64_init(PyAL64 *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = { NULL};  
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist)) {
        return -1;  
    }

    Py_ssize_t prev, cur;

    try {
        self->data = new ActivationLayer<double>{0x2, nullptr, nullptr, 0.0f, nullptr, false, 0.0f, 0.0f};
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}

static int PyReverseReLU64_init(PyAL64 *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"maximum", NULL};  
    double maximum = 0.0;  
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|d", kwlist, &maximum)) {
        return -1;  
    }


    Py_ssize_t prev, cur;
    try {
        // If this function becomes popular I'll probably optimize for now it's one path
        self->data = new ActivationLayer<double>{0xc, nullptr, nullptr, maximum, nullptr, false, 0.0f, 0.0f};
        
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return -1;
    }
    return 0;
}

static PyObject* PyAL64_forward(PyAL64 *self, PyObject *arg){
    PyAL64 *activation = (PyAL64*) self;

    static char *kwlist[] = { (char*)"x", NULL };
    if (!PyObject_TypeCheck(arg, &PyArrayD2Type)) {
        PyErr_SetString(PyExc_TypeError, "forward() expects an ArrayD2");
        return NULL;
    }
    PyArrayD2Object *input_obj = (PyArrayD2Object*)arg;

    ArrayD2* out_cpp;

    try {
        out_cpp = activationForward(input_obj->cpp_obj, (*activation->data));
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }

    // Allocate a new Python ArrayD2 object
    PyObject *out_py = PyArrayD2Type.tp_new(&PyArrayD2Type, NULL, NULL);

    if (!out_py) return NULL;
    // Steal the C++ result into its cpp_obj
    ((PyArrayD2Object*)out_py)->cpp_obj = new ArrayD2(std::move((*out_cpp)));

    return out_py;
}

static PyObject * PyAL64_backward(PyAL64 *self, PyObject *arg){
    PyAL64 *activation = (PyAL64*) self;

    if (!PyObject_TypeCheck(arg, &PyArrayD2Type)) {
        PyErr_SetString(PyExc_TypeError, "forward() expects an ArrayD2");
        return NULL;
    }
    PyArrayD2Object *input_obj = (PyArrayD2Object*)arg;

    ArrayD2* out_cpp;
    try {
        out_cpp = activationBackward(input_obj->cpp_obj, (*activation->data));
    } catch (const std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }

    // Allocate a new Python ArrayD2 object
    PyObject *out_py = PyArrayD2Type.tp_new(&PyArrayD2Type, NULL, NULL);
    if (!out_py) return NULL;

    // Steal the C++ result into its cpp_obj
    ((PyArrayD2Object*)out_py)->cpp_obj = new ArrayD2(std::move((*out_cpp)));

    return out_py;
}

PyMethodDef PyAL64_methods[]{
    {"forward", (PyCFunction)PyAL64_forward, METH_O, "forward(x)->y"},
    {"backward", (PyCFunction)PyAL64_backward, METH_O, "backward(x)->y"},
    {NULL, NULL, 0, NULL}
};

PyGetSetDef PyAL64_getset[] = {
    {NULL, NULL, NULL, NULL, NULL}
};

PyTypeObject PyAL64Type{
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.activation",                          // tp_name
    sizeof(PyAL64),                   // tp_basicsize
    0,                                       // tp_itemsize
    (destructor)PyAL64_dealloc,            // tp_dealloc
    0,                                       // tp_vectorcall_offset / tp_print (deprecated)
    0,                                       // tp_getattr
    0,                                       // tp_setattr
    0,                                       // tp_as_async / tp_compare
    0,                                       // tp_repr
    0,                                       // tp_as_number
    0,                                       // tp_as_sequence
    0,                                       // tp_as_mapping
    0,                                       // tp_hash
    0,                                       // tp_call
    0,                                       // tp_str
    0,                                       // tp_getattro
    0,                                       // tp_setattro
    0,                                       // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                      // tp_flags
    "Neural Network Activation",                 // tp_doc
    0,                                       // tp_traverse
    0,                                       // tp_clear
    0,                                       // tp_richcompare
    0,                                       // tp_weaklistoffset
    0,                                       // tp_iter
    0,                                       // tp_iternext
    PyAL64_methods,                         // tp_methods
    0,                                       // tp_members
    PyAL64_getset,                          // tp_getset
    0,                                       // tp_base
    0,                                       // tp_dict
    0,                                       // tp_descr_get
    0,                                       // tp_descr_set
    0,                                       // tp_dictoffset
    (initproc)PyAL64_init,                 // tp_init
    0,                                       // tp_alloc
    PyAL64_new,                             // tp_new
};

PyTypeObject PyRELU64Type{
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.RELU64",                          // tp_name
    sizeof(PyAL64),                   // tp_basicsize
    0,                                       // tp_itemsize
    (destructor)PyAL64_dealloc,            // tp_dealloc
    0,                                       // tp_vectorcall_offset / tp_print (deprecated)
    0,                                       // tp_getattr
    0,                                       // tp_setattr
    0,                                       // tp_as_async / tp_compare
    0,                                       // tp_repr
    0,                                       // tp_as_number
    0,                                       // tp_as_sequence
    0,                                       // tp_as_mapping
    0,                                       // tp_hash
    0,                                       // tp_call
    0,                                       // tp_str
    0,                                       // tp_getattro
    0,                                       // tp_setattro
    0,                                       // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                      // tp_flags
    "Neural Network ReLU Activation",                 // tp_doc
    0,                                       // tp_traverse
    0,                                       // tp_clear
    0,                                       // tp_richcompare
    0,                                       // tp_weaklistoffset
    0,                                       // tp_iter
    0,                                       // tp_iternext
    PyAL64_methods,                         // tp_methods
    0,                                       // tp_members
    PyAL64_getset,                          // tp_getset
    0,                                       // tp_base
    0,                                       // tp_dict
    0,                                       // tp_descr_get
    0,                                       // tp_descr_set
    0,                                       // tp_dictoffset
    (initproc)PyReLU64_init,                 // tp_init
    0,                                       // tp_alloc
    PyAL64_new,                             // tp_new
};

PyTypeObject PyLinear64Type{
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.Linear64",                          // tp_name
    sizeof(PyAL64),                   // tp_basicsize
    0,                                       // tp_itemsize
    (destructor)PyAL64_dealloc,            // tp_dealloc
    0,                                       // tp_vectorcall_offset / tp_print (deprecated)
    0,                                       // tp_getattr
    0,                                       // tp_setattr
    0,                                       // tp_as_async / tp_compare
    0,                                       // tp_repr
    0,                                       // tp_as_number
    0,                                       // tp_as_sequence
    0,                                       // tp_as_mapping
    0,                                       // tp_hash
    0,                                       // tp_call
    0,                                       // tp_str
    0,                                       // tp_getattro
    0,                                       // tp_setattro
    0,                                       // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                      // tp_flags
    "Neural Network Linear Activation",                 // tp_doc
    0,                                       // tp_traverse
    0,                                       // tp_clear
    0,                                       // tp_richcompare
    0,                                       // tp_weaklistoffset
    0,                                       // tp_iter
    0,                                       // tp_iternext
    PyAL64_methods,                         // tp_methods
    0,                                       // tp_members
    PyAL64_getset,                          // tp_getset
    0,                                       // tp_base
    0,                                       // tp_dict
    0,                                       // tp_descr_get
    0,                                       // tp_descr_set
    0,                                       // tp_dictoffset
    (initproc)PyLinear64_init,                 // tp_init
    0,                                       // tp_alloc
    PyAL64_new,                             // tp_new
};

PyTypeObject PySigmoid64Type{
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.Sigmoid64",                          // tp_name
    sizeof(PyAL64),                   // tp_basicsize
    0,                                       // tp_itemsize
    (destructor)PyAL64_dealloc,            // tp_dealloc
    0,                                       // tp_vectorcall_offset / tp_print (deprecated)
    0,                                       // tp_getattr
    0,                                       // tp_setattr
    0,                                       // tp_as_async / tp_compare
    0,                                       // tp_repr
    0,                                       // tp_as_number
    0,                                       // tp_as_sequence
    0,                                       // tp_as_mapping
    0,                                       // tp_hash
    0,                                       // tp_call
    0,                                       // tp_str
    0,                                       // tp_getattro
    0,                                       // tp_setattro
    0,                                       // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                      // tp_flags
    "Neural Network Sigmoid Activation",                 // tp_doc
    0,                                       // tp_traverse
    0,                                       // tp_clear
    0,                                       // tp_richcompare
    0,                                       // tp_weaklistoffset
    0,                                       // tp_iter
    0,                                       // tp_iternext
    PyAL64_methods,                         // tp_methods
    0,                                       // tp_members
    PyAL64_getset,                          // tp_getset
    0,                                       // tp_base
    0,                                       // tp_dict
    0,                                       // tp_descr_get
    0,                                       // tp_descr_set
    0,                                       // tp_dictoffset
    (initproc)PySigmoid64_init,                 // tp_init
    0,                                       // tp_alloc
    PyAL64_new,                             // tp_new
};

PyTypeObject PyLeakyReLU64Type{
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.LeakyReLU64",                          // tp_name
    sizeof(PyAL64),                   // tp_basicsize
    0,                                       // tp_itemsize
    (destructor)PyAL64_dealloc,            // tp_dealloc
    0,                                       // tp_vectorcall_offset / tp_print (deprecated)
    0,                                       // tp_getattr
    0,                                       // tp_setattr
    0,                                       // tp_as_async / tp_compare
    0,                                       // tp_repr
    0,                                       // tp_as_number
    0,                                       // tp_as_sequence
    0,                                       // tp_as_mapping
    0,                                       // tp_hash
    0,                                       // tp_call
    0,                                       // tp_str
    0,                                       // tp_getattro
    0,                                       // tp_setattro
    0,                                       // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                      // tp_flags
    "Neural Network Leaky ReLU Activation",                 // tp_doc
    0,                                       // tp_traverse
    0,                                       // tp_clear
    0,                                       // tp_richcompare
    0,                                       // tp_weaklistoffset
    0,                                       // tp_iter
    0,                                       // tp_iternext
    PyAL64_methods,                         // tp_methods
    0,                                       // tp_members
    PyAL64_getset,                          // tp_getset
    0,                                       // tp_base
    0,                                       // tp_dict
    0,                                       // tp_descr_get
    0,                                       // tp_descr_set
    0,                                       // tp_dictoffset
    (initproc)PyLeakyReLU64_init,                 // tp_init
    0,                                       // tp_alloc
    PyAL64_new,                             // tp_new
};

PyTypeObject PyStep64Type{
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.Step64",                          // tp_name
    sizeof(PyAL64),                   // tp_basicsize
    0,                                       // tp_itemsize
    (destructor)PyAL64_dealloc,            // tp_dealloc
    0,                                       // tp_vectorcall_offset / tp_print (deprecated)
    0,                                       // tp_getattr
    0,                                       // tp_setattr
    0,                                       // tp_as_async / tp_compare
    0,                                       // tp_repr
    0,                                       // tp_as_number
    0,                                       // tp_as_sequence
    0,                                       // tp_as_mapping
    0,                                       // tp_hash
    0,                                       // tp_call
    0,                                       // tp_str
    0,                                       // tp_getattro
    0,                                       // tp_setattro
    0,                                       // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                      // tp_flags
    "Neural Network Step Activation",                 // tp_doc
    0,                                       // tp_traverse
    0,                                       // tp_clear
    0,                                       // tp_richcompare
    0,                                       // tp_weaklistoffset
    0,                                       // tp_iter
    0,                                       // tp_iternext
    PyAL64_methods,                         // tp_methods
    0,                                       // tp_members
    PyAL64_getset,                          // tp_getset
    0,                                       // tp_base
    0,                                       // tp_dict
    0,                                       // tp_descr_get
    0,                                       // tp_descr_set
    0,                                       // tp_dictoffset
    (initproc)PyStep64_init,                 // tp_init
    0,                                       // tp_alloc
    PyAL64_new,                             // tp_new
};

// There's no way I'll ever track down all the random comments in this library
PyTypeObject PySoftmax64Type{
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.Softmax64",                          // tp_name
    sizeof(PyAL64),                   // tp_basicsize
    0,                                       // tp_itemsize
    (destructor)PyAL64_dealloc,            // tp_dealloc
    0,                                       // tp_vectorcall_offset / tp_print (deprecated)
    0,                                       // tp_getattr
    0,                                       // tp_setattr
    0,                                       // tp_as_async / tp_compare
    0,                                       // tp_repr
    0,                                       // tp_as_number
    0,                                       // tp_as_sequence
    0,                                       // tp_as_mapping
    0,                                       // tp_hash
    0,                                       // tp_call
    0,                                       // tp_str
    0,                                       // tp_getattro
    0,                                       // tp_setattro
    0,                                       // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                      // tp_flags
    "Neural Network Softmax Activation",                 // tp_doc
    0,                                       // tp_traverse
    0,                                       // tp_clear
    0,                                       // tp_richcompare
    0,                                       // tp_weaklistoffset
    0,                                       // tp_iter
    0,                                       // tp_iternext
    PyAL64_methods,                         // tp_methods
    0,                                       // tp_members
    PyAL64_getset,                          // tp_getset
    0,                                       // tp_base
    0,                                       // tp_dict
    0,                                       // tp_descr_get
    0,                                       // tp_descr_set
    0,                                       // tp_dictoffset
    (initproc)PySoftmax64_init,                 // tp_init
    0,                                       // tp_alloc
    PyAL64_new,                             // tp_new
};

PyTypeObject PyReverseReLU64Type{
    PyVarObject_HEAD_INIT(NULL, 0)
    "pypearl.ReverseReLU64",                          // tp_name
    sizeof(PyAL64),                   // tp_basicsize
    0,                                       // tp_itemsize
    (destructor)PyAL64_dealloc,            // tp_dealloc
    0,                                       // tp_vectorcall_offset / tp_print (deprecated)
    0,                                       // tp_getattr
    0,                                       // tp_setattr
    0,                                       // tp_as_async / tp_compare
    0,                                       // tp_repr
    0,                                       // tp_as_number
    0,                                       // tp_as_sequence
    0,                                       // tp_as_mapping
    0,                                       // tp_hash
    0,                                       // tp_call
    0,                                       // tp_str
    0,                                       // tp_getattro
    0,                                       // tp_setattro
    0,                                       // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                      // tp_flags
    "Neural Network Softmax Activation",                 // tp_doc
    0,                                       // tp_traverse
    0,                                       // tp_clear
    0,                                       // tp_richcompare
    0,                                       // tp_weaklistoffset
    0,                                       // tp_iter
    0,                                       // tp_iternext
    PyAL64_methods,                         // tp_methods
    0,                                       // tp_members
    PyAL64_getset,                          // tp_getset
    0,                                       // tp_base
    0,                                       // tp_dict
    0,                                       // tp_descr_get
    0,                                       // tp_descr_set
    0,                                       // tp_dictoffset
    (initproc)PyReverseReLU64_init,                 // tp_init
    0,                                       // tp_alloc
    PyAL64_new,                             // tp_new
};

#endif