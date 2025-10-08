from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Min, ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from bank_transaction_bridge.forms import (
    BankAccountForm,
    ImportBankStatementForm,
    ImportMappingForm,
)
from bank_transaction_bridge.models import BankAccount, ImportMapping, Transaction
from .convertors.file_to_json_convertor import (
    CSVFielToBridgeJSONConvertor,
)
from .convertors.json_to_transactions_convertor import (
    JSONToTransactionsConvertor,
)


class BulkDeleteMixin:
    confirm_param = "confirm_ids"
    delete_param = "selected_item_ids"

    def get_success_url(self):
        if hasattr(self, "success_url") and self.success_url:
            return str(self.success_url)  # reverse_lazy resolves lazily
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} is missing a success_url. "
            "Define success_url or override get_success_url()."
        )

    def post(self, request, *args, **kwargs):
        ids_to_delete = request.POST.getlist("selected_item_ids")
        if ids_to_delete:
            try:
                self.model.objects.filter(id__in=ids_to_delete).delete()
                messages.success(request, "Selected items were deleted successfully.")
            except ProtectedError as e:
                protected_items = e.protected_objects
                messages.error(
                    request,
                    f"Cannot delete some items because they are in use: {', '.join(str(obj) for obj in protected_items)}",
                )
            return redirect(self.get_success_url())
        selected_ids = request.POST.getlist("items")
        if selected_ids:
            ids_param = ",".join(selected_ids)
            return redirect(
                f"{self.get_success_url()}?{self.confirm_param}={ids_param}"
            )

        return redirect(self.get_success_url())

    def get_queryset(self):
        queryset = super().get_queryset()
        confirm_ids = self.request.GET.get(self.confirm_param)
        if confirm_ids:
            return queryset.filter(id__in=confirm_ids.split(","))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_to_delete"] = bool(self.request.GET.get(self.confirm_param))
        context["items"] = context["object_list"]
        return context


class DeleteViewWithError(DeleteView):
    def form_valid(self, form):
        success_url = self.get_success_url()
        try:
            self.object.delete()
            messages.success(self.request, "Selected item was deleted successfully.")
        except ProtectedError as e:
            protected_items = e.protected_objects
            messages.error(
                self.request,
                f'Cannot delete selected item "{self.object}" because it is in use: {", ".join(str(obj) for obj in protected_items)}',
            )
        return HttpResponseRedirect(success_url)


class BankAccountCreateView(CreateView):
    model = BankAccount
    form_class = BankAccountForm
    success_url = reverse_lazy("bank_transaction_bridge:bank_account_list")


class BankAccountUpdateView(UpdateView):
    model = BankAccount
    form_class = BankAccountForm
    success_url = reverse_lazy("bank_transaction_bridge:bank_account_list")


class BankAccountDeleteView(DeleteViewWithError):
    model = BankAccount
    success_url = reverse_lazy("bank_transaction_bridge:bank_account_list")


class BankAccoutListView(BulkDeleteMixin, ListView):
    model = BankAccount
    success_url = reverse_lazy("bank_transaction_bridge:bank_account_list")


class ImportMappingCreateView(CreateView):
    model = ImportMapping
    form_class = ImportMappingForm
    success_url = reverse_lazy("bank_transaction_bridge:import_mapping_list")


class ImportMappingUpdateView(UpdateView):
    model = ImportMapping
    form_class = ImportMappingForm
    success_url = reverse_lazy("bank_transaction_bridge:import_mapping_list")


class ImportMappingDeleteView(DeleteViewWithError):
    model = ImportMapping
    success_url = reverse_lazy("bank_transaction_bridge:import_mapping_list")


class ImportMappingListView(BulkDeleteMixin, ListView):
    model = ImportMapping
    success_url = reverse_lazy("bank_transaction_bridge:import_mapping_list")


class TransactionListView(BulkDeleteMixin, ListView):
    model = Transaction
    template_name = "bank_transaction_bridge/transaction_list.html"
    success_url = reverse_lazy("bank_transaction_bridge:transaction_list")

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action and action.startswith("create_connected_item"):
            item_id = action.replace("create_connected_item_", "")
            model_path = getattr(settings, "CONNECTED_ITEM_CLASS", None)
            if not model_path:
                messages.error(
                    self.request,
                    "CONNECTED_ITEM_CLASS not defined in settings",
                )
            else:
                app_label, model_name = model_path.split(".")
                try:
                    ConnectedModelClass = apps.get_model(app_label, model_name)
                    transaction_data = Transaction.objects.get(pk=item_id).get_data()
                    transaction_data["transaction_pk"] = item_id
                    ConnectedModelClass.create_object(transaction_data)
                except (LookupError, ValueError) as err:
                    messages.error(self.request, str(err))

        if "remove_duplicates" in request.POST:
            self._remove_duplicate_transactions()
            return redirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["connected_item_class"] = getattr(settings, "CONNECTED_ITEM_CLASS", None)
        return data

    def _remove_duplicate_transactions(self):
        fields = [
            f.name
            for f in Transaction._meta.fields
            if f.name not in ("id", "created_at")
        ]
        earliest_ids = (
            Transaction.objects.values(*fields)
            .annotate(min_id=Min("id"))
            .values_list("min_id", flat=True)
        )
        Transaction.objects.exclude(id__in=earliest_ids).delete()


def _get_file_to_json_convertor_class(file):
    extension = file.name.rsplit(".", 1)[-1].lower()
    return {"csv": CSVFielToBridgeJSONConvertor}.get(extension)


def import_bank_statement_view(request):
    template = "bank_transaction_bridge/import_file.html"
    result = None
    if request.method == "POST":
        form = ImportBankStatementForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            bank_account = form.cleaned_data["bank_account"]
            import_mapping_object = form.cleaned_data["import_mapping"]
            if not (convertor := _get_file_to_json_convertor_class(file)):
                raise NotImplementedError(
                    f"File {file.name} cannot be converted to JSON. No convertor found for type {file.name.split('.')[0]}."
                )
            json_data = convertor(file, import_mapping_object.mapping).get_json_data()
            result = JSONToTransactionsConvertor(bank_account, json_data).get_result()
    else:
        if not ImportMapping.objects.all():
            return render(request, template, {"nomapping": True})
        form = ImportBankStatementForm()

    return render(
        request,
        template,
        {"form": form, "result": result},
    )
