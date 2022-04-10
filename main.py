from Exception.dynamic_code_exception import DynamicCodeException, show_dynamic_code_exception
from Concept.concept_manager import summon_concepts

cid_of, cid_reverse = summon_concepts('Concept/concepts.txt')
try:
    print(cid_of)
except DynamicCodeException as d:
    show_dynamic_code_exception(d, cid_of, cid_reverse)
