from Exception.dynamic_code_exception import DynamicCodeException, show_dynamic_code_exception
from Concept.concept_manager import summon_concepts
from AGI.code_browser import translate_code
cid_of, cid_reverse = summon_concepts('Concept/concepts.txt')
try:
    translate_code('func::compare_natural_numbers', cid_of, cid_reverse)
except DynamicCodeException as d:
    show_dynamic_code_exception(d, cid_of, cid_reverse)
