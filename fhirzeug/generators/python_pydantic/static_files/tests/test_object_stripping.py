import pytest

from pydantic import ValidationError
from pydantic_fhir.r4 import from_dict, ClinicalImpression


@pytest.mark.parametrize(
    "subject_reference", [{"reference": ""}, {"reference": " "}, {"reference": None}]
)
def test_skipped_resource(subject_reference):

    with pytest.raises(ValidationError):
        from_dict(
            {
                "resourceType": "ClinicalImpression",
                "status": "completed",
                "subject": subject_reference,
            }
        )
