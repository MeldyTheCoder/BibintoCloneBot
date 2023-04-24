from types import FunctionType


class ReprModel:

    @property
    def data(self) -> dict:
        return {key.replace(f'_{self.__class__.__name__}__', ''): val for key, val in self.__dict__.items() if
                not isinstance(val, FunctionType)}

    def __str__(self):
        return f"{self.__class__.__name__} -> {str(self.data)}"

    def __repr__(self):
        return f"{self.__class__.__name__} -> {self.data}"
