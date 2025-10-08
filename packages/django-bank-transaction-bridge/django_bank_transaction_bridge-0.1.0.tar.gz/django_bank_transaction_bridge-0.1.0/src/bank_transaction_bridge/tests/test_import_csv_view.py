from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse_lazy

from bank_transaction_bridge.models import ImportMapping
from bank_transaction_bridge.tests.utils import (
    create_test_bank_account,
    get_bank_statement_test_file,
)


class ImportViewTest(TestCase):
    def test_import_bank_statement_view_tet(self):
        response = self.client.get(
            reverse_lazy("bank_transaction_bridge:import_bank_statement")
        )
        assert response.status_code == 200

    def test_import_bank_statement_view_post(self):
        response = self.client.post(
            reverse_lazy("bank_transaction_bridge:import_bank_statement")
        )
        # requiered fields
        errors_data = response.context["form"].errors.as_data()
        assert errors_data["bank_account"][0].code == "required"
        assert errors_data["file"][0].code == "required"

        create_test_bank_account()
        with open(get_bank_statement_test_file(), "rb") as f:
            uploaded_file = SimpleUploadedFile(
                f.name, f.read(), content_type="text/csv"
            )
        ImportMapping.objects.create(name="test")
        response = self.client.post(
            reverse_lazy("bank_transaction_bridge:import_bank_statement"),
            data={"bank_account": 1, "import_mapping": 1, "file": uploaded_file},
        )
        print(response.context["result"].get_errors())
        assert response.status_code == 200
