from enum import Enum

from h2o_featurestore.gen.model.advanced_search_option_search_operator import (
    AdvancedSearchOptionSearchOperator,
)


class SearchOperator(Enum):
    SEARCH_OPERATOR_LIKE = 1
    SEARCH_OPERATOR_EQ = 2

    @classmethod
    def to_proto(cls, search_operator):
        return {
            cls.SEARCH_OPERATOR_LIKE: AdvancedSearchOptionSearchOperator("LIKE"),
            cls.SEARCH_OPERATOR_EQ: AdvancedSearchOptionSearchOperator("EQ"),
        }[search_operator]
