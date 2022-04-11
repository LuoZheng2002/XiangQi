from AGI.struct import AGIObject, AGIList
from AGI.objects import to_integer, num_obj
from AGI.hardcoded_code_getter import get_hardcoded_code
from AGI.code_getter_fundamental import is_code_dynamic
from AGI.runtime_memory import RuntimeMemory, Input
from copy import deepcopy
from Exception.dynamic_code_exception import DynamicCodeException, LineException, DynamicExceptionInfo, \
    HardcodedExceptionInfo, ExpressionException
from Exception.hardcoded_code_exception import HardcodedCodeException
from Exception.structure_exception import StructureException
from AGI.concept_instance_creator import create_concept_instance
from AGI.translate_struct import print_obj
from Hardcoded.is_code_dynamic_func import is_code_dynamic_func
from Hardcoded.run_hardcoded_code_func import run_hardcoded_code_func
from Hardcoded.code_simulator import get_dynamic_code_object


def run_hardcoded_code(code_id, input_params: AGIList, cid_of, dcd):
    if code_id == cid_of['func::is_code_dynamic']:
        result = is_code_dynamic_func(input_params, cid_of, dcd)
    elif code_id == cid_of['func::run_hardcoded_code']:
        result = run_hardcoded_code_func(input_params, cid_of, dcd)
    elif code_id == cid_of['func::get_dynamic_code_object']:
        result = get_dynamic_code_object(input_params, cid_of, dcd)
    else:
        result = get_hardcoded_code(code_id, cid_of)(input_params, cid_of)
    if result is None:
        result = AGIObject(cid_of['None'])
    return result


class LineSignal:
    def __init__(self, signal_type, signal_value=None):
        self.signal_type = signal_type
        if signal_type == 'return':
            assert signal_value is not None
        self.signal_value = signal_value


def find_element(target_list: AGIList, expr, runtime_memory, cid_of, dcd) -> int:
    assert type(target_list) == AGIList
    for i, element in enumerate(target_list.value):
        if solve_expression(expr, runtime_memory, cid_of, dcd, element).concept_id == cid_of['True']:
            return i
    return -1


def solve_expression(expr: AGIObject, runtime_memory: RuntimeMemory, cid_of, dcd,
                     target=None) -> AGIObject or AGIList:
    if expr.concept_id == cid_of['dcr::input']:
        index = to_integer(expr.attributes[cid_of['dc::index']], cid_of)
        assert runtime_memory.has_input(index)
        return runtime_memory.get_input_value(index)
    if expr.concept_id == cid_of['dcr::reg']:
        index = to_integer(expr.attributes[cid_of['dc::index']], cid_of)
        if not runtime_memory.has_reg(index):
            raise ExpressionException('Register not created.')
        return runtime_memory.get_reg_value(index)
    if expr.concept_id == cid_of['dcr::iterator']:
        index = to_integer(expr.attributes[cid_of['dc::index']], cid_of)
        assert runtime_memory.has_iterator(index)
        return num_obj(runtime_memory.get_iterator_value(index), cid_of)
    if expr.concept_id == cid_of['dcr::call']:
        code_id = expr.attributes[cid_of['dc::function_name']].concept_id
        function_params = list()
        for param in expr.attributes[cid_of['dc::function_params']].value:
            function_params.append(solve_expression(param, runtime_memory, cid_of, dcd, target))
        function_params = AGIList(function_params)
        if is_code_dynamic(code_id, dcd, cid_of):
            try:
                result = run_dynamic_code(code_id, function_params, cid_of, dcd)
            except DynamicCodeException as d:
                raise
        else:
            try:
                result = run_hardcoded_code(code_id, function_params, cid_of, dcd)
            except HardcodedCodeException as h:
                raise
        return result
    if expr.concept_id == cid_of['dcr::concept_instance']:
        return create_concept_instance(expr.attributes[cid_of['dc::concept_name']].concept_id, cid_of)
    if expr.concept_id == cid_of['dcr::size']:
        target_list = solve_expression(expr.attributes[cid_of['dc::target_list']],
                                       runtime_memory, cid_of, dcd, target)
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        return num_obj(target_list.size(), cid_of)
    if expr.concept_id == cid_of['dcr::get_member']:
        target_object = solve_expression(expr.attributes[cid_of['dc::target_object']],
                                         runtime_memory, cid_of, dcd, target)
        member_id = expr.attributes[cid_of['dc::member_name']].concept_id
        if member_id not in target_object.attributes.keys():
            raise ExpressionException('Can not get target object\'s member!')
        return target_object.attributes[member_id]
    if expr.concept_id == cid_of['dcr::at']:
        target_list = solve_expression(expr.attributes[cid_of['dc::target_list']],
                                       runtime_memory, cid_of, dcd, target)
        index = to_integer(solve_expression(expr.attributes[cid_of['dc::element_index']],
                                            runtime_memory, cid_of, dcd, target), cid_of)
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        return target_list.get_element(index)
    if expr.concept_id == cid_of['dcr::find'] or \
            expr.concept_id == cid_of['dcr::exist'] or expr.concept_id == cid_of['dcr::count']:
        target_list = solve_expression(expr.attributes[cid_of['dc::target_list']],
                                       runtime_memory, cid_of, dcd, target)
        if type(target_list) == AGIObject:
            target_list = target_list.agi_list()
        else:
            assert type(target_list) == AGIList
        count = 0
        for element in target_list.value:
            if solve_expression(expr.attributes[cid_of['dc::expression_for_constraint']],
                                runtime_memory, cid_of, dcd, element).concept_id == cid_of['True']:
                if expr.concept_id == cid_of['dcr::find']:
                    return element
                if expr.concept_id == cid_of['dcr::exist']:
                    return AGIObject(cid_of['True'])
                count += 1
        if expr.concept_id == cid_of['dcr::find']:
            raise ExpressionException('Can not find the target element!')
        if expr.concept_id == cid_of['dcr::exist']:
            return AGIObject(cid_of['False'])
        return num_obj(count, cid_of)
    if expr.concept_id == cid_of['dcr::target']:
        assert target is not None
        return target
    if expr.concept_id == cid_of['dcr::constexpr']:
        return expr.attributes[cid_of['value']]
    print(expr.concept_id)
    raise ExpressionException('Unknown head of expression!')


