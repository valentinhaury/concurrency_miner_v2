class Activity:
    def __init__(self, activity_label):
        self.label = activity_label

    def __eq__(self, other):
        return self.label == other.label

    def __hash__(self):
        return hash(self.label)

    def __repr__(self):
        return f"<Activity \"{self.label}\">"

    def __str__(self):
        return self.label

    def get_label(self):
        return self.label
