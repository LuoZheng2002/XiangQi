import pickle
concepts = [
    # 基本概念
    'None',
    'True',
    'False',
    'Fail',
    'id',
    'name',
    'content',
    'value',
    # 普通概念
    'list',
    'digit',
    'natural_number',
    'vector',
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    'greater_than',
    'less_than',
    'math_equal',
    # 可执行代码相关概念
    'dynamic_code',
    'dc::lines',
    'dc::sub_block',
    # 语句头
    'dcr::assign',  #
    'dcr::assign_as_reference',  #
    'dcr::return',  #
    'dcr::assert',  #
    'dcr::for',  #
    'dcr::while',  #
    'dcr::break',  #
    'dcr::if',  #
    'dcr::append',  #
    'dcr::remove',  #
    'dcr::request',  #
    'dcr::call_none_return_func',  #
    # 表达式头
    'dcr::input',  #
    'dcr::reg',  #
    'dcr::iterator',  #
    'dcr::call',  #
    'dcr::concept_instance',  #
    'dcr::size',
    'dcr::get_member',
    'dcr::at',
    'dcr::find',
    'dcr::exist',
    'dcr::count',
    'dcr::target',
    'dcr::constexpr',
    # 参数名称
    'dc::left_value',
    'dc::right_value',
    'dc::return_value',
    'dc::assert_expression',
    'dc::index',
    'dc::function_name',
    'dc::function_params',
    'dc::concept_name',
    'dc::target_list',
    'dc::target_object',
    'dc::member_name',
    'dc::expression_for_constraint',
    'dc::expression_for_judging',
    'dc::iterator_index',
    'dc::end_value',
    'dc::for_block',
    'dc::while_block',
    'dc::if_block',
    'dc::elif_modules',
    'dc::elif_module',
    'dc::elif_block',
    'dc::else_block',
    'dc::element',
    'dc::element_index',
    'dc::requested_registers',
    'dc::provided_block',
    'dc::line_index',
    # reg, iterator容器
    'dc::input_container',
    'dc::register_container',
    'dc::iterator_container',
    'dc::runtime_inputs',
    'dc::runtime_registers',
    'dc::runtime_iterators',
    'dc::runtime_memory',
    'dc::line_signal_normal',
    'dc::line_signal_break',
    'dc::line_signal_return',
    'dc::line_return_value',
    # 可执行代码
    # 硬编码代码
    'func::compare_concepts',
    'func::logic_and',
    'func::logic_or',
    'func::logic_not',
    'func::is_natural_number_single_digit',
    'func::compare_single_digit_natural_numbers',
    'func::sum',
    'func::difference',
    'func::get_object_member',
    'func::set_object_member',
    'func::remove_element_by_index',
    'func::get_input_object',
    'func::is_code_dynamic',
    'func::run_hardcoded_code',
    'func::get_dynamic_code_object',
    'func::create_concept_instance',
    # 动态代码
    'func::digit_to_natural_number',
    'func::compare_natural_numbers',
    'func::math_equal',
    'func::greater_than',
    'func::less_than',
    'func::greater_than_or_equal_to',
    'func::less_than_or_equal_to',
    'func::test',
    'func::batch_logic_and',
    'func::batch_logic_or',
    'func::max',
    'func::min',
    'func::run_dynamic_code_object',
    'func::process_line',
    'func::solve_expression',
    'func::remove_one_element',
    'func::increment',
    # 博弈问题策略接口
    'interface::find_winning_determining_variables_find_variable_changing_code',
    'interface_member::winning_determining_variables',

    # 回合制博弈问题相关概念
    'tb_game::game',
    'tb_game::chessboard',
    'tb_game::rule',
    'tb_game::winning_criteria',
    'tb_game::teams',
    'tb_game::occupations',
    'tb_game::who_is_next_func',
    'tb_game::my_team_id',
    'tb_game::end_game_func',
    'tb_game::end_game_benefits',
    'tb_game::team',
    'tb_game::players',
    'tb_game::end_game_benefit_id',
    'tb_game::occupation',
    'tb_game::operation_func',
    'tb_game::end_game_benefit',
    'tb_game::benefit_func',
    'tb_game::player',
    'tb_game::occupation_id',
    # 下面是在解决博弈问题时临时生成的概念id
    'xq::chessboard',
    'xq::pieces',
    'xq::piece',
    'xq::piece_owner',
    'xq::piece_name',
    'xq::position',
    'xq::Che',
    'xq::Ma',
    'xq::Xiang',
    'xq::Shi',
    'xq::Jiang',
    'xq::Pao',
    'xq::Bing',
    'xq::whose_turn',
    'xq::red_team',
    'xq::black_team',
    'xq::red_player',
    'xq::black_player',
    'xq::player_occupation',
    'xq::player_benefit',
]


def generate_concept_ids(concept_names):
    concept_ids = dict()
    file = open('concepts.txt', 'rb')
    concept_database = pickle.load(file)
    file.close()
    for concept in concept_database.concepts:
        concept_ids.update({concept.debug_description: concept.concept_id})
    return concept_ids