def process_line(line: AGIObject, runtime_memory: RuntimeMemory, cid_of, dcd) -> LineSignal:
    try:
        if line.concept_id == cid_of['dcr::assign'] or line.concept_id == cid_of['dcr::assign_as_reference']:
            rhs_value = solve_expression(line.attributes[cid_of['dc::right_value']], runtime_memory, cid_of, dcd)
            lhs = line.attributes[cid_of['dc::left_value']]
            if lhs.concept_id == cid_of['dcr::reg']:
                reg_index = to_integer(lhs.attributes[cid_of['dc::index']], cid_of)
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
                target_list = solve_expression(lhs.attributes[cid_of['dc::target_list']], runtime_memory, cid_of,
                                               dcd)
                element_index = solve_expression(lhs.attributes[cid_of['dc::element_index']], runtime_memory, cid_of,
                                                 dcd)
                if type(target_list) == AGIObject:
                    target_list = target_list.agi_list()
                else:
                    assert type(target_list) == AGIList
                if line.concept_id == cid_of['dcr::assign']:
                    target_list.set_value(to_integer(element_index, cid_of), deepcopy(rhs_value))
                else:
                    target_list.set_value(to_integer(element_index, cid_of), rhs_value)
            elif lhs.concept_id == cid_of['dcr::get_member']:
                target_object = solve_expression(lhs.attributes[cid_of['dc::target_object']], runtime_memory, cid_of,
                                                 dcd)
                assert type(target_object) == AGIObject
                member_id = lhs.attributes[cid_of['dc::member_name']].concept_id
                assert member_id in target_object.attributes.keys()
                if line.concept_id == cid_of['dcr::assign']:
                    target_object.attributes[member_id] = deepcopy(rhs_value)
                else:
                    target_object.attributes[member_id] = rhs_value
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::return']:
            return_value = solve_expression(line.attributes[cid_of['dc::return_value']], runtime_memory, cid_of,
                                            dcd)
            return LineSignal('return', return_value)
        if line.concept_id == cid_of['dcr::assert']:
            assert_expression = solve_expression(line.attributes[cid_of['dc::assert_expression']],
                                                 runtime_memory, cid_of, dcd)
            if assert_expression.concept_id != cid_of['True']:
                raise LineException(to_integer(line.attributes[cid_of['dc::line_index']], cid_of),
                                    'Assertion Failed in Dynamic Code.')
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::for']:
            iter_id = to_integer(line.attributes[cid_of['dc::iterator_index']], cid_of)
            if runtime_memory.has_iterator(iter_id):
                iterator = runtime_memory.get_iterator(iter_id)
                iterator.value = 0
            else:
                iterator = runtime_memory.create_iterator(iter_id, 0)
            end_value = to_integer(solve_expression(line.attributes[cid_of['dc::end_value']],
                                                    runtime_memory, cid_of, dcd), cid_of)
            for i in range(end_value):
                for for_line in line.attributes[cid_of['dc::for_block']].agi_list().value:
                    try:
                        line_signal = process_line(for_line, runtime_memory, cid_of, dcd)
                    except DynamicCodeException as d:
                        d.line_cache = to_integer(for_line.attributes[cid_of['dc::line_index']], cid_of)
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
        if line.concept_id == cid_of['dcr::while']:
            loop_count = 0
            while solve_expression(line.attributes[cid_of['dc::expression_for_judging']],
                                   runtime_memory, cid_of, dcd).concept_id == cid_of['True']:
                loop_count += 1
                for while_line in line.attributes[cid_of['dc::while_block']].agi_list().value:
                    try:
                        line_signal = process_line(while_line, runtime_memory, cid_of, dcd)
                    except DynamicCodeException as d:
                        d.line_cache = to_integer(while_line.attributes[cid_of['dc::line_index']], cid_of)
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('normal')
                    if line_signal.signal_type == 'return':
                        return line_signal
                if loop_count == 1000:
                    raise LineException(to_integer(line.attributes[cid_of['dc::line_index']], cid_of),
                                        'While loop does not stop.')
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::break']:
            return LineSignal('break')
        if line.concept_id == cid_of['dcr::if']:
            expression_for_judging = solve_expression(line.attributes[cid_of['dc::expression_for_judging']],
                                                      runtime_memory, cid_of, dcd)
            if expression_for_judging.concept_id == cid_of['True']:
                for if_line in line.attributes[cid_of['dc::if_block']].agi_list().value:
                    try:
                        line_signal = process_line(if_line, runtime_memory, cid_of, dcd)
                    except DynamicCodeException as d:
                        d.line_cache = to_integer(if_line.attributes[cid_of['dc::line_index']], cid_of)
                        raise
                    except LineException:
                        raise
                    if line_signal.signal_type == 'break':
                        return LineSignal('break')
                    if line_signal.signal_type == 'return':
                        return line_signal
            else:
                elif_executed = False
                for elif_module in line.attributes[cid_of['dc::elif_modules']].value:
                    elif_expression = solve_expression(elif_module.attributes[cid_of['dc::expression_for_judging']],
                                                       runtime_memory, cid_of, dcd)
                    if elif_expression.concept_id == cid_of['True']:
                        for elif_line in elif_module.attributes[cid_of['dc::elif_block']].agi_list().value:
                            try:
                                line_signal = process_line(elif_line, runtime_memory, cid_of, dcd)
                            except DynamicCodeException as d:
                                d.line_cache = to_integer(elif_line.attributes[cid_of['dc::line_index']], cid_of)
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
                    for else_line in line.attributes[cid_of['dc::else_block']].agi_list().value:
                        try:
                            line_signal = process_line(else_line, runtime_memory, cid_of, dcd)
                        except DynamicCodeException as d:
                            d.line_cache = to_integer(else_line.attributes[cid_of['dc::line_index']], cid_of)
                            raise
                        except LineException:
                            raise
                        if line_signal.signal_type == 'break':
                            return LineSignal('break')
                        if line_signal.signal_type == 'return':
                            return line_signal
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::append']:
            target_list = solve_expression(line.attributes[cid_of['dc::target_list']], runtime_memory, cid_of, dcd)
            element = solve_expression(line.attributes[cid_of['dc::element']], runtime_memory, cid_of, dcd)
            if type(target_list) == AGIObject:
                target_list = target_list.agi_list()
            else:
                assert type(target_list) == AGIList
            target_list.append(element)
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::remove']:
            target_list = solve_expression(line.attributes[cid_of['dc::target_list']], runtime_memory, cid_of, dcd)
            if type(target_list) == AGIObject:
                target_list = target_list.agi_list()
            else:
                assert type(target_list) == AGIList
            while True:
                element_pos = find_element(target_list, line.attributes[cid_of['dc::expression_for_constraint']],
                                           runtime_memory, cid_of, dcd)
                if element_pos == -1:
                    break
                target_list.remove(element_pos)
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::request']:
            for reg_id in line.attributes[cid_of['dc::requested_registers']].value:
                reg_id_int = to_integer(reg_id, cid_of)
                raw_input = input('Dynamic code asks you to fill in reg' + str(reg_id_int) + '!\n')
                if raw_input.isdigit():
                    input_object = num_obj(int(raw_input), cid_of)
                else:
                    assert False
                if not runtime_memory.has_reg(reg_id_int):
                    runtime_memory.create_reg(reg_id_int, input_object)
                else:
                    runtime_memory.set_reg(reg_id_int, input_object)
            for provided_line in line.attributes[cid_of['dc::provided_block']].agi_list().value:
                try:
                    line_signal = process_line(provided_line, runtime_memory, cid_of, dcd)
                except DynamicCodeException as d:
                    d.line_cache = to_integer(provided_line.attributes[cid_of['dc::line_index']], cid_of)
                    raise
                except LineException:
                    raise
                assert line_signal.signal_type != 'break'
                if line_signal.signal_type == 'return':
                    return line_signal
            if solve_expression(line.attributes[cid_of['dc::expression_for_constraint']],
                                runtime_memory, cid_of, dcd).concept_id != cid_of['True']:
                raise LineException(to_integer(line.attributes[cid_of['dc::line_index']], cid_of),
                                    'Your inputs do not satisfy the constraints.')
            return LineSignal('normal')
        if line.concept_id == cid_of['dcr::call_none_return_func']:
            code_id = line.attributes[cid_of['dc::function_name']].concept_id
            function_params = list()
            for param in line.attributes[cid_of['dc::function_params']].value:
                function_params.append(solve_expression(param, runtime_memory, cid_of, dcd))
            function_params = AGIList(function_params)
            if is_code_dynamic(code_id, dcd, cid_of):
                try:
                    result = run_dynamic_code(code_id, function_params, cid_of, dcd)
                except DynamicCodeException as d:
                    d.line_cache = to_integer(line.attributes[cid_of['dc::line_index']], cid_of)
                    raise

            else:
                try:
                    result = run_hardcoded_code(code_id, function_params, cid_of, dcd)
                except HardcodedCodeException as h:
                    h.line = to_integer(line.attributes[cid_of['dc::line_index']], cid_of)
                    raise
            assert result.concept_id == cid_of['None']
            return LineSignal('normal')
        print(line.concept_id)
        assert False
    except ExpressionException as e:
        raise LineException(to_integer(line.attributes[cid_of['dc::line_index']], cid_of), e.description)
    except StructureException as s:
        raise LineException(to_integer(line.attributes[cid_of['dc::line_index']], cid_of), s.description)
    except DynamicCodeException as d:
        if d.line_cache is None:
            d.line_cache = to_integer(line.attributes[cid_of['dc::line_index']], cid_of)
        raise
    except HardcodedCodeException as h:
        h.line = to_integer(line.attributes[cid_of['dc::line_index']], cid_of)
        raise
    except LineException:
        raise


def run_dynamic_code(code_id: int, input_params: AGIList, cid_of, dcd) -> AGIObject:
    code_object = dcd.get_code(code_id)
    runtime_memory = RuntimeMemory()
    for i, input_param in enumerate(input_params.value):
        runtime_memory.inputs.append(Input(i, input_param))
    for line in code_object.agi_list().value:
        try:
            line_signal = process_line(line, runtime_memory, cid_of, dcd)
        except LineException as l:
            raise DynamicCodeException(DynamicExceptionInfo(code_id,
                                                            input_params.value, l.line, runtime_memory), l.description)
        except DynamicCodeException as d:
            d.call_stacks.append(DynamicExceptionInfo(code_id, input_params.value, d.line_cache, runtime_memory))
            d.line_cache = None
            raise
        except HardcodedCodeException as h:
            d = DynamicCodeException(HardcodedExceptionInfo(h.function_name), h.description)
            d.call_stacks.append(DynamicExceptionInfo(code_id, input_params.value, h.line, runtime_memory))
            raise d
        assert line_signal.signal_type != 'break'
        if line_signal.signal_type == 'return':
            return line_signal.signal_value
    return AGIObject(cid_of['None'])
