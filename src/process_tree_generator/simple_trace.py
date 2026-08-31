from itertools import permutations


class SimpleTrace:
    def __init__(self, events, strict_partial_order):
        self.events = set(events)
        self.strict_partial_order = set(strict_partial_order)

    def __repr__(self):
        output = "___ST: "
        output += str(self.events)
        output += ", "
        output += str(self.strict_partial_order)
        output += "___"
        return output

    def __str__(self):
        output = "___ST: "
        output += str(self.events)
        output += ", "
        output += str(self.strict_partial_order)
        output += "___"
        return output

    def add_event(self, event):
        self.events.add(event)

    def add_strict_partial_order(self, strict_partial_order):
        self.strict_partial_order.add(strict_partial_order)

    def compute_closure(self):
        changed = True
        while changed:
            changed = False
            for e1, e2, e3 in permutations(self.events, 3):
                relation = (e1, e3)
                if ((e1, e2) in self.strict_partial_order and
                        (e2, e3) in self.strict_partial_order and
                        relation not in self.strict_partial_order):
                    self.add_strict_partial_order(relation)
                    changed = True