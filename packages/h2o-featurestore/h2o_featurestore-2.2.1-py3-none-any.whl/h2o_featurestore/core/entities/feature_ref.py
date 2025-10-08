from __future__ import annotations

from .feature_set_ref import FeatureSetRef


class FeatureRef:
    def __init__(self, name, feature_set_ref: FeatureSetRef):
        self.name = name
        self.feature_set_ref = feature_set_ref

    def __repr__(self):
        return f"FeatureRef({self.name}, {self.feature_set_ref})"

    def __hash__(self):
        return hash((self.name, self.feature_set_ref))

    def __eq__(self, other):
        return self.name == other.name and self.feature_set_ref == other.feature_set_ref
