class FeatureSetRef:
    def __init__(self, id: str, major_version: int):
        self.id = id
        self.major_version = major_version

    def __repr__(self):
        return f"FeatureSetRef({self.id}, {self.major_version})"

    def __hash__(self):
        return hash((self.id, self.major_version))

    def __eq__(self, other):
        return self.id == other.id and self.major_version == other.major_version
