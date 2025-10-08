from django.test import TestCase
from bank_transaction_bridge.models import BankAccount, Transaction
from bank_transaction_bridge.schemas import BankAccountSchema, TransactionSchema
from bank_transaction_bridge.tests.utils import (
    get_bank_account_test_data,
    get_transaction_test_data,
)


class ImportJsonTestCase(TestCase):
    def test_create_bank_statement(self):
        test_data = get_bank_account_test_data()
        for data in test_data:
            # Validate with Ninja/Pydantic
            validated = BankAccountSchema(**data)
            # Create Django object
            bs = BankAccount.objects.create(**validated.dict())
            assert bs.bank_name == data["bank_name"]

    def test_create_transaction(self):
        test_data = get_transaction_test_data()
        bs = BankAccount.objects.create(**get_bank_account_test_data()[0])
        for data in test_data:
            validated = TransactionSchema(**data)
            payload = validated.dict()
            payload["bank_account"] = bs
            tr = Transaction.objects.create(**payload)
            assert tr.payment_participant == data["payment_participant"]
            assert tr.amount == data["amount"]
            assert tr.description == data["description"]
