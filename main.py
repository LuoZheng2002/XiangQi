from AGI.code_driver import run_dynamic_code
from AGI.struct import AGIObject,AGIList
from AGI.concept_ids import cid_of
from Exception.dynamic_code_exception import DynamicCodeException
try:
    result = run_dynamic_code(cid_of['test'], )
except DynamicCodeException as d:
    d.show()
