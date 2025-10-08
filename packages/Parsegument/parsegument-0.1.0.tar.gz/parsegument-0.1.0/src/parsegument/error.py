class ParseGumentError(Exception):
    def __init__(self, message="Unimplemented") -> None:
        self.message = message

class NodeDoesNotExist(ParseGumentError):
    def __init__(self) -> None:
        super().__init__("Argument does not exist")

class ArgumentGroupNotFound(ParseGumentError):
    def __init__(self) -> None:
        super().__init__("Argument group does not exist")

class MultipleChildrenFound(ParseGumentError):
    def __init__(self) -> None:
        super().__init__("Multiple children found")
