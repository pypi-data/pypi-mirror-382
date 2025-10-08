from django.urls import path

from bank_transaction_bridge.views import (
    BankAccountCreateView,
    BankAccountDeleteView,
    BankAccountUpdateView,
    BankAccoutListView,
    ImportMappingDeleteView,
    ImportMappingListView,
    TransactionListView,
    import_bank_statement_view,
    ImportMappingCreateView,
    ImportMappingUpdateView,
)

app_name = "bank_transaction_bridge"

urlpatterns = [
    path(
        "bank-accounts/",
        BankAccoutListView.as_view(),
        name="bank_account_list",
    ),
    path(
        "bank-accounts/new",
        BankAccountCreateView.as_view(),
        name="bank_account_create",
    ),
    path(
        "bank-accounts/<int:pk>/update",
        BankAccountUpdateView.as_view(),
        name="bank_account_update",
    ),
    path(
        "bank-accounts/<int:pk>/delete",
        BankAccountDeleteView.as_view(),
        name="bank_account_delete",
    ),
    path(
        "import-mappings/",
        ImportMappingListView.as_view(),
        name="import_mapping_list",
    ),
    path(
        "import-mappings/new",
        ImportMappingCreateView.as_view(),
        name="import_mapping_create",
    ),
    path(
        "import-mappings/<int:pk>/update",
        ImportMappingUpdateView.as_view(),
        name="import_mapping_update",
    ),
    path(
        "import-mappings/<int:pk>/delete",
        ImportMappingDeleteView.as_view(),
        name="import_mapping_delete",
    ),
    path(
        "transactions/",
        TransactionListView.as_view(),
        name="transaction_list",
    ),
    path(
        "import",
        import_bank_statement_view,
        name="import_bank_statement",
    ),
]
