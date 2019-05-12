# might as well enclose it all in a generator-class
import gdb

# caches dynamically generated classes which correspond to C-structs base types
class_cache = {}


def get_class_by_gdb_type(gdb_type):
    return get_class(gdb_type)


def get_class_by_typestr(typestr):
    struct_type = gdb.lookup_type(typestr)
    return get_class(struct_type)


def base_type(gdb_type):
    return gdb_type.strip_typedefs()


def base_type_tag(gdb_type):
    return base_type(gdb_type).tag


def get_class(gdb_type):

    className = base_type_tag(gdb_type)

    if className in class_cache:
        return class_cache[className]

    gdb_base_type = base_type(gdb_type)
    _Class = construct_class(gdb_base_type)
    class_cache[className] = _Class
    return _Class


def construct_class(gdb_base_type):
    """Constructs class corresponding to C-type struct.
    Parameters:
    gdb_base_struct_type: gdb.Type. may be typedef but NOT A POINTER
    """
    className = base_type_tag(gdb_base_type)

    def constructor(self, base):
        self.base = base

    d = {}
    d['__init__'] = constructor

    d['gdb_base_type'] = gdb_base_type

    fields = gdb_base_type.strip_typedefs().fields()

    def _closure(val):
        return property(lambda self: self.base.dereference()[val])

    for f in fields:
        d[f.name] = _closure(f.name)
    
    _Class = type(className, (object, ), d)
    return _Class


def structgen_of_ptr(gdb_value_ptr, **kwargs):
    """Constructs of looks up class and returns its instance.

    Params:
    gdb_value_ptr: gdb.Value - pointer to C-struct. base address
    kwarg:typestr: str - ptr to C-type of this struct
    """

    if 'typestr' in kwargs:
        gdb_type_ptr = gdb.lookup_type(kwargs['typestr'])
    else:
        gdb_type_ptr = gdb_value_ptr.type

    # need to dereference pointer
    gdb_type = gdb_type_ptr.strip_typedefs().target()

    _Class = get_class(gdb_type)
    return _Class(gdb_value_ptr)

def structgen(gdb_value, **kwargs):
    """Constructs of looks up class and returns its instance.

    Params:
    gdb_value: gdb.Value - C-struct.
    kwarg:typestr: str - C-type of this struct
    """

    if 'typestr' in kwargs:
        gdb_type = gdb.lookup_type(kwargs['typestr'])
    else:
        gdb_type = gdb_value.type

    _Class = get_class(gdb_type)
    return _Class(gdb_value.address)

