from data_structures.relations.relation import Relation

class DirectlyFollowsRelation(Relation):
    def __init__(self, first, second):
        super().__init__(first, second)

    def __str__(self):
        return "(" + str(self.first) + "->>" + str(self.second) + ")"