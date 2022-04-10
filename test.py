from Exception.dynamic_code_exception import DynamicCodeException, show_dynamic_code_exception
from Concept.concept_manager import summon_concepts
from AGI.code_generator import generate_code

cid_of, cid_reverse = summon_concepts('Concept/concepts.txt')
try:
    name = input('input the function name:\n')
    generate_code(name, cid_of)
except DynamicCodeException as d:
    show_dynamic_code_exception(d, cid_of, cid_reverse)



