from h2o_featurestore.gen.model.v1_review_status import V1ReviewStatus

IN_PROGRESS = V1ReviewStatus("REVIEW_STATUS_TO_REVIEW")
APPROVED = V1ReviewStatus("REVIEW_STATUS_APPROVED")
REJECTED = V1ReviewStatus("REVIEW_STATUS_REJECTED")
