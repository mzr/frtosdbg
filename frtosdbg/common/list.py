import gdb

# moze tutaj chce ze structgen klase do listy a potem zrobic
# dziedziczenie i w potomnej klasie __iter__

from frtosdbg.structgen import get_class_by_typestr

ListClass = get_class_by_typestr('List_t')

class FreeRTOSList():

    def __init__(self, lst, cast_type_str="void*"):
        self.base = lst
        self.cast_type = gdb.lookup_type(cast_type_str)
        self.end_marker = lst['xListEnd']
        self.head = self.end_marker['pxNext']  # ptr to item

    @property
    def length(self):
        return self.base['uxNumberOfItems']

    def __iter__(self):
        item_ptr = self.head
        while item_ptr != self.end_marker.address:
            item = item_ptr.dereference()
            yield item['pvOwner'].cast(self.cast_type)
            item_ptr = item['pxNext']
