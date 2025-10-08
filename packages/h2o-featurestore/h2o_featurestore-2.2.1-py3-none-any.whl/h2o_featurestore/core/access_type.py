from enum import Enum

from h2o_featurestore.gen.model.v1_active_permission import V1ActivePermission
from h2o_featurestore.gen.model.v1_permission_type import V1PermissionType


class AccessType(Enum):
    OWNER = 1
    EDITOR = 2
    CONSUMER = 3
    SENSITIVE_CONSUMER = 4
    VIEWER = 5

    @classmethod
    def from_proto_permission(cls, proto_permission_type):
        return {
            "Owner": cls.OWNER,
            "Editor": cls.EDITOR,
            "Consumer": cls.CONSUMER,
            "SensitiveConsumer": cls.SENSITIVE_CONSUMER,
            "Viewer": cls.VIEWER,
        }[str(proto_permission_type)]

    @classmethod
    def to_proto_permission(cls, access_type):
        return {
            cls.OWNER: V1PermissionType("Owner"),
            cls.EDITOR: V1PermissionType("Editor"),
            cls.CONSUMER: V1PermissionType("Consumer"),
            cls.SENSITIVE_CONSUMER: V1PermissionType("SensitiveConsumer"),
            cls.VIEWER: V1PermissionType("Viewer"),
        }[access_type]

    @classmethod
    def from_proto_active_permission(cls, active_permission):
        return {
            "ACTIVE_PERMISSION_NONE": None,
            "ACTIVE_PERMISSION_OWNER": cls.OWNER,
            "ACTIVE_PERMISSION_EDITOR": cls.EDITOR,
            "ACTIVE_PERMISSION_CONSUMER": cls.CONSUMER,
            "ACTIVE_PERMISSION_SENSITIVE_CONSUMER": cls.SENSITIVE_CONSUMER,
            "ACTIVE_PERMISSION_VIEWER": cls.VIEWER,
        }[str(active_permission)]

    @classmethod
    def to_proto_active_permission(cls, active_permission):
        return {
            None: V1ActivePermission("ACTIVE_PERMISSION_NONE"),
            cls.OWNER: V1ActivePermission("ACTIVE_PERMISSION_OWNER"),
            cls.EDITOR: V1ActivePermission("ACTIVE_PERMISSION_EDITOR"),
            cls.CONSUMER: V1ActivePermission("ACTIVE_PERMISSION_CONSUMER"),
            cls.SENSITIVE_CONSUMER: V1ActivePermission("ACTIVE_PERMISSION_SENSITIVE_CONSUMER"),
            cls.VIEWER: V1ActivePermission("ACTIVE_PERMISSION_VIEWER"),
        }[active_permission]
