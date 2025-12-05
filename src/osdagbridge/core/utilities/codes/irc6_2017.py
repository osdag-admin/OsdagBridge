from .base import BaseCode

class IRC62017(BaseCode):
    code_name = "IRC:6-2017"

    def factored_load(self, load):
        return 1.5 * load
