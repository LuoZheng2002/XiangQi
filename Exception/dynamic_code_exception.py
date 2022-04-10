from AGI.translate_struct import print_obj
from AGI.code_browser import translate_code
import traceback

class HardcodedExceptionInfo:
    def __init__(self, function_name):
        self.function_name = function_name


class DynamicExceptionInfo:
    def __init__(self, code_id, input_params, line, runtime_memory):
        self.code_id = code_id
        self.input_params = input_params
        self.line = line
        self.runtime_memory = runtime_memory


class ExpressionException(BaseException):
    def __init__(self, description):
        self.description = description


class LineException(BaseException):
    def __init__(self, line, description):
        self.line = line
        self.description = description


class DynamicCodeException(BaseException):
    def __init__(self, process_exception_info, description):
        self.call_stacks = [process_exception_info]
        self.description = description
        self.line_cache = None


def show_dynamic_code_exception(dce: DynamicCodeException, cid_of, cid_reverse):
    print('Dynamic Code Exception Triggered!')
    print(dce.description)
    for process in dce.call_stacks:
        if type(process) == DynamicExceptionInfo:
            print('Process: \'' + cid_reverse[process.code_id] + "'")
            print('Input params are:')
            for i, param in enumerate(process.input_params):
                print('input' + str(i) + ':')
                print_obj(param, cid_reverse)
            print('The problematic line is: ' + str(process.line))
            print('The runtime registers are:')
            for register in process.runtime_memory.registers:
                print('reg' + str(register.index) + ':')
                print_obj(register.value, cid_reverse)
            print('The code is:')
            translate_code(process.code_id, cid_of, cid_reverse)
            print()
        elif type(process) == HardcodedExceptionInfo:
            print('Hardcoded Process: ' + process.function_name)
            print()
        else:
            assert False
    traceback.print_exc()
