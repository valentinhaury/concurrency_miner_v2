from src.data_structures.relations.relation import Relation

class MinimumSelfDistanceRelation(Relation):
    def __init__(self, first, second):
        super().__init__(first, second)

    def __str__(self):
        return "(" + str(self.first) + "-o-" + str(self.second) + ")"

    def __repr__(self):
        return "(" + repr(self.first) + "-o-" + repr(self.second) + ")"