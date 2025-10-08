from typing import Iterator

from h2o_featurestore.core.entities.feature_set_review import FeatureSetReviewRequest
from h2o_featurestore.core.entities.feature_set_review import FeatureSetUserReview
from h2o_featurestore.gen.api.core_service_api import CoreServiceApi


class FeatureSetReviews:
    def __init__(self, stub: CoreServiceApi, online_stub, project_id=None):
        self._stub = stub
        self._online_stub = online_stub
        self._project_id = project_id

    def manageable_requests(self, filters=None) -> Iterator[FeatureSetReviewRequest]:
        """List pending manageable feature set review requests.

        Args:
            (ReviewStatuses) Object represents a specific review status.
            filters: (list[ReviewStatuses]) Filter includes the status of review
            (either IN_PROGRESS, APPROVED or REJECTED).

        Returns:
            Generator of feature set review requests

        Typical example:
            filters = [ReviewStatuses.IN_PROGRESS]
            reviews = client.feature_set_reviews.manageable_requests()

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-review-requests-from-other-users
        """
        has_next_page = True
        next_page_token = ""
        while has_next_page:
            response = self._stub.core_service_list_feature_sets_to_review(filters=filters, project_id=self._project_id, page_token=next_page_token)
            if response.next_page_token:
                next_page_token = response.next_page_token
            else:
                has_next_page = False
            for entry in response.entries:
                yield FeatureSetReviewRequest(self._stub, self._online_stub, entry)

    def my_requests(self, filters=None) -> Iterator[FeatureSetUserReview]:
        """List existing feature set review requests belonging to the user.

        Args:
            (ReviewStatuses) Object represents a specific review status.
            filters: (list[ReviewStatuses]) Filter includes the status of review
            (either IN_PROGRESS, APPROVED or REJECTED).

        Returns:
            Generator of feature set user review requests

        Typical example:
            filters = [ReviewStatuses.IN_PROGRESS]
            reviews = client.feature_set_reviews.my_requests(filters)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-own-feature-sets-in-review
        """
        has_next_page = True
        next_page_token = ""
        while has_next_page:
            response = self._stub.core_service_list_feature_sets_reviews_page(filters=filters, project_id=self._project_id, page_token=next_page_token)
            if response.next_page_token:
                next_page_token = response.next_page_token
            else:
                has_next_page = False
            for entry in response.entries:
                yield FeatureSetUserReview(self._stub, self._online_stub, entry)


    def __paged_response_to_request(self, request, call):
        while request:
            response = call(request)
            if response.next_page_token:
                request.page_token = response.next_page_token
            else:
                request = None
            for entry in response.entries:
                yield entry
