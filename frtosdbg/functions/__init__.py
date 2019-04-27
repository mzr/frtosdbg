import gdb

class Function(gdb.Function):

    # init dziala tylko jak kod jest parsowany
    def __init__(self, function):
        self.function = function
        self.function_name = function.__name__

        # czy do super na pewno dobre argumenty?
        super(Function, self).__init__(self.function_name)

    def invoke(self, *args, **kwargs):
        # return self(*args, **kwargs)
        return self.function(*args, **kwargs)

