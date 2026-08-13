class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def __str__(self):
        string = ""
        if self.children:
            string += self.value.value + "("
            for child in self.children:
                string += str(child) + ", "
            string = string[:-2] + ")"
        else:
            string += str(self.value)
        return string

    def add_child(self, child):
        self.children.append(child)
