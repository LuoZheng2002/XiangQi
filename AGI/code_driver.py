from AGI.struct import AGIObject, AGIList
from AGI.objects import to_integer, num_obj
from AGI.code_getter import is_code_dynamic, get_dynamic_code, hardcoded_code_dict
from AGI.runtime_memory import RuntimeMemory, Input
from AGI.concept_ids import cid_of
from copy import deepcopy
from Exception.dynamic_code_exception import DynamicCodeException, LineException, DynamicExceptionInfo, \
    HardcodedExceptionInfo, ExpressionException
from Exception.hardcoded_code_exception import HardcodedCodeException
from AGI.concept_instance_creator import create_concept_instance


def run_hardcoded_code(code_id, input_params: AGIList):
    result = hardcoded_code_dict[code_id](input_params)
    return result


class LineSignal:
    def __init__(self, signal_type, signal_value=None):
        self.signal_type = signal_type
        if signal_type == 'return':
            assert signal_value is not None
        self.signal_value = signal_value


def find_element(target_list: AGIList, expr, runtime_memory) -> int:
    assert type(target_list) == AGIList
    for i, element in enumerate(target_list.value):
        if solve_expression(expr, runtime_memory, element).concept_id == cid_of['True']:
            return i
    return -1


def solve_expression(expr: AGIObject, runtime_memory: RuntimeMemory, target=None) -> AGIObject or AGIList:
    if expr.concept_id == cid_of['input']:
        index = to_integer(expr.attribute('dc::index'))
        assert runtime_memory.has_input(index)
        return runtime_memory.get_input_value(index)
    if expr.concept_id == cid_of['reg']:
        index = to_integer(expr.attribute('dc::index'))
        assert runtime_memory.has_reg(index)
        return runtime_memory.get_reg_value(index)
    if expr.concept_id == cid_of['iterator']:
        index = to_integer(expr.attribute('dc::index'))
        assert runtime_memory.has_iterator(index)
        return runtime_memory.get_iterator_value(index)
    if expr.concept_id == cid_of['call']:
        code_id = expr.attribute('dc::function_name').concept_id
        if is_code_dynamic(code_id):
            try:
                result = run_dynamic_code(code_id, expr.attribute('dc::function_params'))
            except DynamicCodeException as d:
                d.line_cache = to_integer(expr.attribute('dc::line_index'))
                raise
        else:
            try:
                result = run_hardcoded_code(code_id, expr.attribute('dc::function_params'))
            except HardcodedCodeException as h:
                h.line = to_integer(expr.attribute('dc::line_index'))
                raise
        return result
    if expr.concept_id == cid_of['concept_instance']:
        return create_concept_instance(expr.attribute('concept_name').concept_id)
    if expr.concept_id == cid_of['size']:
        target_list = solve_expression(expr.attribute('dc::target_list'), runtime_memory, target)
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        return num_obj(target_list.size())
    if expr.concept_id == cid_of['get_member']:
        target_object = solve_expression(expr.attribute('dc::target_object'), runtime_memory, target)
        member_id = expr.attribute('dc::member_name').concept_id
        return target_object.attributes[member_id]
    if expr.concept_id == cid_of['at']:
        target_list = solve_expression(expr.attribute('dc::target_list'), runtime_memory, target)
        index = to_integer(solve_expression(expr.attribute('dc::index'), runtime_memory, target))
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        return target_list.get_element(index)
    if expr.concept_id == cid_of['find'] or expr.concept_id == cid_of['exist'] or expr.concept_id == cid_of['count']:
        target_list = solve_expression(expr.attribute('dc::target_list'), runtime_memory, target)
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        count = 0
        for element in target_list.value:
            if solve_expression(expr.attribute('dc::expression_for_constraint'),
                                runtime_memory, element).concept_id == cid_of['True']:
                if expr.concept_id == cid_of['find']:
                    return element
                if expr.concept_id == cid_of['exist']:
                    return AGIObject(cid_of['True'])
                count += 1
        if expr.concept_id == cid_of['find']:
            raise ExpressionException('Can not find the target element!')
        if expr.concept_id == cid_of['exist']:
            return AGIObject(cid_of['False'])
        return num_obj(count)
    if expr.concept_id == cid_of['target']:
        assert target is not None
        return target
    if expr.concept_id == cid_of['constexpr']:
        return expr.attribute('value')
    assert False


