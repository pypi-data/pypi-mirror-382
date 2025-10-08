from __future__ import annotations
from typing import Union
from .error import NodeDoesNotExist, ArgumentGroupNotFound, MultipleChildrenFound

if annotations:
    from .Arguments import Argument
    from .CommandGroup import CommandGroup
    from .Command import Command


class Parsegumenter:
    def __init__(self) -> None:
        self.children = {}

    @staticmethod
    def parse_string(string: str) -> list:
        if not string: return []
        opened_quotation = False
        saved_index = 0
        arguments = []
        for idx, letter in enumerate(string):
            if letter == '"' or letter == "'":
                opened_quotation = not opened_quotation
                if opened_quotation:
                    saved_index = idx + 1
                else:
                    arguments.append(string[saved_index:idx])
                    saved_index = idx + 1
                continue
            if letter == ' ' and not opened_quotation:
                arguments.append(string[saved_index:idx])
                saved_index = idx + 1
                continue
        if string[saved_index:]:
            arguments.append(string[saved_index:])
        arguments = [i for i in arguments if i != ""]
        return arguments

    def add_child(self, child: Union[CommandGroup, Command]):
        if child.name in [i.name for i in self.children]:
            return False
        self.children[child.name] = child
        return True

    def execute(self, string:str):
        parsed = self.parse_string(string)
        child_name = parsed[0]
        arguments = parsed[1:]
        child_command = self.children.get(child_name)
        if not child_command:
            raise NodeDoesNotExist
        return child_command.execute(arguments)

