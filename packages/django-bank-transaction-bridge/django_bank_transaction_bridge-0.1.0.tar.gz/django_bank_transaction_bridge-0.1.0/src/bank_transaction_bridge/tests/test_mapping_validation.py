from django.test import TestCase
from bank_transaction_bridge.forms import ImportMappingForm


default_mapping = {
    "booking_date": "Buchungstag",
    "payment_participant": "Name Zahlungsbeteiligter",
    "payment_participant_account": "IBAN Zahlungsbeteiligter",
    "amount": "Betrag",
    "currency": "Waehrung",
    "reference": "Verwendungszweck",
    "transcation_text": "Buchungstext",
    "balance_after_booking": "Saldo nach Buchung",
}


class ImportMappingFormValidationTestCase(TestCase):
    def test_correct_mapping(self):
        form_data = {
            "name": "test",
            "mapping": default_mapping,
        }
        form = ImportMappingForm(data=form_data)
        assert form.is_valid()
        im = form.save()
        assert im.mapping == default_mapping

    def test_wrong_mapping_type(self):
        test_mapping = default_mapping.copy()
        test_mapping["booking_date"] = 1234
        test_mapping["amount"] = None

        form_data = {"name": "test", "mapping": test_mapping}
        form = ImportMappingForm(data=form_data)
        assert not form.is_valid()
        errors = form.errors.as_data()["mapping"][0].messages[0]
        assert "booking_date" in errors
        assert "amount" in errors

    def test_missing_mapping_type(self):
        test_mapping = default_mapping.copy()
        test_mapping.pop("amount")
        test_mapping.pop("reference")  # optional

        form_data = {"name": "test", "mapping": test_mapping}
        form = ImportMappingForm(data=form_data)
        assert not form.is_valid()
        errors = form.errors.as_data()["mapping"][0].messages[0]
        assert "amount" in errors
        # reference is optional, so should not be in errors
        assert "reference" not in errors

    def test_redundant_mapping_type(self):
        test_mapping = default_mapping.copy()
        test_mapping.update({"nothing": "hoho"})

        form_data = {"name": "test", "mapping": test_mapping}
        form = ImportMappingForm(data=form_data)
        assert not form.is_valid()
        errors = form.errors.as_data()["mapping"][0].messages[0]
        assert "nothing" in errors
