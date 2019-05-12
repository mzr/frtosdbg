import gdb
import frtosdbg.commands
from frtosdbg.commands.freertos import freertos
from frtosdbg.structgen import structgen_of_ptr
from frtosdbg.common.list import FreeRTOSList

task_lists = {
    'ready': 'pxReadyTasksLists',
    'pending': 'xPendingReadyList',
    'suspended': 'xSuspendedTaskList',
    'blocked': 'pxDelayedTaskList',
}

are_initialized = False

class InitTaskListsBP(gdb.Breakpoint):
    def __init__(self):
        super().__init__(function='prvInitialiseTaskLists', internal=True, temporary=True)

    def stop(self):
        global are_initialized
        are_initialized = True

InitTaskListsBP()

class TaskList(FreeRTOSList):
    def __init__(self, gdb_value_ptr):
        super().__init__(gdb_value_ptr, "TaskHandle_t")


class TaskListArray:
    # might want gdb_value_ptr here
    def __init__(self, gdb_value):
        self.base = gdb_value.address
        self.size = gdb_value.type.range()[1] + 1
        self.task_lists = []

        for idx in range(self.size):
            gdb_value_task_list = gdb_value[idx]
            self.task_lists.append(TaskList(gdb_value_task_list.address))

    def __iter__(self):
        for task_list in self.task_lists:
            for task in task_list:
                yield task


class UnknownTypeCodeForTaskList(Exception):
    pass


class UnknownTaskListName(Exception):
    pass


def dispatch_task_list_of_sym_str(sym_str):
    gdb_value = gdb.parse_and_eval(sym_str)
    type_code = gdb_value.type.strip_typedefs().code

    if type_code == gdb.TYPE_CODE_PTR:
        task_list = TaskList(gdb_value)
    elif type_code == gdb.TYPE_CODE_STRUCT:
        task_list = TaskList(gdb_value.address)
    elif type_code == gdb.TYPE_CODE_ARRAY:
        task_list = TaskListArray(gdb_value)
    else:
        raise UnknownTypeCodeForTaskList("Type code: %d" % type_code)

    return task_list


def init_task_lists():
    for k, v in task_lists.items():
        task_list = dispatch_task_list_of_sym_str(v)
        task_lists[k] = (v, task_list)


def print_task_list(task_list):

    for idx, item in enumerate(task_list):
        task = structgen_of_ptr(item)
        line1 = "{}.\t({}) {}".format(idx, item.type, task.base)
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


def tasks_completer(text, word):
    return ["ready", "blocked", "suspended", "pending"]


@frtosdbg.commands.Command(parent=freertos, complete=tasks_completer)
@frtosdbg.commands.OnlyWhenTaskListsAreInitialized
def tasks(*args):
    if len(args) == 0:
        for _, v in task_lists.items():
            print_task_list(v[1])
        return

    if args[0] in task_lists:
        print_task_list(task_lists[args[0]][1])
    else:
        raise UnknownTaskListName


init_task_lists()
