from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from urllib.parse import urlencode
from django.http import HttpResponse, Http404
from django.urls import reverse_lazy
from horilla_core.decorators import (
    htmx_required,
    permission_required,
    permission_required_or_denied,
)
from horilla_crm.accounts.filters import AccountFilter
from horilla_crm.accounts.forms import AccountFormClass, AddChildAccountForm
from horilla_crm.accounts.models import Account, PartnerAccountRelationship
from horilla_crm.contacts.models import ContactAccountRelationship
from horilla_generics.mixins import RecentlyViewedMixin
from horilla_generics.views import (
    HorillaActivitySectionView,
    HorillaNotesAttachementSectionView,
    HorillaSingleDeleteView,
    HorillaSingleFormView,
    HorillaKanbanView,
    HorillaDetailSectionView,
    HorillaHistorySectionView,
    HorillaDetailView,
    HorillaListView,
    HorillaMultiStepFormView,
    HorillaNavView,
    HorillaRelatedListSectionView,
    HorillaDetailTabView,
    HorillaView,
)
from functools import cached_property
from django.utils.translation import gettext_lazy as _
from horilla_utils.middlewares import _thread_local
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import FormView
from django.utils.decorators import method_decorator
from horilla_crm.opportunities.models import Opportunity, OpportunityContactRole
import logging

logger = logging.getLogger(__name__)


class AccountView(LoginRequiredMixin, HorillaView):
    """
    Render the accounts page
    """

    nav_url = reverse_lazy("accounts:accounts_nav_view")
    list_url = reverse_lazy("accounts:accounts_list_view")
    kanban_url = reverse_lazy("accounts:accounts_kanban_view")


@method_decorator(htmx_required, name="dispatch")
@method_decorator(
    permission_required(["accounts.view_account", "accounts.view_own_account"]),
    name="dispatch",
)
class AccountsNavbar(LoginRequiredMixin, HorillaNavView):
    """
    Navbar View for accounts page
    """

    nav_title = Account._meta.verbose_name_plural
    search_url = reverse_lazy("accounts:accounts_list_view")
    main_url = reverse_lazy("accounts:accounts_view")
    kanban_url = reverse_lazy("accounts:accounts_kanban_view")
    model_name = "Account"
    model_app_label = "accounts"
    filterset_class = AccountFilter

    @cached_property
    def new_button(self):
        if self.request.user.has_perm("accounts.add_account"):
            return {
                "url": f"""{ reverse_lazy('accounts:account_create_form_view')}?new=true""",
                "attrs": {"id": "account-create"},
            }

    @cached_property
    def actions(self):
        if self.request.user.has_perm(
            "accounts.view_account"
        ) or self.request.user.has_perm("accounts.view_own_account"):
            return [
                {
                    "action": "Kanban Settings",
                    "attrs": f"""
                            hx-get="{reverse_lazy('horilla_generics:create_kanban_group')}?model={self.model_name}&app_label={self.model_app_label}&exclude_fields=company"
                            onclick="openModal()"
                            hx-target="#modalBox"
                            hx-swap="innerHTML"
                            """,
                },
                {
                    "action": "Add column to list",
                    "attrs": f"""
                            hx-get="{reverse_lazy('horilla_generics:column_selector')}?app_label={self.model_app_label}&model_name={self.model_name}&url_name=accounts_list_view"
                            onclick="openModal()"
                            hx-target="#modalBox"
                            hx-swap="innerHTML"
                            """,
                },
            ]


