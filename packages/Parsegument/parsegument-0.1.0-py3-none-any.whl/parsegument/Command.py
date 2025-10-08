from typing import Callable, Union
from .Node import Node
from .Arguments import Argument, Operand, Flag
import inspect
from .utils.parser import node_type, parse_operand, convert_string_to_result

class Command(Node):
    def __init__(self, name: str, executable: Callable) -> None:
        super().__init__(name)
        self.arguments: Union[dict[str, list[Union[Argument, Operand, Flag, None]]], dict[str, dict[str, Union[Argument, Operand, Flag, None]]]] = {
            "args": [],
            "kwargs": {}
                          }
        self.executable = executable

    def add_node(self, arg: Union[Argument, Operand, Flag]) -> None:
        if type(arg) == Argument:
            self.arguments["args"].append(arg)
        elif type(arg) == Operand:
            self.arguments["kwargs"][arg.name] = arg
        elif type(arg) == Flag:
            self.arguments["kwargs"][arg.name] = arg

    def execute(self, nodes:list[str]):
        args_length = len(self.arguments["args"])
        args = nodes[:args_length]
        args = [convert_string_to_result(i, self.arguments["args"][idx].arg_type) for idx, i in enumerate(args)]
        kwargs_strings = nodes[args_length:]
        kwargs = {}
        for kwarg_string in kwargs_strings:
            type_of_node = node_type(kwarg_string)
            if type_of_node == "Flag":
                node_arguments = self.arguments["kwargs"][kwarg_string[1:]]
                kwargs[kwarg_string[1:]] = True
                continue
            elif type_of_node == "Operand":
                name, value = parse_operand(kwarg_string)
                node_arguments = self.arguments["kwargs"][name]
                value = convert_string_to_result(value, node_arguments.arg_type)
                kwargs[name] = value
                continue
        return self.executable(*args, **kwargs)

