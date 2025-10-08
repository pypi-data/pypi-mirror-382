
from h2o_featurestore.gen.model.v1_advanced_search_option import V1AdvancedSearchOption

from ..search_field import SearchField
from ..search_operator import SearchOperator


class AdvancedSearchOption:
    def __init__(
        self,
        search_operator: SearchOperator,
        search_field: SearchField,
        search_value: str,
    ):
        self._search_operator = search_operator
        self._search_field = search_field
        self._search_value = search_value

    def _to_proto(self):
        return V1AdvancedSearchOption(
            search_operator=SearchOperator.to_proto(self._search_operator),
            search_field=SearchField.to_proto(self._search_field),
            search_value=self._search_value,
        )
