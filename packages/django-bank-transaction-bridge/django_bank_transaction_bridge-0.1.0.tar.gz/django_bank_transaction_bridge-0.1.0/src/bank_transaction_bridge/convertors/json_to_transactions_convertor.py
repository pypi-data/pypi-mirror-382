from django.db.transaction import atomic
from pydantic import ValidationError
from bank_transaction_bridge.models import Transaction
from bank_transaction_bridge.schemas import TransactionSchema


def format_pydantic_validation_error(err):
    return {
        "type": err.get("type"),
        "field": err.get("loc"),
        "message": err.get("msg"),
        "input": err.get("input"),
    }


class ConversionResult:
    SUCCESS_MESSAGE = "Converstion suceeded!"
    FAILURE_MESSAGE = "Some errors occured. Conversion not suceeded."

    def __init__(self):
        self._message = self.SUCCESS_MESSAGE
        self._errors = []

    def add_error(self, error):
        if error:
            self._errors.append(error)
            self._message = self.FAILURE_MESSAGE

    def get_errors(self):
        return self._errors

    def get_message(self):
        return self._message


class JSONToTransactionsConvertor:
    def __init__(self, bank_account, json_data_dict, parsers=None):
        self.bank_account = bank_account
        self.json_data_dict = json_data_dict
        self.parsers = parsers
        self._result = ConversionResult()
        self._convert()

    @atomic
    def _convert(self):
        for data in self.json_data_dict:
            try:
                validated = TransactionSchema(**data)
            except ValidationError as verr:
                for error in verr.errors():
                    self._result.add_error(format_pydantic_validation_error(error))
                return
            payload = validated.dict()
            payload["bank_account"] = self.bank_account
            Transaction.objects.create(**payload)

    def get_result(self):
        return self._result
