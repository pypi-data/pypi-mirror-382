from django.db import models
from django.forms import model_to_dict


class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    bank_account = models.ForeignKey("BankAccount", on_delete=models.PROTECT)
    booking_date = models.DateField()
    payment_participant = models.CharField(max_length=255)
    payment_participant_account = models.CharField(max_length=255)
    amount = models.FloatField()
    currency = models.CharField(max_length=10)
    reference = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    transcation_text = models.TextField(null=True, blank=True)
    balance_after_booking = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-booking_date", "payment_participant"]

    def __str__(self) -> str:
        return f"{self.bank_account.alias if self.bank_account.alias else self.bank_account.bank_name}: {self.booking_date}: {self.payment_participant}"

    def get_data(self):
        data = model_to_dict(self)
        data["transaction_pk"] = self.pk
        return data


class BankAccount(models.Model):
    bank_name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=64)
    notes = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.alias if self.alias else self.bank_name


def get_default_mapping():
    return {
        "booking_date": "Buchungstag",
        "payment_participant": "Name Zahlungsbeteiligter",
        "payment_participant_account": "IBAN Zahlungsbeteiligter",
        "amount": "Betrag",
        "currency": "Waehrung",
        "reference": "Verwendungszweck",
        "transcation_text": "Buchungstext",
        "balance_after_booking": "Saldo nach Buchung",
    }


class ImportMapping(models.Model):
    name = models.CharField(max_length=255)
    mapping = models.JSONField(default=get_default_mapping)

    def __str__(self) -> str:
        return self.name


class AbstractTransactionBridge(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        related_name="connected_item",
        null=True,
        blank=True,
    )

    @classmethod
    def create_object(cls, transaction_data):
        raise NotImplementedError(
            f"{cls.__name__} must implement the class method 'create_object'"
        )

    def get_absolute_url(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the method 'get_absolute_url'"
        )

    class Meta:
        abstract = True
