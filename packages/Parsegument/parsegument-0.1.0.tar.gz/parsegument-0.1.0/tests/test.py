from typing import Union
import parsegument
from parsegument import Argument

parser = parsegument.Parsegumenter()
command = parsegument.Command(name="something", executable=print)
command.add_node(Argument(name="value", arg_type=str))
parser.add_child(command)
parser.execute("something yes")
