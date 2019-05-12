import gdb
import frtosdbg.commands
from frtosdbg.commands.freertos import freertos

from frtosdbg.structgen import structgen_of_ptr

from frtosdbg.common.list import FreeRTOSList

are_initialized = False

class InitTaskListsBP(gdb.Breakpoint):
    def __init__(self):
        super().__init__(function='prvInitialiseTaskLists', internal=True, temporary=True)

    def stop(self):
        global are_initialized
        are_initialized = True

InitTaskListsBP()

def print_task_list_ptr(task_list_symbol_name):
    head = gdb.parse_and_eval(task_list_symbol_name).dereference()
    print_task_rtos_list(head)


def print_task_list(task_list_symbol_name):
    head = gdb.parse_and_eval(task_list_symbol_name)
    print_task_rtos_list(head)


def print_task_rtos_list(rtos_list):
    l = FreeRTOSList(rtos_list, "TaskHandle_t")

    for i, item in enumerate(l):
        task = structgen_of_ptr(item)
        line1 = "{}.\t({}) {}".format(i, item.type, task.base)
        line2 = "\tname: {}".format(task.pcTaskName)
        line3 = "\tpriority: {}".format(task.uxPriority)
        print(line1)
        print(line2)
        print(line3)
        try:
            end_of_stack = int(task.pxEndOfStack)
            top_of_stack = int(task.pxTopOfStack)
            stack_left = end_of_stack - top_of_stack
            print("\tstack left: {}".format(stack_left))
        except:
            # no pxTopOfStack
            pass


def print_ready_tasks_lists():
    readyLists = gdb.parse_and_eval('pxReadyTasksLists')
    r = readyLists.type.range()

    for idx in range(r[0], r[1] + 1):
        rtos_list = readyLists[idx]
        print_task_rtos_list(rtos_list)


def tasks_completer(text, word):
    return ["ready", "blocked", "suspended", "pending"]


@frtosdbg.commands.Command(parent=freertos, complete=tasks_completer)
@frtosdbg.commands.OnlyWhenTaskListsAreInitialized
def tasks(*args):
    if len(args) == 0:
        print_ready_tasks_lists()
        print_task_list('xPendingReadyList')
        print_task_list('xSuspendedTaskList')
        print_task_list_ptr('pxDelayedTaskList')
        return

    if args[0] == "ready":
        print_ready_tasks_lists()
    elif args[0] == "pending":
        print_task_list('xPendingReadyList')
    elif args[0] == "suspended":
        print_task_list('xSuspendedTaskList')
    elif args[0] == "blocked":
        print_task_list_ptr('pxDelayedTaskList')
    else:
        print("unknown argument")
