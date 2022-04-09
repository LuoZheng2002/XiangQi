from AGI.struct import AGIObject, AGIList
from AGI.concept_ids import cid_of, cid_reverse
from AGI.objects import num_obj, obj
from AGI.translate_struct import print_obj
from AGI.objects import to_integer
import pickle
from AGI.code_generator import number_to_letter
from AGI.code_getter import dynamic_code_dict
add_line_index = True


def translate_expression(expr: AGIObject) -> str:
    if expr.concept_id == cid_of['dcr::input']:
        return 'input' + str(to_integer(expr.attribute('dc::index')))
    if expr.concept_id == cid_of['dcr::reg']:
        return 'reg' + str(to_integer(expr.attribute('dc::index')))
    if expr.concept_id == cid_of['dcr::iterator']:
        iter_id = to_integer(expr.attribute('dc::index'))
        if iter_id in number_to_letter.keys():
            return number_to_letter[iter_id]
        return 'iter' + str(iter_id)
    if expr.concept_id == cid_of['dcr::call']:
        special_functions = {'func::logic_and': 'and',
                             'func::logic_or': 'or',
                             'func::compare_concepts': '==',
                             'func::math_equal': '===',
                             'func::greater_than': '>',
                             'func::less_than': '<',
                             'func::greater_than_or_equal_to': '>=',
                             'func::less_than_or_equal_to': '<=',
                             'func::sum': '+',
                             'func::difference': '-'}
        function_name = cid_reverse[expr.attribute('dc::function_name').concept_id]
        function_params = expr.attribute('dc::function_params').value
        if function_name in special_functions.keys():
            param1 = translate_expression(function_params[0])
            param2 = translate_expression(function_params[1])
            return param1 + ' ' + special_functions[function_name] + ' ' + param2
        if function_name == 'func::logic_not':
            return 'not ' + translate_expression(function_params[0])
        result = "'" + function_name + "'("
        for function_param in function_params:
            result += translate_expression(function_param) + ', '
        if function_params:
            result = result[:-2]
        result += ')'
        return result
    if expr.concept_id == cid_of['dcr::concept_instance']:
        result = "'" + cid_reverse[expr.attribute('dc::concept_name').concept_id] + "'"
        return result
    if expr.concept_id == cid_of['dcr::size']:
        target_list = translate_expression(expr.attribute('dc::target_list'))
        result = target_list + '.size'
        return result
    if expr.concept_id == cid_of['dcr::get_member']:
        target_object = translate_expression(expr.attribute('dc::target_object'))
        member_name = cid_reverse[expr.attribute('dc::member_name').concept_id]
        result = target_object + ".'" + member_name + "'"
        return result
    if expr.concept_id == cid_of['dcr::at']:
        target_list = translate_expression(expr.attribute('dc::target_list'))
        element_index = translate_expression(expr.attribute('dc::element_index'))
        result = target_list + '[' + element_index + ']'
        return result
    if expr.concept_id == cid_of['dcr::find']:
        target_list = translate_expression(expr.attribute('dc::target_list'))
        expression = translate_expression(expr.attribute('dc::expression_for_constraint'))
        result = target_list + '.find(' + expression + ')'
        return result
    if expr.concept_id == cid_of['dcr::exist']:
        target_list = translate_expression(expr.attribute('dc::target_list'))
        expression = translate_expression(expr.attribute('dc::expression_for_constraint'))
        result = target_list + '.exist(' + expression + ')'
        return result
    if expr.concept_id == cid_of['dcr::count']:
        target_list = translate_expression(expr.attribute('dc::target_list'))
        expression = translate_expression(expr.attribute('dc::expression_for_constraint'))
        result = target_list + '.count(' + expression + ')'
        return result
    if expr.concept_id == cid_of['dcr::target']:
        return 'target'
    if expr.concept_id == cid_of['dcr::constexpr']:
        value = expr.attribute('value')
        if value.concept_id == cid_of['natural_number']:
            return str(to_integer(value))
        else:
            return cid_reverse[value.concept_id]
    print(cid_reverse[expr.concept_id])
    assert False


def add_indentation(line: str, indentation_count: int, line_index=0) -> str:
    for i in range(indentation_count):
        line = '    ' + line
    if add_line_index:
        if line_index == 0:
            line = '        ' + line
        else:
            line = str(line_index).ljust(8, ' ') + line
    line += '\n'
    return line


