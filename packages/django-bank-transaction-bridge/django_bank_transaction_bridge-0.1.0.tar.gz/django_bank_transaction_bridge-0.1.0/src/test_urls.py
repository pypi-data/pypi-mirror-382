from django.urls import include, path

# urlpatterns = [
#     path(
#         "",
#         include(("bank_transaction_bridge.urls", "bank_transaction_bridge"), namespace="bank_transaction_bridge"),
#     ),
# ]

urlpatterns = [
    path("bank_transaction_bridge/", include("bank_transaction_bridge.urls")),
]
