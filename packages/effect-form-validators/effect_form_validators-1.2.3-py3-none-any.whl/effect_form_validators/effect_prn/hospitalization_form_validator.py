from __future__ import annotations

from edc_constants.constants import YES
from edc_form_validators import INVALID_ERROR
from edc_form_validators.form_validator import FormValidator


class HospitalizationFormValidator(FormValidator):
    def clean(self):
        self.validate_discharged_date()

        self.required_if(YES, field="lp_performed", field_required="lp_count")

        self.applicable_if(YES, field="lp_performed", field_applicable="csf_positive_cm")

        self.validate_csf_positive_cm_date()

        self.required_if(YES, field="have_details", field_required="narrative", inverse=False)

    def validate_discharged_date(self):
        self.required_if(YES, field="discharged", field_required="discharged_date")

        if (
            self.cleaned_data.get("discharged_date")
            and self.cleaned_data.get("admitted_date")
            and (
                self.cleaned_data.get("discharged_date")
                < self.cleaned_data.get("admitted_date")
            )
        ):
            self.raise_validation_error(
                {"discharged_date": "Invalid. Cannot be before date admitted."},
                INVALID_ERROR,
            )

        self.applicable_if(
            YES, field="discharged", field_applicable="discharged_date_estimated"
        )

    def validate_csf_positive_cm_date(self):
        self.required_if(YES, field="csf_positive_cm", field_required="csf_positive_cm_date")

        if self.cleaned_data.get("csf_positive_cm_date"):
            if self.cleaned_data.get("admitted_date") and (
                self.cleaned_data.get("csf_positive_cm_date")
                < self.cleaned_data.get("admitted_date")
            ):
                self.raise_validation_error(
                    {"csf_positive_cm_date": "Invalid. Cannot be before date admitted."},
                    INVALID_ERROR,
                )

            if self.cleaned_data.get("discharged_date") and (
                self.cleaned_data.get("csf_positive_cm_date")
                > self.cleaned_data.get("discharged_date")
            ):
                self.raise_validation_error(
                    {"csf_positive_cm_date": "Invalid. Cannot be after date discharged."},
                    INVALID_ERROR,
                )
