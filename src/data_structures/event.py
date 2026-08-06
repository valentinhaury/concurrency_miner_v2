import uuid

class Event:
    def __init__(self, activity):
        self.activity = activity
        self.id = uuid.uuid4()

    def __repr__(self):
        return f"<Event \"{self.activity.get_label()}\" with id {self.id}>"

    def __str__(self):
        return ":" + self.activity.get_label() + ":"

    def get_id(self):
        return self.id

    def get_activity(self):
        return self.activity
