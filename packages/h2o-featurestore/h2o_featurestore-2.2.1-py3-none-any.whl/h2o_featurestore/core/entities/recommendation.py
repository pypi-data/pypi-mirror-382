class Recommendation:
    def __init__(self, stub, online_stub, source_feature_set, match_result):
        from .feature_set import FeatureSet  # To avoid circular import reference

        self._source = source_feature_set
        self._target = FeatureSet(stub, online_stub, match_result.target_feature_set)
        self._joins = {join.classifier: join.columns for join in match_result.joins}

    def __repr__(self):
        return str(
            {
                "source": {
                    "project_name": self._source.project,
                    "feature_set_name": self._source.feature_set_name,
                },
                "target": {
                    "project_name": self._target.project,
                    "feature_set_name": self._target.feature_set_name,
                },
                "joins": self._joins,
            }
        )

    def __str__(self):
        return (
            f"Source                  \n"
            f"  Project name        : {self._source.project}\n"
            f"  Feature set name    : {self._source.feature_set_name}\n"
            f"Target                  \n"
            f"  Project name        : {self._target.project}\n"
            f"  Feature set name    : {self._target.feature_set_name}\n"
            f"Joins                 : {self._joins}\n"
        )
