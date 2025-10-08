from datetime import datetime
from typing import Optional
from ninja import ModelSchema, Schema
from pydantic import ConfigDict, field_validator
from .models import Transaction, BankAccount


class TransactionSchema(ModelSchema):
    class Meta:
        model = Transaction
        exclude = ["created_at", "id", "bank_account"]

    @field_validator(
        "amount", "balance_after_booking", mode="before", check_fields=False
    )
    @classmethod
    def parse_german_float(cls, v):
        """
        Accept German-style floats (e.g. "606,79") and convert to Python float.
        """
        if isinstance(v, str):
            v = v.replace(",", ".")
        return float(v)

    @field_validator("booking_date", mode="before", check_fields=False)
    @classmethod
    def parse_date(cls, v):
        try:
            return datetime.fromisoformat(v)
        except ValueError:
            try:
                return datetime.strptime(v, "%d.%m.%Y").date()
            except ValueError:
                raise ValueError(f"Invalid date format: {v}")

    @field_validator(
        "payment_participant",
        "payment_participant_account",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def parse_none_to_string(cls, v):
        if v is None:
            v = "none"
        return str(v)


class BankAccountSchema(ModelSchema):
    class Meta:
        model = BankAccount
        exclude = ["id"]


class ImportMappingSchema(Schema):
    model_config = ConfigDict(extra="forbid")

    booking_date: str
    payment_participant: str
    payment_participant_account: str
    amount: str
    currency: str
    reference: Optional[str] = None
    decscription: Optional[str] = None
    transcation_text: Optional[str] = None
    balance_after_booking: Optional[str] = None
