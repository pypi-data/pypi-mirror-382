from abc import ABC
from abc import abstractmethod

from h2o_featurestore.gen.api.core_service_api import CoreServiceApi
from h2o_featurestore.gen.model.core_service_update_recommendation_classifier_request import (
    CoreServiceUpdateRecommendationClassifierRequest,
)
from h2o_featurestore.gen.model.v1_recommendation_classifier import (
    V1RecommendationClassifier,
)
from h2o_featurestore.gen.model.v1_recommendation_regex_matching_policy import (
    V1RecommendationRegexMatchingPolicy,
)
from h2o_featurestore.gen.model.v1_recommendation_sample_matching_policy import (
    V1RecommendationSampleMatchingPolicy,
)


class Classifier(ABC):
    name: str
    
    @abstractmethod
    def _to_proto(self):
        raise NotImplementedError("Method `__to_proto` needs to be implemented by the child class")

    @staticmethod
    def _from_proto(classifier: V1RecommendationClassifier):
        if classifier.regex:
            return RegexClassifier(
                classifier.name,
                classifier.regex.regex,
                classifier.regex.percentage_match,
            )
        elif classifier.sample:
            return SampleClassifier(
                classifier.name,
                classifier.sample.feature_set_id,
                classifier.sample.feature_set_major_version,
                classifier.sample.column_name,
                classifier.sample.sample_fraction,
                classifier.sample.fuzzy_distance,
                classifier.sample.percentage_match,
            )
        elif classifier.name:
            return EmptyClassifier(classifier.name)
        else:
            raise ValueError("Not supported classifier provided")


class EmptyClassifier(Classifier):
    def __init__(self, name):
        self.name = name

    def _to_proto(self):
        return V1RecommendationClassifier(name=self.name)

    def __repr__(self):
        return f"EmptyClassifier(name={self.name})"


class RegexClassifier(Classifier):
    def __init__(self, name, regex, percentage_match):
        self.name = name
        self.regex = regex
        self.percentage_match = percentage_match

    def _to_proto(self):
        return V1RecommendationClassifier(
            name=self.name,
            regex=V1RecommendationRegexMatchingPolicy(regex=self.regex, percentage_match=self.percentage_match),
        )

    def __repr__(self):
        return f"RegexClassifier(name={self.name}, regex={self.regex}, percentage_match={self.percentage_match})"


class SampleClassifier(Classifier):
    def __init__(
        self,
        name: str,
        feature_set_id: str,
        feature_set_major_version: int,
        column_name: str,
        sample_fraction: float,
        fuzzy_distance: int,
        percentage_match: int,
    ):
        self.name = name
        self.feature_set_id = feature_set_id
        self.feature_set_major_version = feature_set_major_version
        self.column_name = column_name
        self.sample_fraction = sample_fraction
        self.fuzzy_distance = fuzzy_distance
        self.percentage_match = percentage_match

    @classmethod
    def from_feature_set(
        cls,
        feature_set,
        name,
        column_name,
        sample_fraction,
        fuzzy_distance,
        percentage_match,
    ):
        return cls(
            name,
            feature_set.id,
            feature_set.major_version,
            column_name,
            sample_fraction,
            fuzzy_distance,
            percentage_match,
        )

    def _to_proto(self):
        return V1RecommendationClassifier(
            name=self.name,
            sample=V1RecommendationSampleMatchingPolicy(
                feature_set_id=self.feature_set_id,
                feature_set_major_version=self.feature_set_major_version,
                column_name=self.column_name,
                sample_fraction=self.sample_fraction,
                fuzzy_distance=self.fuzzy_distance,
                percentage_match=self.percentage_match,
            ),
        )

    def __repr__(self):
        return (
            f"SampleClassifier(name={self.name}, "
            f"feature_set_id={self.feature_set_id}, "
            f"feature_set_major_version={self.feature_set_major_version}, "
            f"column_name={self.column_name}, "
            f"sample_fraction={self.sample_fraction}, "
            f"fuzzy_distance={self.fuzzy_distance}, "
            f"percentage_match={self.percentage_match})"
        )


class Classifiers:
    def __init__(self, stub: CoreServiceApi):
        self._stub = stub

    def list(self) -> list[Classifier]:
        """Return all configured classifiers on the backend.

        Returns:
            list[Classifier]: A list of Classifier - EmptyClassifier | RegexClassifier | SampleClassifier.

            For example:

            [RegexClassifier(name=FS_TEST_CLASSIFIER, regex=auto_apply_classifier, percentage_match=100)]

        Typical example:
            client.classifiers.list()

        """
        response = self._stub.core_service_list_recommendation_classifiers()
        return [Classifier._from_proto(classifier) for classifier in response.classifiers]

    def create(self, classifier) -> None:
        """Register a new classifier.

        Feature Store administrators can register new classifiers in the system.

        Args:
            classifier: (str | Classifier) Object represents String or Classifier.

        Typical example:
            client.classifiers.create("classifierName")
            client.classifiers.create(RegexClassifier("classifierName", "test", 10))

        Raises:
            ValueError: Parameter classifier should be string or object of Classifier class.

        For more details:
            https://docs.h2o.ai/featurestore/api/recommendation_api.html#creating-a-new-classifier
        """
        if isinstance(classifier, str):
            classifier_to_send = EmptyClassifier(classifier)._to_proto()
        elif isinstance(classifier, Classifier):
            classifier_to_send = classifier._to_proto()
        else:
            raise ValueError("Parameter classifier should be string or object of Classifier class")

        self._stub.core_service_create_recommendation_classifier(classifier=classifier_to_send)

    def update(self, classifier: Classifier):
        """Update an existing classifier.

        Feature Store administrators can update the classifiers.

        Args:
            classifier: (Classifier) Object represents Classifier.
              EmptyClassifier | RegexClassifier | SampleClassifier

        Typical example:
            client.classifiers.update(RegexClassifier("classifierName", "test", 10))

        For more details:
            https://docs.h2o.ai/featurestore/api/recommendation_api.html#updating-an-existing-classifier
        """
        request = CoreServiceUpdateRecommendationClassifierRequest()
        proto = classifier._to_proto()
        if proto.regex:
            request.regex = proto.regex
        if proto.sample:
            request.sample = proto.sample
        self._stub.core_service_update_recommendation_classifier(classifier_name=classifier.name, classifier=request)

    def delete(self, name: str):
        """Delete an existing classifier.

        Feature Store administrators can delete the classifiers.

        Args:
            name: (str) A name of an existing classifier.

        Typical example:
            client.classifiers.delete("classifierName")

        For more details:
            https://docs.h2o.ai/featurestore/api/recommendation_api.html#deleting-an-existing-classifier
        """
        self._stub.core_service_delete_recommendation_classifier(classifier_name=name)

    def __repr__(self):
        return "Recommendation classifiers"
