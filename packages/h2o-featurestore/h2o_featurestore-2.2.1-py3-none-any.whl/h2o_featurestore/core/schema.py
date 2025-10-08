import copy
import re
from typing import List
from typing import Optional

from h2o_featurestore.core.entities.feature import FeatureType
from h2o_featurestore.gen.model.v1_derived_information import V1DerivedInformation
from h2o_featurestore.gen.model.v1_feature_schema import V1FeatureSchema
from h2o_featurestore.gen.model.v1_feature_schema_monitoring import (
    V1FeatureSchemaMonitoring,
)
from h2o_featurestore.gen.model.v1_feature_schema_special_data import (
    V1FeatureSchemaSpecialData,
)
from h2o_featurestore.gen.model.v1_feature_type import V1FeatureType
from h2o_featurestore.gen.model.v1_versioned_id import V1VersionedId

from .transformations import Transformation


class FeatureSchemaSpecialData:
    def __init__(self, spi=False, pci=False, rpi=False, demographic=False, sensitive=False):
        self.spi = spi
        self.pci = pci
        self.rpi = rpi
        self.demographic = demographic
        self.sensitive = sensitive

    def __repr__(self):
        return (
            f"spi={self.spi}, pci={self.pci}, rpi={self.rpi}, demographic={self.demographic}, "
            f"sensitive={self.sensitive}"
        )


class FeatureSchemaMonitoring:
    def __init__(self, anomaly_detection=False):
        self.anomaly_detection = anomaly_detection

    def __repr__(self):
        return f"anomaly_detection={self.anomaly_detection}"


class FeatureSchema:
    def __init__(
        self,
        name,
        _data_type,
        special_data=None,
        nested_features_schema=None,
        _feature_type="AUTOMATIC_DISCOVERY",
        description="",
        classifiers: Optional[set] = None,
        custom_data=None,
        monitoring=None,
    ):
        self._data_type = _data_type
        self._name = name
        self._special_data = special_data or FeatureSchemaSpecialData()
        self._nested_features_schema = nested_features_schema or []
        self._schema = Schema(self._nested_features_schema, False)
        self._validated_feature_type = FeatureSchema.get_and_validate_feature_type(_feature_type)
        self._description = description
        self._classifiers = classifiers or set()
        self._custom_data = custom_data
        self._monitoring = monitoring or FeatureSchemaMonitoring()

    @property
    def schema(self):
        return self._schema

    @property
    def special_data(self):
        return self._special_data

    @special_data.setter
    def special_data(self, value):
        self._special_data = value

    @property
    def name(self):
        return self._name

    @property
    def data_type(self):
        if self._schema.size() > 0:
            nested_data_type = ", ".join(
                [f"{nested.name}: {nested.data_type}" for nested in self._nested_features_schema]
            )
            return self._data_type.format(nested_data_type)
        else:
            return self._data_type

    @data_type.setter
    def data_type(self, value):
        self._data_type = value

    @property
    def feature_type(self) -> FeatureType:
        return self._validated_feature_type

    @feature_type.setter
    def feature_type(self, value: FeatureType):
        self._validated_feature_type = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def classifiers(self):
        return self._classifiers

    @classifiers.setter
    def classifiers(self, value: set):
        self._classifiers = value

    @property
    def custom_data(self):
        return self._custom_data

    @custom_data.setter
    def custom_data(self, value):
        self._custom_data = value

    @property
    def monitoring(self):
        return self._monitoring

    @monitoring.setter
    def monitoring(self, value):
        self._monitoring = value

    def to_string(self):
        return self._to_string("")

    def _to_string(self, prefix):
        initial = "- " if prefix == "" else prefix
        res = f"{initial}{self.name}: {self.data_type}"
        if self._schema.size() > 0:
            nested_prefix = "  |-- " if prefix == "" else "  " + prefix
            res += "\n" + self._schema._to_string(nested_prefix)
        return res

    @staticmethod
    def create_from(feature):
        nested = [FeatureSchema.create_from(nested_feature) for _, nested_feature in feature.nested_features.items()]
        return FeatureSchema(
            feature.name,
            feature.data_type,
            FeatureSchemaSpecialData(
                feature.special_data.spi,
                feature.special_data.pci,
                feature.special_data.rpi,
                feature.special_data.demographic,
                feature.special_data.sensitive,
            ),
            nested,
            feature.profile.feature_type.value,
            feature.description,
            feature.classifiers,
            feature.custom_data,
            FeatureSchemaMonitoring(feature.monitoring.anomaly_detection),
        )

    @staticmethod
    def get_and_validate_feature_type(feature_type):
        return V1FeatureType(feature_type)

    def __repr__(self):
        return self.to_string()


