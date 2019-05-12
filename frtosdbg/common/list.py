import gdb

from frtosdbg.structgen import get_class_by_typestr

ListClass = get_class_by_typestr('List_t')

class FreeRTOSList(ListClass):

    def __init__(self, gdb_value_ptr, cast_type_str="void*"):
        # is this a correct way?
        super().__init__(gdb_value_ptr)
        # print(dir(self))
        # print(self.base.type) # to jest List_t !!!!!!!
        # print(self.xListEnd)
        self.cast_type = gdb.lookup_type(cast_type_str) # no type void* !
        # why cant i use self.xListEnd
        self.end_marker = self.xListEnd
        # self.end_marker = lst['xListEnd']
        self.head = self.end_marker['pxNext']  # ptr to item

    @property
    def length(self):
        # return self.base['uxNumberOfItems']
        return self.uxNumberOfItems

    def __iter__(self):
        item_ptr = self.head
        while item_ptr != self.end_marker.address:
            item = item_ptr.dereference()
            yield item['pvOwner'].cast(self.cast_type)
            item_ptr = item['pxNext']
