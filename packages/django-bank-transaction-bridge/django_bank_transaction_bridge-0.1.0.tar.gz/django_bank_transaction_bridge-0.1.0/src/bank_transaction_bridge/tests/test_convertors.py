from django.test import TestCase
from bank_transaction_bridge.models import BankAccount, ImportMapping
from bank_transaction_bridge.tests.utils import (
    get_bank_account_test_data,
    get_bank_statement_test_file,
)
from bank_transaction_bridge.convertors.file_to_json_convertor import (
    CSVFielToBridgeJSONConvertor,
)
from bank_transaction_bridge.convertors.json_to_transactions_convertor import (
    JSONToTransactionsConvertor,
)


class CSVFileConvertorTest(TestCase):
    def setUp(self):
        self.csv_mapping = ImportMapping.objects.create(name="test_mapping").mapping

    def test_get_json_data_dict(self):
        convertor = CSVFielToBridgeJSONConvertor(
            file=get_bank_statement_test_file(), mapping=self.csv_mapping
        )

        json_data = convertor.get_json_data()
        assert len(json_data) == 10
        assert self.csv_mapping.keys() == json_data[0].keys()


class JSONToTransactionsConvertorTestCase(TestCase):
    def setUp(self) -> None:
        self.csv_mapping = ImportMapping.objects.create(name="test_mapping").mapping
        self.ba = BankAccount.objects.create(**get_bank_account_test_data()[0])

    def test_json_to_transaction_errors(self):
        json_data = CSVFielToBridgeJSONConvertor(
            file=get_bank_statement_test_file(), mapping=self.csv_mapping
        ).get_json_data()
        result = JSONToTransactionsConvertor(
            bank_account=self.ba, json_data_dict=json_data
        ).get_result()
        errors = result.get_errors()
        print(errors)
        assert not errors
