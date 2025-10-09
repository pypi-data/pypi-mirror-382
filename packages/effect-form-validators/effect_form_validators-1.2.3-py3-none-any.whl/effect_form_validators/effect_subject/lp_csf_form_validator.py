from typing import Any

from edc_constants.constants import NO, YES
from edc_crf.crf_form_validator import CrfFormValidator
from edc_csf.form_validators import (
    LpFormValidatorMixin,
    QuantitativeCsfFormValidatorMixin,
)
from edc_lab.form_validators import CrfRequisitionFormValidatorMixin


class LpCsfFormValidator(
    CrfRequisitionFormValidatorMixin,
    LpFormValidatorMixin,
    QuantitativeCsfFormValidatorMixin,
    CrfFormValidator,
):
    csf_culture_panel = None
    assay_datetime_field: str = "csf_culture_assay_datetime"
    requisition_field: str = "csf_requisition"

    def clean(self):
        self.validate_lp()
        self.validate_csf_assessment()
        self.validate_csf_culture(self.requisition_field)

    def validate_csf_assessment(self: Any):
        for fld in [
            "india_ink",
            "csf_crag_lfa",
            "sq_crag",
            "sq_crag_pos",
            "crf_crag_titre_done",
        ]:
            self.applicable_if(YES, NO, field="csf_positive", field_applicable=fld)

        self.required_if(YES, field="crf_crag_titre_done", field_required="crf_crag_titre")

    def validate_csf_culture(self: Any, requisition: str):
        self.require_together(
            field=requisition,
            field_required=self.assay_datetime_field,
        )
        self.validate_requisition(
            requisition, self.assay_datetime_field, self.csf_culture_panel
        )
