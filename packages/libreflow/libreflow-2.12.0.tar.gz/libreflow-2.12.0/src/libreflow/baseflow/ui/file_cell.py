class FileCell:

    def __init__(self, origin, substitution):
        self.origin = origin
        self.substitution = substitution

    def __repr__(self):
        return "<{0}({1})>".format(self.origin, self.substitution)