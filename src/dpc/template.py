

class Template:

    def __init_subclass__(cls):
        pass

    @classmethod
    def _register() -> None:
        """Registers this class to a pack, called within
        `pack.add_template()`
        """
        pass

    @classmethod
    def _render() -> None:
        pass