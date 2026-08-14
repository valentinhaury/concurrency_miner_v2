from enum import Enum

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def __str__(self):
        if isinstance(self.value, Enum):
            value = self.value.value
        else:
            value = str(self.value)

        if not self.children:
            return value

        children = ", ".join(str(child) for child in self.children)
        return f"{value}({children})"

    def add_child(self, child):
        self.children.append(child)

    def get_value_string(self):
        if isinstance(self.value, Enum):
            value = self.value.value
        else:
            value = str(self.value)
        return value

    def print_tree(self, prefix="", is_last=True):
        if isinstance(self.value, Enum):
            value = self.value.value
        else:
            value = str(self.value)

        print(prefix + ("└── " if is_last else "├── ") + value)

        new_prefix = prefix + ("    " if is_last else "│   ")

        for i, child in enumerate(self.children):
            child.print_tree(
                new_prefix,
                i == len(self.children) - 1
            )