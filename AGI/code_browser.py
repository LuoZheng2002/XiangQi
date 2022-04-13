from AGI.struct import AGIObject, AGIList
from AGI.objects import to_integer
import pickle
from AGI.code_generator import number_to_letter
from AGI.translate_struct import print_obj
from AGI.dynamic_code_getter import get_dynamic_code
add_line_index = True


def translate_expression(expr: AGIObject, cid_of, cid_reverse) -> str:
    if expr.concept_id == cid_of['dcr::input']:
        return 'input' + str(to_integer(expr.attributes[cid_of['dc::index']], cid_of))
    if expr.concept_id == cid_of['dcr::reg']:
        return 'reg' + str(to_integer(expr.attributes[cid_of['dc::index']], cid_of))
    if expr.concept_id == cid_of['dcr::iterator']:
        iter_id = to_integer(expr.attributes[cid_of['dc::index']], cid_of)
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
        function_name = cid_reverse[expr.attributes[cid_of['dc::function_name']].concept_id]
        function_params = expr.attributes[cid_of['dc::function_params']].value
        if function_name in special_functions.keys():
            param1 = translate_expression(function_params[0], cid_of, cid_reverse)
            param2 = translate_expression(function_params[1], cid_of, cid_reverse)
            return '(' + param1 + ' ' + special_functions[function_name] + ' ' + param2 + ')'
        if function_name == 'func::logic_not':
            return 'not ' + translate_expression(function_params[0], cid_of, cid_reverse)
        result = "'" + function_name + "'("
        for function_param in function_params:
            result += translate_expression(function_param, cid_of, cid_reverse) + ', '
        if function_params:
            result = result[:-2]
        result += ')'
        return result
    if expr.concept_id == cid_of['dcr::concept_instance']:
        result = "'" + cid_reverse[expr.attributes[cid_of['dc::concept_name']].concept_id] + "'"
        return result
    if expr.concept_id == cid_of['dcr::size']:
        target_list = translate_expression(expr.attributes[cid_of['dc::target_list']], cid_of, cid_reverse)
        result = target_list + '.size'
        return result
    if expr.concept_id == cid_of['dcr::get_member']:
        target_object = translate_expression(expr.attributes[cid_of['dc::target_object']], cid_of, cid_reverse)
        member_name = cid_reverse[expr.attributes[cid_of['dc::member_name']].concept_id]
        result = target_object + ".'" + member_name + "'"
        return result
    if expr.concept_id == cid_of['dcr::at']:
        target_list = translate_expression(expr.attributes[cid_of['dc::target_list']], cid_of, cid_reverse)
        element_index = translate_expression(expr.attributes[cid_of['dc::element_index']], cid_of, cid_reverse)
        result = target_list + '[' + element_index + ']'
        return result
    if expr.concept_id == cid_of['dcr::find']:
        target_list = translate_expression(expr.attributes[cid_of['dc::target_list']], cid_of, cid_reverse)
        expression = translate_expression(expr.attributes[cid_of['dc::expression_for_constraint']], cid_of, cid_reverse)
        result = target_list + '.find(' + expression + ')'
        return result
    if expr.concept_id == cid_of['dcr::exist']:
        target_list = translate_expression(expr.attributes[cid_of['dc::target_list']], cid_of, cid_reverse)
        expression = translate_expression(expr.attributes[cid_of['dc::expression_for_constraint']], cid_of, cid_reverse)
        result = target_list + '.exist(' + expression + ')'
        return result
    if expr.concept_id == cid_of['dcr::count']:
        target_list = translate_expression(expr.attributes[cid_of['dc::target_list']], cid_of, cid_reverse)
        expression = translate_expression(expr.attributes[cid_of['dc::expression_for_constraint']], cid_of, cid_reverse)
        result = target_list + '.count(' + expression + ')'
        return result
    if expr.concept_id == cid_of['dcr::target']:
        return 'target'
    if expr.concept_id == cid_of['dcr::constexpr']:
        value = expr.attributes[cid_of['value']]
        if value.concept_id == cid_of['natural_number']:
            return str(to_integer(value, cid_of))
        else:
            return cid_reverse[value.concept_id]
    print(cid_reverse[expr.concept_id])
    assert False


