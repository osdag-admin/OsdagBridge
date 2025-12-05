class BaseCode:
    """Base class for IRC/IS code implementations."""
    code_name = "Unknown"

    def factored_load(self, load):
        raise NotImplementedError
