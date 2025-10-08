from abc import ABC
from abc import abstractmethod

from h2o_featurestore.core.utils import Utils
from h2o_featurestore.gen.model.v1_optimize_storage_z_order_by_spec import (
    V1OptimizeStorageZOrderBySpec,
)
from h2o_featurestore.gen.model.v1_storage_optimization import V1StorageOptimization


class StorageOptimization(ABC):
    @abstractmethod
    def _initialize(self):
        raise NotImplementedError("Method `_initialize` needs to be implemented by the child class")

    @abstractmethod
    def _to_proto(self):
        raise NotImplementedError("Method `to_proto` needs to be implemented by the child class")

    @staticmethod
    def from_proto(proto: V1StorageOptimization):
        if proto.get("compact"):
            return CompactOptimization()
        elif proto.get("z_order_by"):
            columns = proto.z_order_by.columns
            return ZOrderByOptimization(columns)
        else:
            return None

    def __repr__(self):
        return Utils.pretty_print_proto(self._to_proto())


class ZOrderByOptimization(StorageOptimization):
    def __init__(self, columns):
        self.columns = columns

    def _initialize(self):
        pass

    def _to_proto(self):
        spec = V1OptimizeStorageZOrderBySpec(columns=self.columns)
        proto = V1StorageOptimization(
            z_order_by=spec
        )
        return proto


class CompactOptimization(StorageOptimization):
    def __init__(self):
        pass

    def _initialize(self):
        pass

    def _to_proto(self):
        proto = V1StorageOptimization(
            compact=True,
        )
        return proto
