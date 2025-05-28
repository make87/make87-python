from abc import ABC


class PeripheralBase(ABC):
    def __init__(self, name: str):
        self.name = name
