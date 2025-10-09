
class Tag:
    def __init__(self, name, description=None, **kwargs):
        self.name = name
        self.description = description
        self.options = kwargs

    def to_dict(self):
        return dict(
            name=self.name, description=self.description, **self.options)
