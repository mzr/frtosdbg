import gdb
from frtosdbg.commands import Command
from frtosdbg.commands.freertos import freertos

from frtosdbg.common.list import FreeRTOSList
from frtosdbg.structgen import structgen_of_ptr

active_queues = {}


class queueCreatedBP(gdb.Breakpoint):
    def __init__(self):
        super().__init__(function='prvInitialiseNewQueue', internal=True)

    def stop(self):
        q = gdb.newest_frame().read_var('pxNewQueue')
        active_queues[int(q)] = structgen_of_ptr(q, typestr='QueueHandle_t')
        return False


class queueDeletedBP(gdb.Breakpoint):
    def __init__(self):

        super().__init__(function='vQueueDelete', internal=True)

    def stop(self):
        q = gdb.newest_frame().read_var('xQueue')
        active_queues.pop(int(q))
        return False


# detect queues
try:
    if gdb.parse_and_eval('prvInitialiseNewQueue') is not None:
        queueCreatedBP()
except:
    pass

if gdb.lookup_global_symbol('vQueueDelete') is not None:
    queueDeletedBP()


@Command(parent=freertos)
def queues(*args):
    for _, q in active_queues.items():
        print('l:\t{}'.format(q.uxLength))
        print('mw:\t{}'.format(q.uxMessagesWaiting))
        print('is:\t{}'.format(q.uxItemSize))
        twts = FreeRTOSList(q.xTasksWaitingToSend, "TaskHandle_t")
        twtr = FreeRTOSList(q.xTasksWaitingToReceive, "TaskHandle_t")
        print('twts:\t{}'.format(twts.length))
        print('twtr:\t{}'.format(twtr.length))
        print("")
