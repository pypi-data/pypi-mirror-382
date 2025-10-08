from .bases import Pys

class PysResult(Pys):
    pass

class PysParserResult(PysResult):

    def __init__(self):
        self.error = None
        self.node = None
        self.fatal = False
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count += 1
        self.advance_count += 1

    def register(self, result, require=False):
        self.last_registered_advance_count = result.advance_count
        self.advance_count += result.advance_count
        self.error = result.error
        self.fatal = require or result.fatal
        return result.node

    def try_register(self, result):
        if result.error and not result.fatal:
            self.to_reverse_count = result.advance_count
        else:
            return self.register(result)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error, fatal=True):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
            self.fatal = fatal
        return self

class PysRunTimeResult(PysResult):

    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.func_should_return = False
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, result):
        self.error = result.error
        self.func_return_value = result.func_return_value
        self.func_should_return = result.func_should_return
        self.loop_should_continue = result.loop_should_continue
        self.loop_should_break = result.loop_should_break

        return result.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        self.func_should_return = True
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        return (
            self.error or
            self.func_should_return or
            self.loop_should_continue or
            self.loop_should_break
        )

class PysExecuteResult(PysResult):

    def __init__(self, error, result, context, future):
        self.error = error
        self.result = result
        self.context = context
        self.future = future