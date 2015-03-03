#include <Python.h>
#include <wordexp.h>

static PyObject *wordexp_wordexp(PyObject *self, PyObject *args) {
    char *string;
    wordexp_t expansion;
    PyObject *returnval;

    int i=0;

    if (!PyArg_ParseTuple(args, "s:wordexp", &string)) {
        return NULL;
    }

    wordexp(string, &expansion, 0);

    if((int)expansion.we_wordc >= 0) {
        if(!(returnval = PyTuple_New(expansion.we_wordc))) {
            return NULL;
        }

        for(i=0; i < expansion.we_wordc; i++) {
            PyObject *obj;
            obj = Py_BuildValue("s", expansion.we_wordv[i]);
            PyTuple_SET_ITEM(returnval, i, obj);
        }
    } else { /* couldn't expand the string, return it verbatim */
        PyErr_SetString(PyExc_RuntimeError, "wordexp() failed to expand string");
        return NULL;
    }

    wordfree(&expansion);
    return returnval;
}

static PyMethodDef wordexp_methods[] = {
    { "wordexp", wordexp_wordexp, METH_VARARGS, 
         "Separates a string into words according to shell expansion rules." },
    { NULL, NULL, 0, NULL} /* sentinel */
};

PyMODINIT_FUNC initwordexp(void) {
    Py_InitModule("wordexp", wordexp_methods);
}
