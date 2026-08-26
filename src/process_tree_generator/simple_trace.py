
class SimpleTrace:
    def __init__(self, events, transitive_reduced_strict_partial_order):
        self.events = set(events)
        self.transitive_reduced_strict_partial_order = set(transitive_reduced_strict_partial_order)

