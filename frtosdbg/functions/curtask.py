import gdb

import frtosdbg.functions

@frtosdbg.functions.Function
def curtask():
    return gdb.parse_and_eval('pxCurrentTCB')

