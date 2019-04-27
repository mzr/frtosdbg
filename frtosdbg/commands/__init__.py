import gdb

class _Command(gdb.Command):
    def __init__(self, complete, parent, prefix, function):

        self.parent_cmd = parent
        self.function = function
        self.local_command_name = function.__name__

        if parent is not None:
            # sub-command
            self.full_command_name = parent.full_command_name + " " + self.local_command_name
        else:
            # root command
            self.full_command_name = self.local_command_name

        # None is for default behaviour as in vanilla command without
        # completer_class passed
        if callable(complete) or complete is None:
            if callable(complete):
                self.complete = complete  # set only when completer provided
            super(_Command, self).__init__(
                self.full_command_name, gdb.COMMAND_USER, prefix=prefix)
        else:
            super(_Command, self).__init__(
                self.full_command_name,
                gdb.COMMAND_USER,
                completer_class=complete,
                prefix=prefix)

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        self.function(*argv)


def Command(complete=gdb.COMPLETE_NONE, parent=None, prefix=False):
    def _command_wrapper(fun):
        return _Command(complete, parent, prefix, fun)

    return _command_wrapper


def PrefixCommand(complete=gdb.COMPLETE_NONE, parent=None):
    return Command(complete, parent, prefix=True)