def add_indentation(line: str, indentation_count: int, line_index=0, new_line=True) -> str:
    for i in range(indentation_count):
        line = '    ' + line
    if add_line_index:
        if line_index == 0:
            line = '        ' + line
        else:
            line = str(line_index).ljust(8, ' ') + line
    if new_line:
        line += '\n'
    return line


def translate_line(line: AGIObject, cid_of, cid_reverse, indentation_count=0) -> str:
    if line.concept_id == cid_of['dcr::assign'] or line.concept_id == cid_of['dcr::assign_as_reference']:
        if line.concept_id == cid_of['dcr::assign']:
            sign = ' = '
        else:
            sign = ' &= '
        result = translate_expression(line.attributes[cid_of['dc::left_value']], cid_of, cid_reverse) \
                 + sign + translate_expression(line.attributes[cid_of['dc::right_value']], cid_of, cid_reverse)
        return add_indentation(result, indentation_count, to_integer(line.attributes[cid_of['dc::line_index']], cid_of))
    if line.concept_id == cid_of['dcr::return']:
        result = 'return ' + translate_expression(line.attributes[cid_of['dc::return_value']], cid_of, cid_reverse)
        return add_indentation(result, indentation_count, to_integer(line.attributes[cid_of['dc::line_index']], cid_of))
    if line.concept_id == cid_of['dcr::assert']:
        result = 'assert ' + translate_expression(line.attributes[cid_of['dc::assert_expression']], cid_of, cid_reverse)
        return add_indentation(result, indentation_count, to_integer(line.attributes[cid_of['dc::line_index']], cid_of))
    if line.concept_id == cid_of['dcr::for']:
        iter_index = to_integer(line.attributes[cid_of['dc::iterator_index']], cid_of)
        if iter_index in number_to_letter.keys():
            iterator_name = number_to_letter[iter_index]
        else:
            iterator_name = 'iter' + str(iter_index)
        end_value = translate_expression(line.attributes[cid_of['dc::end_value']], cid_of, cid_reverse)
        result = 'for ' + iterator_name + ' in range(' + end_value + '):'
        result = add_indentation(result, indentation_count,
                                 to_integer(line.attributes[cid_of['dc::line_index']], cid_of))
        assert line.attributes[cid_of['dc::for_block']].concept_id == cid_of['dc::sub_block']
        for_block_list = line.attributes[cid_of['dc::for_block']].attributes[cid_of['dc::lines']]
        assert type(for_block_list) == AGIList
        for for_line in for_block_list.value:
            result += translate_line(for_line, cid_of, cid_reverse, indentation_count + 1)
        return result
    if line.concept_id == cid_of['dcr::while']:
        expression_for_judging = translate_expression(line.attributes[cid_of['dc::expression_for_judging']], cid_of,
                                                      cid_reverse)
        result = 'while ' + expression_for_judging + ':'
        result = add_indentation(result, indentation_count,
                                 to_integer(line.attributes[cid_of['dc::line_index']], cid_of))
        assert line.attributes[cid_of['dc::while_block']].concept_id == cid_of['dc::sub_block']
        while_block_list = line.attributes[cid_of['dc::while_block']].attributes[cid_of['dc::lines']]
        assert type(while_block_list) == AGIList
        for while_line in while_block_list.value:
            result += translate_line(while_line, cid_of, cid_reverse, indentation_count + 1)
        return result
    if line.concept_id == cid_of['dcr::break']:
        result = 'break'
        return add_indentation(result, indentation_count, to_integer(line.attributes[cid_of['dc::line_index']], cid_of))
    if line.concept_id == cid_of['dcr::if']:
        expression_for_judging = translate_expression(line.attributes[cid_of['dc::expression_for_judging']], cid_of,
                                                      cid_reverse)
        result = 'if ' + expression_for_judging + ':'
        result = add_indentation(result, indentation_count,
                                 to_integer(line.attributes[cid_of['dc::line_index']], cid_of))
        assert line.attributes[cid_of['dc::if_block']].concept_id == cid_of['dc::sub_block']
        if_block_list = line.attributes[cid_of['dc::if_block']].attributes[cid_of['dc::lines']]
        assert type(if_block_list) == AGIList
        for if_line in if_block_list.value:
            result += translate_line(if_line, cid_of, cid_reverse, indentation_count + 1)
        assert type(line.attributes[cid_of['dc::elif_modules']]) == AGIList
        for elif_module in line.attributes[cid_of['dc::elif_modules']].value:
            assert elif_module.concept_id == cid_of['dc::elif_module']
            elif_expression = translate_expression(elif_module.attributes[cid_of['dc::expression_for_judging']], cid_of,
                                                   cid_reverse)
            elif_result = 'elif ' + elif_expression + ':'
            elif_result = add_indentation(elif_result, indentation_count,
                                          to_integer(elif_module.attributes[cid_of['dc::line_index']], cid_of))
            result += elif_result
            assert elif_module.attributes[cid_of['dc::elif_block']].concept_id == cid_of['dc::sub_block']
            elif_block_list = elif_module.attributes[cid_of['dc::elif_block']].attributes[cid_of['dc::lines']]
            assert type(elif_block_list) == AGIList
            for elif_line in elif_block_list.value:
                result += translate_line(elif_line, cid_of, cid_reverse, indentation_count + 1)
        assert line.attributes[cid_of['dc::else_block']].concept_id == cid_of['dc::sub_block']
        else_block_list = line.attributes[cid_of['dc::else_block']].attributes[cid_of['dc::lines']]
        assert type(else_block_list) == AGIList
        if else_block_list.value:
            result += add_indentation('else:', indentation_count)
            for else_line in else_block_list.value:
                result += translate_line(else_line, cid_of, cid_reverse, indentation_count + 1)
        return result
    if line.concept_id == cid_of['dcr::append'] or line.concept_id == cid_of['dcr::remove']:
        target_list = translate_expression(line.attributes[cid_of['dc::target_list']], cid_of, cid_reverse)
        if line.concept_id == cid_of['dcr::append']:
            element = translate_expression(line.attributes[cid_of['dc::element']], cid_of, cid_reverse)
            word = '.append('
        else:
            element = translate_expression(line.attributes[cid_of['dc::expression_for_constraint']], cid_of,
                                           cid_reverse)
            word = '.remove('
        result = target_list + word + element + ')'
        return add_indentation(result, indentation_count,
                               to_integer(line.attributes[cid_of['dc::line_index']], cid_of))
    if line.concept_id == cid_of['dcr::request']:
        result = 'request '
        assert type(line.attributes[cid_of['dc::requested_registers']]) == AGIList
        for reg_id in line.attributes[cid_of['dc::requested_registers']].value:
            result += 'reg' + str(to_integer(reg_id, cid_of)) + ', '
        result += 's.t.{'
        result += translate_expression(line.attributes[cid_of['dc::expression_for_constraint']], cid_of, cid_reverse)
        result += '}, provided:'
        result = add_indentation(result, indentation_count,
                                 to_integer(line.attributes[cid_of['dc::line_index']], cid_of))
        assert line.attributes[cid_of['dc::provided_block']].concept_id == cid_of['dc::sub_block']
        provided_block_list = line.attributes[cid_of['dc::provided_block']].attributes[cid_of['dc::lines']]
        assert type(provided_block_list) == AGIList
        for provided_line in provided_block_list.value:
            result += translate_line(provided_line, cid_of, cid_reverse, indentation_count + 1)
        return result
    if line.concept_id == cid_of['dcr::call_none_return_func']:
        result = "'" + cid_reverse[line.attributes[cid_of['dc::function_name']].concept_id] + "'("
        function_params = line.attributes[cid_of['dc::function_params']].value
        for function_param in function_params:
            result += translate_expression(function_param, cid_of, cid_reverse) + ', '
        if function_params:
            result = result[:-2]
        result += ')'
        return add_indentation(result, indentation_count,
                               to_integer(line.attributes[cid_of['dc::line_index']], cid_of))
    assert False


def translate_code(code_name: str or int, cid_of, cid_reverse):
    if type(code_name) == str:
        code_name = cid_of[code_name]
    result = str()
    target_file = open('Formatted/' + str(code_name) + '.txt', 'rb')
    code = pickle.load(target_file)
    for line in code.attributes[cid_of['dc::lines']].value:
        result += translate_line(line, cid_of, cid_reverse)
    # print('original:')
    # print_obj(code, cid_reverse)
    # print('visualized:')
    print(result)




