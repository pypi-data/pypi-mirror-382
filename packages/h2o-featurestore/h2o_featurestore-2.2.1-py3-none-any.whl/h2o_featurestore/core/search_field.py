from enum import Enum

from h2o_featurestore.gen.model.advanced_search_option_search_field import (
    AdvancedSearchOptionSearchField,
)


class SearchField(Enum):
    SEARCH_FIELD_FEATURE_NAME = 1
    SEARCH_FIELD_FEATURE_DESCRIPTION = 2
    SEARCH_FIELD_FEATURE_TAG = 3

    @classmethod
    def to_proto(cls, search_field):
        return {
            cls.SEARCH_FIELD_FEATURE_NAME.name: AdvancedSearchOptionSearchField("FEATURE_NAME"),
            cls.SEARCH_FIELD_FEATURE_DESCRIPTION.name: AdvancedSearchOptionSearchField("FEATURE_DESCRIPTION"),
            cls.SEARCH_FIELD_FEATURE_TAG.name: AdvancedSearchOptionSearchField("FEATURE_TAG"),
        }[search_field]
