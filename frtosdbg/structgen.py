# http://jelly.codes/articles/python-dynamically-creating-classes/
# might as well enclose it all in a generator-class
import gdb

# caches dynamically generated classes which correspond to C-structs base types
class_cache = {}


def base_typename(gdb_type):
    return gdb_type.strip_typedefs().target().tag


def get_class_by_gdb_type(gdb_type):
    return get_class(gdb_type)


def get_class_by_typestr(typestr):
    struct_type = gdb.lookup_type(typestr)
    return get_class(struct_type)


def get_class(struct_type):

    className = base_typename(struct_type)

    if className in class_cache:
        return class_cache[className]

    _Class = construct_class(className, struct_type)
    class_cache[className] = _Class
    return _Class


def construct_class(className, gdb_struct_type):
    def constructor(self, base):
        self.base = base

    d = {}
    d['__init__'] = constructor

    fields = gdb_struct_type.strip_typedefs().target().fields()

    def _closure(val):
        return property(lambda self: self.base.dereference()[val])

    for f in fields:
        d[f.name] = _closure(f.name)

    _Class = type(className, (object, ), d)
    return _Class


def structgen(base_gdb_ptr, **kwargs):
    """Constructs of looks up class and returns its instance.

    Params:
    base_gdb_ptr: gdb.Value - pointer to C-struct. base address
    kwarg:typestr: str - ptr to C-type of this struct
    """

    if 'typestr' in kwargs:
        gdb_struct_type = gdb.lookup_type(kwargs['typestr'])
    else:
        gdb_struct_type = base_gdb_ptr.type

    _Class = get_class(gdb_struct_type)
    return _Class(base_gdb_ptr)
