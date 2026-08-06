class Relation:
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __str__(self):
        return "(" + str(self.first) + "R" + str(self.second) + ")"

    def __repr__(self):
        return "(" + repr(self.first) + "R" + repr(self.second) + ")"

    def __eq__(self, other):
        return self.first == other.first and self.second == other.second

    def __hash__(self):
        return hash((self.first, self.second))

    def get_first(self):
        return self.first

    def get_second(self):
        return self.second