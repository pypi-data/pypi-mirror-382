from __future__ import annotations

from django import forms
from edc_constants.constants import FEMALE, MALE, NO, NOT_APPLICABLE, OTHER, PENDING, POS, YES
from edc_form_validators import INVALID_ERROR, FormValidator
from edc_prn.modelform_mixins import PrnFormValidatorMixin
from edc_screening.form_validator_mixins import SubjectScreeningFormValidatorMixin

THREE_DAYS = 3
MAX_AGE = 120
MIN_AGE = 18


class SubjectScreeningFormValidator(
    SubjectScreeningFormValidatorMixin,
    PrnFormValidatorMixin,
    FormValidator,
):
    def clean(self) -> None:
        self.get_consent_definition_or_raise()
        self.validate_age()
        self.validate_hiv()
        self.validate_cd4()
        self.validate_serum_crag()
        self.validate_lp_and_csf_crag()
        self.validate_cm_in_csf()
        self.validate_mg_ssx()
        self.validate_pregnancy()
        self.validate_suitability_for_study()

    @property
    def age_in_years(self) -> int | None:
        return self.cleaned_data.get("age_in_years")

    def validate_hiv(self):
        self.required_if(
            YES,
            field="hiv_pos",
            field_required="hiv_confirmed_date",
        )
        self.date_before_report_datetime_or_raise(field="hiv_confirmed_date", inclusive=True)
        self.applicable_if(YES, field="hiv_pos", field_applicable="hiv_confirmed_method")

    def validate_cd4(self) -> None:
        self.date_before_report_datetime_or_raise(field="cd4_date", inclusive=True)

    def validate_serum_crag(self) -> None:
        if self.cleaned_data.get("serum_crag_value") != POS:
            raise forms.ValidationError(
                {
                    "serum_crag_value": (
                        "Invalid. Subject must have positive serum/plasma CrAg test result."
                    )
                }
            )
        self.date_before_report_datetime_or_raise(field="serum_crag_date", inclusive=True)

    def validate_lp_and_csf_crag(self) -> None:
        self.required_if(YES, field="lp_done", field_required="lp_date")

        if self.cleaned_data.get("lp_date") and self.cleaned_data.get("serum_crag_date"):
            days = (
                self.cleaned_data.get("serum_crag_date") - self.cleaned_data.get("lp_date")
            ).days

            if days > THREE_DAYS:
                raise forms.ValidationError(
                    {
                        "lp_date": "Invalid. "
                        "LP cannot be more than 3 days before serum/plasma CrAg date"
                    }
                )

        self.date_before_report_datetime_or_raise(field="lp_date", inclusive=True)

        self.applicable_if(NO, field="lp_done", field_applicable="lp_declined")

        self.applicable_if(YES, field="lp_done", field_applicable="csf_crag_value")

    def validate_cm_in_csf(self) -> None:
        self.applicable_if(YES, field="lp_done", field_applicable="cm_in_csf")
        self.required_if(PENDING, field="cm_in_csf", field_required="cm_in_csf_date")
        self.applicable_if(YES, field="cm_in_csf", field_applicable="cm_in_csf_method")
        self.required_if(
            OTHER, field="cm_in_csf_method", field_required="cm_in_csf_method_other"
        )
        if (
            self.cleaned_data.get("cm_in_csf_date")
            and self.cleaned_data.get("lp_date")
            and (self.cleaned_data.get("lp_date") > self.cleaned_data.get("cm_in_csf_date"))
        ):
            raise forms.ValidationError(
                {"cm_in_csf_date": "Invalid. Cannot be before LP date"}
            )

        self.date_after_report_datetime_or_raise(field="cm_in_csf_date", inclusive=True)

    def validate_pregnancy(self) -> None:
        if (
            self.cleaned_data.get("gender") == MALE
            and self.cleaned_data.get("pregnant") != NOT_APPLICABLE
        ):
            raise forms.ValidationError({"pregnant": "Invalid. Subject is male"})
        if self.cleaned_data.get("gender") == MALE and self.cleaned_data.get("preg_test_date"):
            raise forms.ValidationError({"preg_test_date": "Invalid. Subject is male"})
        self.date_before_report_datetime_or_raise(field="preg_test_date", inclusive=True)
        self.applicable_if(FEMALE, field="gender", field_applicable="breast_feeding")

    def validate_age(self) -> None:
        if self.age_in_years is not None and not (0 <= self.age_in_years < MAX_AGE):
            self.raise_validation_error(
                {"age_in_years": "Invalid. Please enter a valid age in years."},
                INVALID_ERROR,
            )

        is_minor = self.age_in_years is not None and self.age_in_years < MIN_AGE
        self.applicable_if_true(is_minor, field_applicable="parent_guardian_consent")

        if is_minor and self.cleaned_data.get("parent_guardian_consent") != YES:
            self.raise_validation_error(
                {
                    "parent_guardian_consent": (
                        "STOP. You must have consent from parent or "
                        "legal guardian to store patient information."
                    )
                },
                INVALID_ERROR,
            )

    def validate_mg_ssx(self) -> None:
        self.validate_other_specify(
            field="any_other_mg_ssx",
            other_specify_field="any_other_mg_ssx_other",
            other_stored_value=YES,
        )

    def validate_suitability_for_study(self):
        self.applicable_if(
            YES, field="unsuitable_for_study", field_applicable="unsuitable_reason"
        )
        self.validate_other_specify(
            field="unsuitable_reason",
            other_specify_field="unsuitable_reason_other",
            other_stored_value=OTHER,
        )
        self.applicable_if(
            OTHER, field="unsuitable_reason", field_applicable="unsuitable_agreed"
        )
        if self.cleaned_data.get("unsuitable_agreed") == NO:
            raise forms.ValidationError(
                {
                    "unsuitable_agreed": "The study coordinator MUST agree "
                    "with your assessment. Please discuss before continuing."
                }
            )
