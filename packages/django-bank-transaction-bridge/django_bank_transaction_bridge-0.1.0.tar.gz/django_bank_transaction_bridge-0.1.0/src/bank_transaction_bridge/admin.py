from django.contrib import admin
from bank_transaction_bridge.models import BankAccount, ImportMapping, Transaction


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass


@admin.register(ImportMapping)
class ImportMappingAdmin(admin.ModelAdmin):
    pass
