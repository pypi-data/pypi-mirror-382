from ...subpackage import *

__all__ = [
    "SimpleClass",
    "simple_function",
    "public_chain",
    "module_level_function",
    "does_not_exist",
]


class SimpleClass:
    def simple_method(self):
        return 5


class NotAllClass:
    def not_all_method(self):
        return 5


def simple_function():
    return 5


def not_all_function():
    return 5
