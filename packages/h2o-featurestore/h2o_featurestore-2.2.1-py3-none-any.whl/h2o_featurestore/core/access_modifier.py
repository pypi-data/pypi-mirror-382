from enum import Enum

from h2o_featurestore.gen.model.v1_access_modifier import V1AccessModifier


class AccessModifier(Enum):
    PUBLIC = 1
    PROJECT_ONLY = 2
    PRIVATE = 3

    @classmethod
    def from_proto(cls, proto_access_modifier):
        return {
            "ACCESS_MODIFIER_PUBLIC": cls.PUBLIC,
            "ACCESS_MODIFIER_PROJECT_ONLY": cls.PROJECT_ONLY,
            "ACCESS_MODIFIER_PRIVATE": cls.PRIVATE,
        }[str(proto_access_modifier)]

    @classmethod
    def to_proto(cls, access_modifier):
        return {
            cls.PUBLIC: V1AccessModifier("ACCESS_MODIFIER_PUBLIC"),
            cls.PROJECT_ONLY: V1AccessModifier("ACCESS_MODIFIER_PROJECT_ONLY"),
            cls.PRIVATE: V1AccessModifier("ACCESS_MODIFIER_PRIVATE"),
            None: V1AccessModifier("ACCESS_MODIFIER_UNSPECIFIED"),
        }[access_modifier]
