from src.data_structures.relations.relation import Relation

class EventuallyFollowsRelation(Relation):
    def __init__(self, first, second):
        super().__init__(first, second)

    def __str__(self):
        return "(" + str(self.first) + "->>+" + str(self.second) + ")"

    def __repr__(self):
        return "(" + repr(self.first) + "->>+" + repr(self.second) + ")"