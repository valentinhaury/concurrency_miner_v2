import uuid

class Event:
    def __init__(self, label):
        self.label = label
        self.id = uuid.uuid4()

    def __repr__(self):
        return f"{self.label}"
        return f"<Event \"{self.label}\" with id {self.id}>"

    def __str__(self):
        return f":{self.label}"

    def get_id(self):
        return self.id

    def get_label(self):
        return self.label
