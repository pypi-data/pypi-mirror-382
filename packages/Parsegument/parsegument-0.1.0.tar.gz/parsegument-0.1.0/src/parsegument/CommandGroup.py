from typing import Union, Callable
from inspect import signature
from .Node import Node
from .Command import Command
from .error import NodeDoesNotExist

class CommandGroup(Node):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.children = {}

    def add_child(self, node:Union[Command, "CommandGroup"]) -> None:
        self.children[node.name] = node

    def command(self, func: Callable):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        print(signature(func).parameters)
        return wrapper

    def execute(self, nodes:list[str]):
        child = self.children.get(nodes[0])
        if not child:
            raise NodeDoesNotExist
        return child.execute(nodes[1:])
