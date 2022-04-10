class HardcodedCodeException(BaseException):
    def __init__(self, description, function_name):
        self.description = description
        self.function_name = function_name
        self.line = None



