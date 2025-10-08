
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi

from ..utils import Utils
from .feature_set import FeatureSet
from .user import User


class FeatureSetReview:
    def __init__(self, stub: CoreServiceApi, online_stub, review):
        self._stub = stub
        self._online_stub = online_stub
        self._review = review

    @property
    def review_id(self):
        return self._review.review_id

    @property
    def project_name(self):
        return self._review.project_name

    @property
    def feature_set_name(self):
        return self._review.feature_set_name

    @property
    def feature_set_major_version(self):
        return self._review.feature_set_major_version

    @property
    def feature_set_id(self):
        return self._review.feature_set_id

    @property
    def created_at(self):
        return Utils.timestamp_to_string(self._review.created_at)

    @property
    def status(self):
        return str(self._review.status)

    def __repr__(self):
        return Utils.pretty_print_proto(self._review)


class FeatureSetReviewRequest(FeatureSetReview):
    @property
    def author(self):
        return User(self._review.owner)

    def approve(self, reason):
        """Approve a review request.

        Args:
        reason: (str) A reason for review request approval.

        Typical example:
        review_request.approve("it will be fun")

        For more details:
        https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-review-requests-from-other-users
        """
        self._stub.core_service_approve_review(review_id=self._review.review_id, reason=reason)

    def reject(self, reason):
        """Reject a review request.

        Args:
        reason: (str) A reason for review request rejection.

        Typical example:
        review_request.reject("it's not ready yet")

        For more details:
        https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-review-requests-from-other-users
        """
        self._stub.core_service_reject_review(review_id=self._review.review_id, reason=reason)


    def get_feature_set(self) -> FeatureSet:
        """Get a feature set to review.

        Returns:
            A corresponding feature set.

        Typical example:
            review_request.get_feature_set()
        """
        response = self._stub.core_service_get_feature_set_to_review(review_id=self._review.review_id)
        return FeatureSet(self._stub, self._online_stub, response.feature_set)

    def get_preview(self):
        """Preview the data of feature set to review.

        This previews up to a maximum of 100 rows and 50 features.

        Returns:
            list[dict]: A list of dictionary which contains JSON rows.

        Typical example:
            review_request.get_preview()
        """
        response = self._stub.core_service_get_feature_set_preview_to_review(review_id=self._review.review_id)
        if response.preview_url:
            json_response = Utils.fetch_preview_as_json_array(response.preview_url)
            return json_response
        else:
            return []


class FeatureSetUserReview(FeatureSetReview):
    @property
    def reviewer(self):
        return User(self._review.reviewer)

    @property
    def reviewed_at(self):
        return Utils.timestamp_to_string(self._review.reviewed_at)

    @property
    def reason(self):
        return self._review.reason

    def get_feature_set(self) -> FeatureSet:
        """Get a feature set in review.

        Returns:
            A corresponding feature set.

        Typical example:
            review_request.get_feature_set()

        For more details:
        https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-own-feature-sets-in-review
        """
        response = self._stub.core_service_get_feature_set_in_review(review_id=self._review.review_id)
        return FeatureSet(self._stub, self._online_stub, response.feature_set)

    def get_preview(self):
        """Preview the data of feature set in review.

        This previews up to a maximum of 100 rows and 50 features.

        Returns:
            list[dict]: A list of dictionary which contains JSON rows.

        Typical example:
            review_request.get_preview()

        For more details:
        https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-own-feature-sets-in-review
        """
        response = self._stub.core_service_get_feature_set_preview_in_review(review_id=self._review.review_id)
        if response.preview_url:
            json_response = Utils.fetch_preview_as_json_array(response.preview_url)
            return json_response
        else:
            return []

    def delete(self):
        """Delete the currently major version in review.

        Review must be in status IN_PROGRESS or REJECTED.

        Typical example:
            review_request.delete()

        For more details:
        https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-own-feature-sets-in-review
        """
        self._stub.core_service_delete_feature_set_version_in_review(review_id=self._review.review_id)
