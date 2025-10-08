import json
from pathlib import Path

from bank_transaction_bridge.models import BankAccount
from bank_transaction_bridge.schemas import TransactionSchema, Transaction

test_json_file = Path(__file__).parent / "fixtures" / "test_data.json"
test_bankstatement_csv_file = Path(__file__).parent / "bank_statement_csv_test_file.csv"


with open(test_json_file) as f:
    json_data = json.load(f)


def get_bank_account_test_data():
    return [
        data["fields"]
        for data in json_data
        if data["model"] == "bank_transaction_bridge.bankaccount"
    ]


def get_transaction_test_data():
    return [
        data["fields"]
        for data in json_data
        if data["model"] == "bank_transaction_bridge.transaction"
    ]


def create_test_bank_account():
    return BankAccount.objects.get_or_create(**get_bank_account_test_data()[0])[0]


def create_test_transaction():
    ba = create_test_bank_account()
    payload = TransactionSchema(**get_transaction_test_data()[0]).dict()
    payload["bank_account"] = ba
    return Transaction.objects.create(**payload)


def get_bank_statement_test_file(key="gls"):
    files = {
        "gls": test_bankstatement_csv_file,
    }
    return files[key]
