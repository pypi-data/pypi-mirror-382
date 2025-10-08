from django import forms
from bank_transaction_bridge.models import BankAccount, ImportMapping
from bank_transaction_bridge.schemas import ImportMappingSchema
from pydantic import ValidationError as PydanticValidationError


class BankAccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bank_name"].widget.attrs.update({"class": "block input mb-3"})
        self.fields["alias"].widget.attrs.update({"class": "block input mb-3"})
        self.fields["account_number"].widget.attrs.update({"class": "block input mb-3"})
        self.fields["notes"].widget.attrs.update({"class": "block textarea mb-3"})

    class Meta:
        model = BankAccount
        fields = "__all__"


class ImportBankStatementForm(forms.Form):
    bank_account = forms.ModelChoiceField(
        queryset=BankAccount.objects.all(),
        widget=forms.Select(attrs={"class": "block select select-accent mb-3"}),
    )
    import_mapping = forms.ModelChoiceField(
        queryset=ImportMapping.objects.all(),
        widget=forms.Select(attrs={"class": "block select select-accent mb-3"}),
    )
    file = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={"class": "block file-input file-input-accent mb-3"}
        )
    )


class ImportMappingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "block input mb-3"})
        self.fields["mapping"].widget.attrs.update({"class": "block textarea mb-3"})

    class Meta:
        model = ImportMapping
        fields = "__all__"

    def clean_mapping(self):
        mapping_data = self.cleaned_data.get("mapping", {})
        try:
            ImportMappingSchema(**mapping_data)
        except PydanticValidationError as verr:
            error_dict = {}
            for err in verr.errors():
                field_name = err["loc"][0]
                message = f"{err['msg']}"
                error_dict[field_name] = message
            raise forms.ValidationError(f"Validation failed: {error_dict}")
        return mapping_data