def translate_line(line: AGIObject, indentation_count=0) -> str:
    if line.concept_id == cid_of['dcr::assign'] or line.concept_id == cid_of['dcr::assign_as_reference']:
        if line.concept_id == cid_of['dcr::assign']:
            sign = ' = '
        else:
            sign = ' &= '
        result = translate_expression(line.attribute('dc::left_value')) \
                 + sign + translate_expression(line.attribute('dc::right_value'))
        return add_indentation(result, indentation_count, to_integer(line.attribute('dc::line_index')))
    if line.concept_id == cid_of['dcr::return']:
        result = 'return ' + translate_expression(line.attribute('dc::return_value'))
        return add_indentation(result, indentation_count, to_integer(line.attribute('dc::line_index')))
    if line.concept_id == cid_of['dcr::assert']:
        result = 'assert ' + translate_expression(line.attribute('dc::assert_expression'))
        return add_indentation(result, indentation_count, to_integer(line.attribute('dc::line_index')))
    if line.concept_id == cid_of['dcr::for']:
        iter_index = to_integer(line.attribute('dc::iterator_index'))
        if iter_index in number_to_letter.keys():
            iterator_name = number_to_letter[iter_index]
        else:
            iterator_name = 'iter' + str(iter_index)
        end_value = translate_expression(line.attribute('dc::end_value'))
        result = 'for ' + iterator_name + ' in range(' + end_value + '):'
        result = add_indentation(result, indentation_count, to_integer(line.attribute('dc::line_index')))
        assert line.attribute('dc::for_block').concept_id == cid_of['dc::sub_block']
        for_block_list = line.attribute('dc::for_block').attribute('dc::lines')
        assert type(for_block_list) == AGIList
        for for_line in for_block_list.value:
            result += translate_line(for_line, indentation_count + 1)
        return result
    if line.concept_id == cid_of['dcr::while']:
        expression_for_judging = translate_expression(line.attribute('dc::expression_for_judging'))
        result = 'while ' + expression_for_judging + ':'
        result = add_indentation(result, indentation_count, to_integer(line.attribute('dc::line_index')))
        assert line.attribute('dc::while_block').concept_id == cid_of['dc::sub_block']
        while_block_list = line.attribute('dc::while_block').attribute('dc::lines')
        assert type(while_block_list) == AGIList
        for while_line in while_block_list.value:
            result += translate_line(while_line, indentation_count + 1)
        return result
    if line.concept_id == cid_of['dcr::break']:
        result = 'break'
        return add_indentation(result, indentation_count, to_integer(line.attribute('dc::line_index')))
    if line.concept_id == cid_of['dcr::if']:
        expression_for_judging = translate_expression(line.attribute('dc::expression_for_judging'))
        result = 'if ' + expression_for_judging + ':'
        result = add_indentation(result, indentation_count, to_integer(line.attribute('dc::line_index')))
        assert line.attribute('dc::if_block').concept_id == cid_of['dc::sub_block']
        if_block_list = line.attribute('dc::if_block').attribute('dc::lines')
        assert type(if_block_list) == AGIList
        for if_line in if_block_list.value:
            result += translate_line(if_line, indentation_count + 1)
        assert type(line.attribute('dc::elif_modules')) == AGIList
        for elif_module in line.attribute('dc::elif_modules').value:
            assert elif_module.concept_id == cid_of['dc::elif_module']
            elif_expression = translate_expression(elif_module.attribute('dc::expression_for_judging'))
            elif_result = 'elif ' + elif_expression + ':'
            elif_result = add_indentation(elif_result, indentation_count,
                                          to_integer(elif_module.attribute('dc::line_index')))
            result += elif_result
            assert elif_module.attribute('dc::elif_block').concept_id == cid_of['dc::sub_block']
            elif_block_list = elif_module.attribute('dc::elif_block').attribute('dc::lines')
            assert type(elif_block_list) == AGIList
            for elif_line in elif_block_list.value:
                result += translate_line(elif_line, indentation_count + 1)
        assert line.attribute('dc::else_block').concept_id == cid_of['dc::sub_block']
        else_block_list = line.attribute('dc::else_block').attribute('dc::lines')
        assert type(else_block_list) == AGIList
        if else_block_list.value:
            result += add_indentation('else:', indentation_count)
            for else_line in else_block_list.value:
                result += translate_line(else_line, indentation_count + 1)
        return result
    if line.concept_id == cid_of['dcr::append'] or line.concept_id == cid_of['dcr::remove']:
        target_list = translate_expression(line.attribute('dc::target_list'))
        if line.concept_id == cid_of['dcr::append']:
            element = translate_expression(line.attribute('dc::element'))
            word = '.append('
        else:
            element = translate_expression(line.attribute('dc::expression_for_constraint'))
            word = '.remove('
        result = target_list + word + element + ')'
        return add_indentation(result, indentation_count, to_integer(line.attribute('dc::line_index')))
    if line.concept_id == cid_of['dcr::request']:
        result = 'request '
        assert type(line.attribute('dc::requested_registers')) == AGIList
        for reg_id in line.attribute('dc::requested_registers').value:
            result += 'reg' + str(to_integer(reg_id)) + ', '
        result += 's.t.{'
        result += translate_expression(line.attribute('dc::expression_for_constraint'))
        result += '}, provided:'
        result = add_indentation(result, indentation_count, to_integer(line.attribute('dc::line_index')))
        assert line.attribute('dc::provided_block').concept_id == cid_of['dc::sub_block']
        provided_block_list = line.attribute('dc::provided_block').attribute('dc::lines')
        assert type(provided_block_list) == AGIList
        for provided_line in provided_block_list.value:
            result += translate_line(provided_line, indentation_count + 1)
        return result
    if line.concept_id == cid_of['dcr::call_none_return_function']:
        result = "'" + cid_reverse[line.attribute('dc::function_name').concept_id] + "'("
        function_params = line.attribute('dc::function_params').value
        for function_param in function_params:
            result += translate_expression(function_param) + ', '
        if function_params:
            result = result[:-2]
        result += ')'
        return add_indentation(result, indentation_count, to_integer(line.attribute('dc::line_index')))
    assert False


def translate_code(code_name: str or int):
    if type(code_name) == int:
        code_name = dynamic_code_dict[code_name]
    result = str()
    target_file = open('Formatted/' + code_name + '.txt', 'rb')
    code = pickle.load(target_file)
    for line in code.attribute('dc::lines').value:
        result += translate_line(line)
    print(result)