class VersionedId:
    def __init__(self, id: str, major_version: int):
        self.id = id
        self.major_version = major_version


class SchemaDerivation:
    def __init__(
        self,
        feature_set_ids: List[VersionedId],
        transformation: Transformation,
    ):
        self.feature_set_ids = feature_set_ids
        self.transformation = transformation

    def _to_proto(self):
        return V1DerivedInformation(
            feature_set_ids=[V1VersionedId(id=f.id, major_version=f.major_version) for f in self.feature_set_ids],
            transformation=self.transformation._to_proto(),
        )


class Schema:
    def __init__(self, feature_schemas, is_root_schema, derivation: Optional[SchemaDerivation] = None):
        self._feature_schemas = feature_schemas
        self._is_root_schema = is_root_schema
        if is_root_schema:
            self._field_separator = " "
        else:
            self._field_separator = ": "
        self.derivation = derivation

    def __getitem__(self, feature_name):
        filtered = list(filter(lambda f: f.name == feature_name, self._feature_schemas))
        if len(filtered):
            return filtered[0]
        else:
            raise Exception(f"Feature name '{feature_name}' does not exist in the schema.")

    @staticmethod
    def create_from(obj):
        """Create a schema from String and FeatureSet.

        Args:
            obj: (str | FeatureSet) Object represents String or FeatureSet.

        Returns:
            Schema: A schema with feature names and data types.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical example:
            schema = Schema.create_from("col1 string, col2 string, col3 integer")

        Raises:
            Exception: Schema can be created either from string or existing feature set.

        For more details:
            https://docs.h2o.ai/featurestore/api/schema_api.html#create-a-schema-from-a-string
        """
        from .entities.feature_set import FeatureSet

        if isinstance(obj, FeatureSet):
            features = [FeatureSchema.create_from(feature) for name, feature in obj.features.items()]
            if obj.is_derived():
                derived_from = obj._feature_set.derived_from
                derivation = SchemaDerivation(
                    [VersionedId(f.id, f.major_version) for f in derived_from.feature_set_ids],
                    Transformation.from_proto(derived_from.transformation),
                )
                return Schema(features, True, derivation)
            else:
                return Schema(features, True)
        elif isinstance(obj, str):
            return Schema(Schema._parse_features_schema(obj, True)[::-1], True)
        else:
            raise Exception("Schema can be created either from string or existing feature set.")

    @staticmethod
    def create_derived_from(schema_string: str, derive_from, transformation: Transformation):
        """Create a schema from a string formatted schema and parent feature set along with transformation.

        Args:
            schema_string: (str) String contains column names and data types.
            derive_from: (FeatureSet) Represents a feature set.
            transformation: (Transformation) Represents an instance of Transformation.

        Returns:
            Schema: A schema with feature names and data types.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP
        """
        return Schema(
            Schema._parse_features_schema(schema_string, True)[::-1],
            True,
            SchemaDerivation(
                [VersionedId(f.id, f.major_version) for f in derive_from],
                transformation,
            ),
        )

    def select(self, feature_names):
        """Create a new schema by column selection.

        Args:
            feature_names: (Iterable[str]) String or iterable collection of strings.

        Returns:
            Schema: A schema with selected feature names and data types.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical example:
            schema_str = "id INT, text STRING, label DOUBLE, state STRING, date STRING"
            schema = Schema.create_from(schema_str)
            new_schema = schema.select("id text label")

        For more details:
            https://docs.h2o.ai/featurestore/api/schema_api.html#create-a-new-schema-by-column-selection
        """
        return Schema(
            feature_schemas=copy.deepcopy(
                list(filter(lambda schema: schema.name in feature_names, self._feature_schemas))
            ),
            is_root_schema=self._is_root_schema,
            derivation=copy.deepcopy(self.derivation),
        )

    def exclude(self, feature_names):
        """Create a new schema by column selection.

        Args:
            feature_names: (Iterable[str]) String or iterable collection of strings.

        Returns:
            Schema: A schema with feature names and data types without excluded names.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical example:
            schema_str = "id INT, text STRING, label DOUBLE, state STRING, date STRING"
            schema = Schema.create_from(schema_str)
            new_schema = schema.exclude("id text label")

        For more details:
            https://docs.h2o.ai/featurestore/api/schema_api.html#create-a-new-schema-by-column-selection
        """
        return Schema(
            feature_schemas=copy.deepcopy(
                list(filter(lambda schema: schema.name not in feature_names, self._feature_schemas))
            ),
            is_root_schema=self._is_root_schema,
            derivation=copy.deepcopy(self.derivation),
        )

    def append(self, feature_schema, after=None):
        """Create a new schema.

        A schema is created by adding a new feature schema to the end / after the selected column.

        Args:
            feature_schema: (FeatureSchema) Represents new feature schema.
            after: (FeatureSchema) Represents an existing feature schema.

        Returns:
            Schema: A schema with existing feature names and data types and newly added feature column.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical example:
            new_feature_schema = FeatureSchema("new_name", STRING)
            schema.append(new_feature_schema)  # Append to the end
            new_schema = schema.append(new_feature_schema, schema["old"])  # Append after old

        Raises:
            Exception: Feature name does not exist in the schema.

        For more details:
            https://docs.h2o.ai/featurestore/api/schema_api.html#create-a-new-schema-by-adding-a-new-feature-schema
        """
        new_feature_schemas = copy.deepcopy(self._feature_schemas)
        if not after:
            new_feature_schemas.append(feature_schema)
        else:
            index = self._feature_schemas.index(after) + 1
            new_feature_schemas.insert(index, feature_schema)
        return Schema(
            feature_schemas=new_feature_schemas,
            is_root_schema=self._is_root_schema,
            derivation=copy.deepcopy(self.derivation),
        )

    def prepend(self, feature_schema, before=None):
        """Create a new schema.

        A schema is created by adding a new feature schema to the beginning / before the selected column.

        Args:
            feature_schema: (FeatureSchema) Represents new feature schema.
            before: (FeatureSchema) Represents an existing feature schema.

        Returns:
            Schema: A schema with existing feature names and data types and newly added feature column.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical example:
            new_feature_schema = FeatureSchema("new_name", STRING)
            schema.prepend(new_feature_schema)  # Prepend to the beginning
            new_schema = schema.prepend(new_feature_schema, schema["old"])  # Prepend before old

        Raises:
            Exception: Feature name does not exist in the schema.

        For more details:
            https://docs.h2o.ai/featurestore/api/schema_api.html#create-a-new-schema-by-adding-a-new-feature-schema
        """
        new_feature_schemas = copy.deepcopy(self._feature_schemas)

        if not before:
            new_feature_schemas.insert(0, feature_schema)
        else:
            index = self._feature_schemas.index(before)
            new_feature_schemas.insert(index, feature_schema)

        return Schema(
            feature_schemas=new_feature_schemas,
            is_root_schema=self._is_root_schema,
            derivation=copy.deepcopy(self.derivation),
        )

    def size(self):
        """Return the length of a schema."""
        return len(self._feature_schemas)

    def is_derived(self):
        return self.derivation is not None

    def to_string(self):
        return self._to_string("")

    def _to_string(self, prefix):
        return "\n".join([f"{nested._to_string(prefix)}" for nested in self._feature_schemas])

    def to_sql_string(self):
        return ", ".join(
            [f"{feature_schema.name} {feature_schema.data_type}" for feature_schema in self._feature_schemas]
        )

    def _to_proto_schema(self):
        return [
            V1FeatureSchema(
                name=feature_schema.name,
                data_type=feature_schema.data_type,
                nested=feature_schema.schema._to_proto_schema(),
                special_data=V1FeatureSchemaSpecialData(
                    spi=feature_schema.special_data.spi,
                    pci=feature_schema.special_data.pci,
                    rpi=feature_schema.special_data.rpi,
                    demographic=feature_schema.special_data.demographic,
                    sensitive=feature_schema.special_data.sensitive,
                ),
                feature_type=FeatureType.to_proto(feature_schema._validated_feature_type),
                description=feature_schema.description,
                classifiers=list(feature_schema.classifiers),
                custom_data=feature_schema.custom_data,
                monitoring=V1FeatureSchemaMonitoring(anomaly_detection=feature_schema.monitoring.anomaly_detection),
            )
            for feature_schema in self._feature_schemas
        ]

    def __repr__(self):
        return self.to_string()

    @staticmethod
    def _parse_features_schema(schema_string, is_root_level):
        if schema_string:
            feature_schema, remaining_schema_string = Schema._extract_pair(schema_string, is_root_level)
            return Schema._parse_features_schema(remaining_schema_string, is_root_level) + [feature_schema]
        else:
            return []

    @staticmethod
    def _get_index_of_matching_ending_angular_bracket(string):
        stack = []
        for idx, ch in enumerate(string):
            if ch == "<":
                stack.append(idx)
            elif ch == ">":
                if len(stack) == 0:
                    raise Exception("Invalid schema!")
                if len(stack) == 1:
                    return idx
                else:
                    stack.pop()
        if len(stack) != 0:
            raise Exception("Invalid schema!")

    @staticmethod
    def _extract_pair(schema, is_root_level):
        if is_root_level:
            splits = schema.split(maxsplit=1)
            remaining_with_data_type = splits[1]
        else:
            splits = re.split(r"\s*:\s*", schema, maxsplit=1)
            remaining_with_data_type = splits[1]
        col_name = splits[0]
        if Schema._is_complex(remaining_with_data_type):
            idx = Schema._get_index_of_matching_ending_angular_bracket(remaining_with_data_type) + 1
            if idx is None:
                raise Exception("Invalid schema.")
            nested_data_type, remaining_schema = (
                remaining_with_data_type[:idx],
                remaining_with_data_type[idx:],
            )
            if remaining_with_data_type.upper().startswith("STRUCT"):
                nested_schema, data_type = Schema._extract_struct(nested_data_type)
            else:
                nested_schema, data_type = Schema._extract_array(nested_data_type)
            rest = remaining_schema
        else:
            data_type, rest = Schema._extract_primitive(remaining_with_data_type)
            nested_schema = []
        parsed_feature_schema = FeatureSchema(col_name, data_type, nested_features_schema=nested_schema)
        remaining_unparsed = re.sub(r"^\s*,?\s*", "", rest)
        return parsed_feature_schema, remaining_unparsed

    @staticmethod
    def _is_complex(data_type):
        first_non_array_type = Schema._extract_first_non_array_data_type(data_type)
        return first_non_array_type.upper().startswith("STRUCT")

    @staticmethod
    def _extract_first_non_array_data_type(data_type):
        if data_type.upper().startswith("ARRAY"):
            nested_data_type = data_type.strip()[len("ARRAY") : len(data_type)].strip()[1:-1]
            return Schema._extract_first_non_array_data_type(nested_data_type)
        else:
            return data_type

    @staticmethod
    def _extract_struct(data_type):
        data_type_content = data_type.strip()[len("STRUCT") : len(data_type)].strip()[1:-1]
        return (
            Schema._parse_features_schema(data_type_content, is_root_level=False)[::-1],
            "STRUCT<{0}>",
        )

    @staticmethod
    def _extract_array(data_type):
        data_type_content = data_type.strip()[len("ARRAY") : len(data_type)].strip()[1:-1]
        if data_type_content.upper().startswith("ARRAY"):
            nested_schema, placeholder = Schema._extract_array(data_type_content)
            return nested_schema, f"ARRAY<{placeholder}>"
        elif data_type_content.upper().startswith("STRUCT"):
            nested_schema, placeholder = Schema._extract_struct(data_type_content)
            return nested_schema, f"ARRAY<{placeholder}>"
        else:
            return [], ""

    @staticmethod
    def _extract_primitive(schema):
        splits = re.split(r"\s*,\s*", schema, maxsplit=1)
        data_type = splits[0].strip()
        # Call bellow is done for validation purposes
        Schema._get_index_of_matching_ending_angular_bracket(data_type)
        if len(splits) > 1:
            remaining_schema = splits[1].strip()
        else:
            remaining_schema = ""
        return data_type, remaining_schema
