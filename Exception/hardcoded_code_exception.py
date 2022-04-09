from AGI.concept_ids import cid_reverse
from AGI.translate_struct import print_obj
from AGI.code_browser import translate_code


class HardcodedCodeException(BaseException):
    def __init__(self, description, function_name):
        self.description = description
        self.function_name = function_name
        self.line = None