def process_line(line: AGIObject, runtime_memory: RuntimeMemory) -> LineSignal:
    try:
        if line.concept_id == cid_of['dcr::assign'] or line.concept_id == cid_of['dcr::assign_as_reference']:
            rhs_value = solve_expression(line.attribute('dc::right_value'), runtime_memory)
            lhs = line.attribute('dc::left_value')
            if lhs.concept_id == cid_of['dcr::reg']:
                reg_index = to_integer(lhs.attribute('dc::index'))
                if not runtime_memory.has_reg(reg_index):
                    if line.concept_id == cid_of['dcr::assign']:
                        runtime_memory.create_reg(reg_index, deepcopy(rhs_value))
                    else:
                        runtime_memory.create_reg(reg_index, rhs_value)
                else:
                    if line.concept_id == cid_of['dcr::assign']:
                        runtime_memory.set_reg(reg_index, deepcopy(rhs_value))
                    else:
                        runtime_memory.set_reg(reg_index, rhs_value)
            elif lhs.concept_id == cid_of['dcr::at']:
                target_list = solve_expression(lhs.attribute('dc::target_list'), runtime_memory)
                element_index = solve_expression(lhs.attribute('dc::element_index'), runtime_memory)
                if type(target_list) == AGIObject:
                    target_list = target_list.agi_list()
                else:
                    assert type(target_list) == AGIList
                if line.concept_id == cid_of['dcr::assign']:
                    target_list.set_value(to_integer(element_index), deepcopy(rhs_value))
                else:
                    target_list.set_value(to_integer(element_index), rhs_value)
            elif lhs.concept_id == cid_of['dcr::get_member']:
                target_object = solve_expression(lhs.attribute('dc::target_object'), runtime_memory)
                assert type(target_object) == AGIObject
                member_name = solve_expression(lhs.attribute('dc::member_name'), runtime_memory)
                member_id = member_name.concept_id
                assert member_id in target_object.attributes.keys()
                if line.concept_id == cid_of['dcr::assign']:
                    target_object.attributes[member_id] = deepcopy(rhs_value)
                else:
                    target_object.attributes[member_id] = rhs_value
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::return']:
            return_value = solve_expression(line.attribute('dc::return_value'), runtime_memory)
            return LineSignal('return', return_value)
        if line.concept_id == cid_of['dcr::assert']:
            assert_expression = solve_expression(line.attribute('dc::assert_expression'), runtime_memory)
            if assert_expression.concept_id != cid_of['True']:
                raise LineException(to_integer(line.attribute('dc::line_index')), 'Assertion Failed')
            return LineSignal('normal')
        if line.concept_id == cid_of['for']:
            iter_id = to_integer(line.attribute('dc::iterator_index'))
            if runtime_memory.has_iterator(iter_id):
                iterator = runtime_memory.get_iterator(iter_id)
                iterator.value = 0
            else:
                iterator = runtime_memory.create_iterator(iter_id, 0)
            end_value = to_integer(solve_expression(line.attribute('dc::end_value'), runtime_memory))
            for i in range(end_value):
                for for_line in line.attribute('dc::for_block').agi_list().value:
                    try:
                        line_signal = process_line(for_line, runtime_memory)
                    except DynamicCodeException as d:
                        d.line_cache = to_integer(for_line.attribute('dc::line_index'))
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('normal')
                    if line_signal.signal_type == 'return':
                        return line_signal
                assert iterator.value == i
                iterator.value = iterator.value + 1
            return LineSignal('normal')
        if line.concept_id == cid_of['while']:
            loop_count = 0
            while solve_expression(line.attribute('dc::expression_for_judging'),
                                   runtime_memory).concept_id == cid_of['True']:
                loop_count += 1
                for while_line in line.attribute('dc::while_block').agi_list().value:
                    try:
                        line_signal = process_line(while_line, runtime_memory)
                    except DynamicCodeException as d:
                        d.line_cache = to_integer(while_line.attribute('dc::line_index'))
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('normal')
                    if line_signal.signal_type == 'return':
                        return line_signal
                if loop_count == 1000:
                    raise LineException(to_integer(line.attribute('dc::line_index')), 'While loop does not stop.')
            return LineSignal('normal')
        if line.concept_id == cid_of['break']:
            return LineSignal('break')
        if line.concept_id == cid_of['if']:
            expression_for_judging = solve_expression(line.attribute('dc::expression_for_judging'), runtime_memory)
            if expression_for_judging.concept_id == cid_of['True']:
                for if_line in line.attribute('dc::if_block').agi_list().value:
                    try:
                        line_signal = process_line(if_line, runtime_memory)
                    except DynamicCodeException as d:
                        d.line_cache = to_integer(if_line.attribute('dc::line_index'))
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('break')
                    if line_signal.signal_type == 'return':
                        return line_signal
            elif_executed = False
            for elif_module in line.attribute('dc::elif_modules').agi_list().value:
                elif_expression = solve_expression(elif_module.attribute('dc::expression_for_judging'), runtime_memory)
                if elif_expression.concept_id == cid_of['True']:
                    for elif_line in elif_module.attribute('dc::elif_block').agi_list().value:
                        try:
                            line_signal = process_line(elif_line, runtime_memory)
                        except DynamicCodeException as d:
                            d.line_cache = to_integer(elif_line.attribute('dc::line_index'))
                            raise
                        except LineException:
                            raise
                        if line_signal.signal_type == 'break':
                            return LineSignal('break')
                        if line_signal.signal_type == 'return':
                            return line_signal
                    elif_executed = True
                    break
            if not elif_executed:
                for else_line in line.attribute('dc::else_block').agi_list().value:
                    try:
                        line_signal = process_line(else_line, runtime_memory)
                    except DynamicCodeException as d:
                        d.line_cache = to_integer(else_line.attribute('dc::line_index'))
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('break')
                    if line_signal.signal_type == 'return':
                        return line_signal
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::append']:
            target_list = solve_expression(line.attribute('dc::target_list'), runtime_memory)
            element = solve_expression(line.attribute('dc::element'), runtime_memory)
            if type(target_list) == AGIObject:
                target_list = target_list.agi_list()
            else:
                assert type(target_list) == AGIList
            target_list.append(element)
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::remove']:
            target_list = solve_expression(line.attribute('dc::target_list'), runtime_memory)
            if type(target_list) == AGIObject:
                target_list = target_list.agi_list()
            else:
                assert type(target_list) == AGIList
            while True:
                element_pos = find_element(target_list, line.attribute('dc::expression_for_constraint'), runtime_memory)
                if element_pos == -1:
                    break
                target_list.remove(element_pos)
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::request']:
            for reg_id in line.attribute('dc::requested_registers').value:
                reg_id_int = to_integer(reg_id)
                raw_input = input('Dynamic code asks you to fill in reg' + str(reg_id_int) + '!')
                if raw_input.isdigit():
                    input_object = num_obj(int(raw_input))
                else:
                    assert False
                if not runtime_memory.has_reg(reg_id_int):
                    runtime_memory.create_reg(reg_id_int, input_object)
                else:
                    runtime_memory.set_reg(reg_id_int, input_object)
            for provided_line in line.attribute('dc::provided_block').agi_list().value:
                try:
                    line_signal = process_line(provided_line, runtime_memory)
                except DynamicCodeException as d:
                    d.line_cache = to_integer(provided_line.attribute('dc::line_index'))
                    raise
                except LineException:
                    raise
                assert line_signal.signal_type != 'break'
                if line_signal.signal_type == 'return':
                    return line_signal
            if solve_expression(line.attribute('dc::expression_for_constraint'),
                                runtime_memory).concept_id != cid_of['True']:
                raise LineException(to_integer(line.attribute('dc::line_index')),
                                    'Your inputs do not satisfy the constraints.')
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::call_none_return_func']:
            code_id = line.attribute('dc::function_name').concept_id
            if is_code_dynamic(code_id):
                try:
                    result = run_dynamic_code(code_id, line.attribute('dc::function_params'))
                except DynamicCodeException as d:
                    d.line_cache = to_integer(line.attribute('dc::line_index'))
                    raise

            else:
                try:
                    result = run_hardcoded_code(code_id, line.attribute('dc::function_params'))
                except HardcodedCodeException as h:
                    h.line = to_integer(line.attribute('dc::line_index'))
                    raise

            assert result.concept_id == cid_of['None']
        assert False
    except ExpressionException as e:
        raise LineException(to_integer(line.attribute('dc::line_index')), e.description)


def run_dynamic_code(code_id: int, input_params: AGIList) -> AGIObject:
    code_object = get_dynamic_code(code_id)
    runtime_memory = RuntimeMemory()
    for i, input_param in enumerate(input_params.value):
        runtime_memory.inputs.append(Input(i, input_param))
    for line in code_object.agi_list().value:
        try:
            line_signal = process_line(line, runtime_memory)
        except LineException as l:
            raise DynamicCodeException(DynamicExceptionInfo(code_id, input_params.value, l.line, runtime_memory), l.description)
        except DynamicCodeException as d:
            d.call_stacks.append(DynamicExceptionInfo(code_id, input_params.value, d.line_cache, runtime_memory))
            raise
        except HardcodedCodeException as h:
            raise DynamicCodeException(HardcodedExceptionInfo(h.function_name), h.description)
        assert line_signal.signal_type != 'break'
        if line_signal.signal_type == 'return':
            return line_signal.signal_value
    return AGIObject(cid_of['None'])