@method_decorator(htmx_required, name="dispatch")
@method_decorator(
    permission_required_or_denied(
        ["accounts.view_account", "accounts.view_own_account"]
    ),
    name="dispatch",
)
class AccountListView(LoginRequiredMixin, HorillaListView):
    """
    account List view
    """

    model = Account
    view_id = "accounts-list"
    filterset_class = AccountFilter
    search_url = reverse_lazy("accounts:accounts_list_view")
    main_url = reverse_lazy("accounts:accounts_view")

    def no_record_add_button(self):
        if self.request.user.has_perm("accounts.add_account"):
            return {
                "url": f"""{reverse_lazy('accounts:account_create_form_view') }?new=true""",
                "attrs": 'id="account-create"',
            }

    @cached_property
    def columns(self):
        instance = self.model()
        return [
            (instance._meta.get_field("name").verbose_name, "name"),
            (instance._meta.get_field("account_number").verbose_name, "account_number"),
            (instance._meta.get_field("account_owner").verbose_name, "account_owner"),
            (
                instance._meta.get_field("account_type").verbose_name,
                "get_account_type_display",
            ),
            (
                instance._meta.get_field("account_source").verbose_name,
                "get_account_source_display",
            ),
            (instance._meta.get_field("annual_revenue").verbose_name, "annual_revenue"),
        ]

    @cached_property
    def col_attrs(self):
        query_params = self.request.GET.dict()
        query_params = {}
        if "section" in self.request.GET:
            query_params["section"] = self.request.GET.get("section")
        query_string = urlencode(query_params)
        attrs = {}
        if self.request.user.has_perm(
            "accounts.view_account"
        ) or self.request.user.has_perm("accounts.view_own_account"):
            attrs = {
                "hx-get": f"{{get_detail_url}}?{query_string}",
                "hx-target": "#mainContent",
                "hx-swap": "outerHTML",
                "hx-push-url": "true",
                "hx-select": "#mainContent",
                "style": "cursor:pointer",
                "class": "hover:text-primary-600",
            }
        return [
            {
                "name": {
                    **attrs,
                }
            }
        ]

    bulk_update_fields = ["account_type", "account_owner", "account_source", "industry"]

    @cached_property
    def actions(self):
        instance = self.model()
        actions = []

        show_actions = (
            self.request.user.is_superuser
            or self.request.user.has_perm("accounts:change_account")
            or self.get_queryset().filter(account_owner=self.request.user).exists()
        )
        if show_actions:
            actions.extend(
                [
                    {
                        "action": _("Edit"),
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                              hx-get="{get_edit_url}?new=true" 
                              hx-target="#modalBox"
                              hx-swap="innerHTML" 
                              onclick="openModal()"
                             """,
                    },
                    {
                        "action": _("Change Owner"),
                        "src": "assets/icons/a2.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_change_owner_url}" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ]
            )
            if self.request.user.has_perm("accounts.delete_account"):
                actions.append(
                    {
                        "action": "Delete",
                        "src": "assets/icons/a4.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                                hx-post="{get_delete_url}" 
                                hx-target="#deleteModeBox"
                                hx-swap="innerHTML" 
                                hx-trigger="click"
                                hx-vals='{{"check_dependencies": "true"}}'
                                onclick="openDeleteModeModal()"
                            """,
                    }
                )
        return actions


@method_decorator(htmx_required, name="dispatch")
@method_decorator(permission_required("accounts.delete_account"), name="dispatch")
class AccountDeleteView(LoginRequiredMixin, HorillaSingleDeleteView):
    """
    Delete view for account
    """

    model = Account

    def get_post_delete_response(self):
        return HttpResponse("<script>htmx.trigger('#reloadButton','click');</script>")


@method_decorator(
    permission_required_or_denied(
        ["accounts.view_account", "accounts.view_own_account"]
    ),
    name="dispatch",
)
class AccountsKanbanView(LoginRequiredMixin, HorillaKanbanView):
    """
    Kanban view for account
    """

    model = Account
    view_id = "account-kanban"
    filterset_class = AccountFilter
    search_url = reverse_lazy("accounts:accounts_list_view")
    main_url = reverse_lazy("accounts:accounts_view")
    group_by_field = "account_type"

    @cached_property
    def columns(self):
        instance = self.model()
        return [
            (instance._meta.get_field("name").verbose_name, "name"),
            (instance._meta.get_field("account_number").verbose_name, "account_number"),
            (instance._meta.get_field("account_owner").verbose_name, "account_owner"),
            (
                instance._meta.get_field("account_type").verbose_name,
                "get_account_type_display",
            ),
            (
                instance._meta.get_field("account_source").verbose_name,
                "get_account_source_display",
            ),
            (instance._meta.get_field("annual_revenue").verbose_name, "annual_revenue"),
        ]

    @cached_property
    def actions(self):
        instance = self.model()
        actions = []

        show_actions = (
            self.request.user.is_superuser
            or self.request.user.has_perm("accounts:change_account")
            or self.get_queryset().filter(account_owner=self.request.user).exists()
        )
        if show_actions:
            actions.extend(
                [
                    {
                        "action": _("Edit"),
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                              hx-get="{get_edit_url}?new=true" 
                              hx-target="#modalBox"
                              hx-swap="innerHTML" 
                              onclick="openModal()"
                             """,
                    },
                    {
                        "action": _("Change Owner"),
                        "src": "assets/icons/a2.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_change_owner_url}" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ]
            )
            if self.request.user.has_perm("accounts.delete_account"):
                actions.append(
                    {
                        "action": "Delete",
                        "src": "assets/icons/a4.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                                hx-post="{get_delete_url}" 
                                hx-target="#deleteModeBox"
                                hx-swap="innerHTML" 
                                hx-trigger="click"
                                hx-vals='{{"check_dependencies": "true"}}'
                                onclick="openDeleteModeModal()"
                            """,
                    }
                )
        return actions

    def no_record_add_button(self):
        if self.request.user.has_perm("accounts.add_account"):
            return {
                "url": f"""{ reverse_lazy('accounts:account_create')}?new=true""",
                "attrs": 'id="account-create"',
            }

    @cached_property
    def kanban_attrs(self):
        query_params = self.request.GET.dict()
        query_params = {}
        if "section" in self.request.GET:
            query_params["section"] = self.request.GET.get("section")
        query_string = urlencode(query_params)
        if self.request.user.has_perm(
            "accounts.view_account"
        ) or self.request.user.has_perm("accounts.view_own_account"):
            return f"""
                    hx-get="{{get_detail_url}}?{query_string}"
                    hx-target="#mainContent"
                    hx-swap="outerHTML"
                    hx-push-url="true"
                    hx-select="#mainContent"
                    style ="cursor:pointer",
                    """


@method_decorator(htmx_required, name="dispatch")
class AccountFormView(LoginRequiredMixin, HorillaMultiStepFormView):
    """
    form view for account
    """

    form_class = AccountFormClass
    model = Account
    fullwidth_fields = ["description"]
    fields = [
        "name",
        "account_source",
        "account_type",
        "rating",
        "phone",
        "parent_account",
        "fax",
        "account_number",
        "website",
        "site",
        "is_active",
        "is_customer_portal",
        "is_partner",
        "billing_city",
        "billing_state",
        "billing_district",
        "billing_zip",
        "shipping_city",
        "shipping_state",
        "shipping_district",
        "shipping_zip",
        "customer_priority",
        "industry",
        "number_of_employees",
        "annual_revenue",
        "ownership",
        "description",
        "account_owner",
        "operating_hours",
    ]
    total_steps = 4
    step_titles = {
        "1": "Account Information",
        "2": "Address Information",
        "3": "Additional Information",
        "4": "Description",
    }

    @cached_property
    def form_url(self):
        pk = self.kwargs.get("pk") or self.request.GET.get("id")
        if pk:
            return reverse_lazy("accounts:account_edit_form_view", kwargs={"pk": pk})
        return reverse_lazy("accounts:account_create_form_view")

    def get(self, request, *args, **kwargs):
        account_id = self.kwargs.get("pk")
        if account_id:
            try:
                account = get_object_or_404(Account, pk=account_id)
            except Exception as e:
                messages.error(request, e)
                return HttpResponse("<script>$('#reloadButton').click();</script>")

            if account.account_owner == request.user:
                return super().get(request, *args, **kwargs)

        if request.user.has_perm("accounts.change_account") or request.user.has_perm(
            "accounts.add_account"
        ):
            return super().get(request, *args, **kwargs)

        return render(request, "403.html")


@method_decorator(htmx_required, name="dispatch")
class AccountChangeOwnerForm(LoginRequiredMixin, HorillaSingleFormView):
    """
    Change owner form
    """

    model = Account
    fields = ["account_owner"]
    full_width_fields = ["account_owner"]
    modal_height = False
    form_title = _("Change Owner")

    @cached_property
    def form_url(self):
        pk = self.kwargs.get("pk") or self.request.GET.get("id")
        if pk:
            return reverse_lazy("accounts:account_change_owner", kwargs={"pk": pk})

    def get(self, request, *args, **kwargs):

        account_id = self.kwargs.get("pk")
        if account_id:
            account = get_object_or_404(Account, pk=account_id)
            if account.account_owner == request.user:
                return super().get(request, *args, **kwargs)

        if request.user.has_perm("accounts.change_account") or request.user.has_perm(
            "accounts.add_account"
        ):
            return super().get(request, *args, **kwargs)

        return render(request, "403.html")


@method_decorator(
    permission_required_or_denied(
        ["accounts.view_account", "accounts.view_own_account"]
    ),
    name="dispatch",
)
class AccountDetailView(RecentlyViewedMixin, LoginRequiredMixin, HorillaDetailView):
    """
    Detail view for account
    """

    model = Account
    breadcrumbs = [
        ("People", "accounts:accounts_view"),
        ("Accounts", "accounts:accounts_view"),
    ]
    body = [
        "name",
        "account_number",
        "account_owner",
        "account_type",
        "account_source",
        "annual_revenue",
    ]
    tab_url = reverse_lazy("accounts:account_detail_view_tabs")

    @cached_property
    def actions(self):
        instance = self.model()
        actions = []

        show_actions = (
            self.request.user.is_superuser
            or self.request.user.has_perm("accounts:change_account")
            or self.get_queryset().filter(account_owner=self.request.user).exists()
        )
        if show_actions:
            actions.extend(
                [
                    {
                        "action": _("Edit"),
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                              hx-get="{get_edit_url}?new=true" 
                              hx-target="#modalBox"
                              hx-swap="innerHTML" 
                              onclick="openModal()"
                             """,
                    },
                    {
                        "action": _("Change Owner"),
                        "src": "assets/icons/a2.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_change_owner_url}" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ]
            )
            if self.request.user.has_perm("accounts.delete_account"):
                actions.append(
                    {
                        "action": "Delete",
                        "src": "assets/icons/a4.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                                hx-post="{get_delete_url}" 
                                hx-target="#deleteModeBox"
                                hx-swap="innerHTML" 
                                hx-trigger="click"
                                hx-vals='{{"check_dependencies": "true"}}'
                                onclick="openDeleteModeModal()"
                            """,
                    }
                )
        return actions

    def get(self, request, *args, **kwargs):
        if not self.model.objects.filter(
            account_owner_id=self.request.user, pk=self.kwargs["pk"]
        ).first() and not self.request.user.has_perm("accounts.view_account"):
            from django.shortcuts import render

            return render(self.request, "403.html")
        return super().get(request, *args, **kwargs)


@method_decorator(
    permission_required_or_denied(
        ["accounts.view_account", "accounts.view_own_account"]
    ),
    name="dispatch",
)
class AccountDetailViewTabs(LoginRequiredMixin, HorillaDetailTabView):
    """
    Tab Views for account detail view
    """

    def __init__(self, **kwargs):
        request = getattr(_thread_local, "request", None)
        self.request = request
        self.object_id = self.request.GET.get("object_id")
        super().__init__(**kwargs)

    urls = {
        "details": "accounts:account_details_tab_view",
        "activity": "accounts:account_activity_tab_view",
        "related_lists": "accounts:account_related_list_tab_view",
        "notes_attachments": "accounts:account_notes_attachements",
        "history": "accounts:account_history_tab_view",
    }

    def get(self, request, *args, **kwargs):
        account_id = self.object_id
        user = request.user

        is_owner = Account.objects.filter(account_owner_id=user, pk=account_id).exists()
        has_permission = user.has_perm("accounts.view_account") or user.has_perm(
            "accounts.view_own_account"
        )

        if not (is_owner or has_permission):
            return render(request, "403.html", status=403)

        return super().get(request, *args, **kwargs)


@method_decorator(
    permission_required_or_denied(
        ["accounts.view_account", "accounts.view_own_account"]
    ),
    name="dispatch",
)
class AccountDetailsTab(LoginRequiredMixin, HorillaDetailSectionView):
    """
    Details Tab view of account detail view
    """

    model = Account

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.excluded_fields.append("account_owner")

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        user = request.user

        is_owner = Account.objects.filter(account_owner_id=user, pk=pk).exists()
        has_permission = user.has_perm("accounts.view_account")

        if not (is_owner or has_permission):
            return render(request, "403.html", status=403)

        return super().get(request, *args, **kwargs)


@method_decorator(
    permission_required_or_denied(
        ["accounts.view_account", "accounts.view_own_account"]
    ),
    name="dispatch",
)
class AccountActivityTab(LoginRequiredMixin, HorillaActivitySectionView):
    """
    account detain view activity tab
    """

    model = Account


@method_decorator(
    permission_required_or_denied(
        ["accounts.view_account", "accounts.view_own_account"]
    ),
    name="dispatch",
)
class AccountHistoryTab(LoginRequiredMixin, HorillaHistorySectionView):
    """
    History tab foe account detail view
    """

    model = Account


@method_decorator(
    permission_required_or_denied(
        ["accounts.view_account", "accounts.view_own_account"]
    ),
    name="dispatch",
)
class AccountRelatedListsTab(LoginRequiredMixin, HorillaRelatedListSectionView):
    """
    Related list tab view
    """

    model = Account

    @cached_property
    def related_list_config(self):
        query_params = {}
        if "section" in self.request.GET:
            query_params["section"] = self.request.GET.get("section")
        query_string = urlencode(query_params)
        pk = self.request.GET.get("object_id")
        referrer_url = "accout_detail_view"

        return {
            "child_accounts": {
                "title": _("Child Accounts"),
                "can_add": True,
                "add_url": reverse_lazy("accounts:create_child_accounts"),
                "columns": [
                    (Account._meta.get_field("name").verbose_name, "name"),
                    (
                        Account._meta.get_field("account_type").verbose_name,
                        "get_account_type_display",
                    ),
                    (
                        Account._meta.get_field("annual_revenue").verbose_name,
                        "annual_revenue",
                    ),
                ],
                "actions": [
                    {
                        "action": "edit",
                        "src": "/assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                        hx-get="{get_edit_url}" 
                        hx-target="#modalBox"
                        hx-swap="innerHTML" 
                        onclick="event.stopPropagation();openModal()"
                        hx-indicator="#modalBox"
                    """,
                    },
                    (
                        {
                            "action": "delete",
                            "src": "/assets/icons/a4.svg",
                            "img_class": "w-4 h-4",
                            "attrs": """
                        hx-post="{get_delete_url}" 
                        hx-target="#deleteModeBox"
                        hx-swap="innerHTML" 
                        hx-trigger="confirmed"
                        hx-on:click="hxConfirm(this,'Are you sure you want to delete this member?')"
                    """,
                        }
                        if self.request.user.has_perm("account.delete_account")
                        else {}
                    ),
                ],
            },
            "contact_relationships": {
                "title": _("Related Contacts"),
                "can_add": True,
                "add_url": reverse_lazy("accounts:create_account_contact_relation"),
                "columns": [
                    (
                        ContactAccountRelationship._meta.get_field("contact")
                        .related_model._meta.get_field("first_name")
                        .verbose_name,
                        "contact__first_name",
                    ),
                    (
                        ContactAccountRelationship._meta.get_field("contact")
                        .related_model._meta.get_field("last_name")
                        .verbose_name,
                        "contact__last_name",
                    ),
                    (
                        ContactAccountRelationship._meta.get_field("role").verbose_name,
                        "role",
                    ),
                ],
                "actions": [
                    {
                        "action": _("Edit"),
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_edit_account_contact_relation_url}?new=true" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ],
            },
            "partner_account": {
                "title": _("Partner"),
                "can_add": True,
                "add_url": reverse_lazy("accounts:account_partner_create_form"),
                "columns": [
                    (
                        PartnerAccountRelationship._meta.get_field("partner")
                        .related_model._meta.get_field("name")
                        .verbose_name,
                        "partner__name",
                    ),
                    (
                        PartnerAccountRelationship._meta.get_field("partner")
                        .related_model._meta.get_field("annual_revenue")
                        .verbose_name,
                        "partner__annual_revenue",
                    ),
                    (
                        PartnerAccountRelationship._meta.get_field("role").verbose_name,
                        "role",
                    ),
                ],
                "actions": [
                    {
                        "action": _("Edit"),
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_account_partner_url}?new=true" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ],
            },
        }

    excluded_related_lists = ["partner"]


@method_decorator(
    permission_required_or_denied(
        ["accounts.view_account", "accounts.view_own_account"]
    ),
    name="dispatch",
)
class AccountsNotesAndAttachments(
    LoginRequiredMixin, HorillaNotesAttachementSectionView
):

    model = Account


@method_decorator(htmx_required, name="dispatch")
class AddRelatedContactFormView(LoginRequiredMixin, HorillaSingleFormView):
    """
    Create and update form for adding related accounts into contacts
    """

    model = ContactAccountRelationship
    modal_height = False
    fields = ["contact", "account", "role"]
    form_title = _("Add Contact Relationships")
    full_width_fields = ["account", "contact", "role"]
    hidden_fields = ["account"]

    def get(self, request, *args, **kwargs):

        account_id = request.GET.get("id")
        if request.user.has_perm(
            "accounts.change_contactaccountrelationship"
        ) or request.user.has_perm("accounts.add_contactaccountrelationship"):
            return super().get(request, *args, **kwargs)

        if account_id:
            account = get_object_or_404(Account, pk=account_id)

            if account.account_owner == request.user:
                return super().get(request, *args, **kwargs)

        return render(request, "403.html")

    def form_valid(self, form):
        response = super().form_valid(form)
        contact_account_relation = form.instance
        contact = contact_account_relation.contact
        account = contact_account_relation.account
        role = contact_account_relation.role
        opportunities = Opportunity.objects.filter(account=account)
        for opportunity in opportunities:
            OpportunityContactRole.objects.get_or_create(
                contact=contact, opportunity=opportunity, defaults={"role": role}
            )
        return HttpResponse(
            "<script>htmx.trigger('#tab-contact_relationships-btn', 'click');closeModal();</script>"
        )

    def get_initial(self):
        initial = super().get_initial()
        id = self.request.GET.get("id")
        if id:
            initial["account"] = id
        return initial

    @cached_property
    def form_url(self):
        if self.kwargs.get("pk"):
            return reverse_lazy(
                "accounts:edit_account_contact_relation",
                kwargs={"pk": self.kwargs.get("pk")},
            )
        return reverse_lazy("accounts:create_account_contact_relation")


@method_decorator(htmx_required, name="dispatch")
class AddChildAccountFormView(LoginRequiredMixin, FormView):
    """
    Form view to select an existing account and assign it as a child account.
    """

    template_name = "single_form_view.html"
    form_class = AddChildAccountForm

    def get(self, request, *args, **kwargs):

        account_id = request.GET.get("id")
        if request.user.has_perm("accounts.change_account") or request.user.has_perm(
            "accounts.add_account"
        ):
            return super().get(request, *args, **kwargs)

        if account_id:
            try:
                account = get_object_or_404(Account, pk=account_id)
            except Http404:
                messages.error(request, f"Account not found or no longer exists.")
                return HttpResponse(
                    "<script>$('#reloadButton').click();closeModal();</script>"
                )
            if account.account_owner == request.user:
                return super().get(request, *args, **kwargs)

        return render(request, "403.html")

    def get_form_kwargs(self):
        """
        Pass the request to the form for queryset filtering and validation.
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_initial(self):
        """
        Prepopulate the form with initial data if needed.
        """
        initial = super().get_initial()
        parent_id = self.request.GET.get("id")

        if parent_id:
            try:
                parent_account = Account.objects.get(pk=parent_id)
                initial["parent_account"] = parent_account
            except Account.DoesNotExist:
                logger.error(f"Parent account with ID {parent_id} not found")  # Debug

        return initial

    def get_context_data(self, **kwargs):
        """
        Add context data for the template.
        """
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Add Child Account")
        context["full_width_fields"] = ["account"]  # Only for template display
        context["form_url"] = self.get_form_url()
        context["modal_height"] = False
        context["view_id"] = "add-child-account-form-view"
        context["condition_fields"] = []

        return context

    def form_valid(self, form):
        """
        Update the selected account's parent_account field and return HTMX response.
        """
        if not self.request.user.is_authenticated:
            messages.error(
                self.request, _("You must be logged in to perform this action.")
            )
            return self.form_invalid(form)

        selected_account = form.cleaned_data["account"]
        parent_account = form.cleaned_data[
            "parent_account"
        ]  # Get from form data instead of GET

        if not parent_account:
            form.add_error(None, _("No parent account specified in the request."))
            return self.form_invalid(form)

        try:

            if selected_account.id == parent_account.id:
                form.add_error("account", _("An account cannot be its own parent."))
                return self.form_invalid(form)

            if selected_account.parent_account:
                form.add_error(
                    "account", _("This account already has a parent account.")
                )
                return self.form_invalid(form)

            # Update the selected account
            selected_account.parent_account = parent_account
            selected_account.updated_at = timezone.now()
            selected_account.updated_by = self.request.user
            selected_account.save()

            messages.success(self.request, _("Child account assigned successfully!"))

        except ValueError as e:
            form.add_error(None, _("Invalid parent account ID format."))
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(
                None,
                _("An unexpected error occurred while assigning the child account."),
            )
            return self.form_invalid(form)

        return HttpResponse(
            "<script>htmx.trigger('#tab-contact_relationships-btn', 'click');closeModal();</script>"
        )

    def get_form_url(self):
        """
        Get the form URL for submission.
        """
        if self.kwargs.get("pk"):
            return reverse_lazy(
                "accounts:edit_child_account", kwargs={"pk": self.kwargs.get("pk")}
            )
        return reverse_lazy("accounts:create_child_accounts")


@method_decorator(htmx_required, name="dispatch")
class AccountPartnerFormView(LoginRequiredMixin, HorillaSingleFormView):
    """
    create and update from view for Account partner
    """

    model = PartnerAccountRelationship
    fields = ["partner", "role", "account"]
    full_width_fields = ["partner", "role", "account"]
    modal_height = False
    form_title = _("Account Partner")
    hidden_fields = ["account"]

    def get(self, request, *args, **kwargs):

        account_id = request.GET.get("id")
        if request.user.has_perm(
            "accounts.change_partneraccountrelationship"
        ) or request.user.has_perm("accounts.add_partneraccountrelationship"):
            return super().get(request, *args, **kwargs)

        if account_id:
            account = get_object_or_404(Account, pk=account_id)
            if account.account_owner == request.user:
                return super().get(request, *args, **kwargs)

        return render(request, "403.html")

    def form_valid(self, form):
        account = form.cleaned_data.get("account")
        role = form.cleaned_data.get("role")

        # Avoid duplicate (account, role) entries
        existing = PartnerAccountRelationship.objects.filter(account=account, role=role)
        if self.object:  # If update, exclude current instance
            existing = existing.exclude(pk=self.object.pk)

        if existing.exists():
            form.add_error(
                "role", _("This partner role is already assigned to this account.")
            )
            return self.form_invalid(form)

        response = super().form_valid(form)
        return HttpResponse(
            "<script>htmx.trigger('#tab-partner_account-btn', 'click');closeModal();</script>"
        )

    def get_initial(self):
        initial = super().get_initial()
        id = self.request.GET.get("id")
        if id:
            initial["account"] = id
        return initial

    @cached_property
    def form_url(self):
        if self.kwargs.get("pk"):
            return reverse_lazy(
                "accounts:account_partner_update_form",
                kwargs={"pk": self.kwargs.get("pk")},
            )
        return reverse_lazy("accounts:account_partner_create_form")
