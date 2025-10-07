from .logs import my_logger


class NoInstantiable:
    """Class that can't be instantiable"""
    def __new__(cls) -> None:
        msg: str = f'Class "{cls.__name__}" is not instantiable.'
        my_logger.critical(msg)
        raise SyntaxError(msg)
