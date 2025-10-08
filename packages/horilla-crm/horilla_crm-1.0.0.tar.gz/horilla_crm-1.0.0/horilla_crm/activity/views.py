"""
Views for the CRM utilities module.

This file contains the view functions or classes that handle HTTP
requests and responses for the CRM application.
"""

from urllib.parse import urlencode
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.utils.functional import cached_property  # type: ignore
from django.urls import reverse_lazy
from horilla_crm.activity.filters import ActivityFilter
from horilla_crm.activity.forms import EventForm
from horilla_generics.mixins import RecentlyViewedMixin
from horilla_mail.models import HorillaMail
from .models import Activity
from django.utils.translation import gettext_lazy as _
from horilla_generics.views import (
    HorillaSingleDeleteView,
    HorillaKanbanView,
    HorillaDetailSectionView,
    HorillaHistorySectionView,
    HorillaDetailView,
    HorillaListView,
    HorillaNavView,
    HorillaDetailTabView,
    HorillaView,
    HorillaSingleFormView,
)
from horilla_utils.middlewares import _thread_local
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    ActivityCreateForm,
    EventForm,
    LogCallForm,
    MeetingsForm,
)
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from horilla_core.decorators import (
    htmx_required,
    permission_required,
    permission_required_or_denied,
)
from django.db.models import Q
from django.apps import apps
from django.db import models
from django.contrib import messages


class ActivityView(LoginRequiredMixin, HorillaView):
    """
    Render the activity page.
    """

    nav_url = reverse_lazy("activity:activity_nav_view")
    list_url = reverse_lazy("activity:activity_list_view")
    kanban_url = reverse_lazy("activity:activity_kanban_view")


@method_decorator(
    permission_required(["activity.view_activity", "activity.view_own_activity"]),
    name="dispatch",
)
class ActivityNavbar(LoginRequiredMixin, HorillaNavView):

    nav_title = Activity._meta.verbose_name_plural
    search_url = reverse_lazy("activity:activity_list_view")
    main_url = reverse_lazy("activity:activity_view")
    filterset_class = ActivityFilter
    kanban_url = reverse_lazy("activity:activity_kanban_view")
    model_name = "Activity"
    model_app_label = "activity"

    @cached_property
    def new_button(self):
        if self.request.user.has_perm("activity.add_activity"):
            return {
                "url": f"""{ reverse_lazy('activity:activity_create_form')}?new=true""",
            }

    @cached_property
    def actions(self):
        if self.request.user.has_perm(
            "activity.view_activity"
        ) or self.request.user.has_perm("activity.view_own_activity"):
            return [
                {
                    "action": "Kanban Settings",
                    "attrs": f"""
                            hx-get="{reverse_lazy('horilla_generics:create_kanban_group')}?model={self.model_name}&app_label={self.model_app_label}"
                            onclick="openModal()"
                            hx-target="#modalBox"
                            hx-swap="innerHTML"
                            hx-vals='{{"include_fields": "status,task_priority"}}'                           
                            """,
                },
                {
                    "action": "Add column to list",
                    "attrs": f"""
                            hx-get="{reverse_lazy('horilla_generics:column_selector')}?app_label={self.model_app_label}&model_name={self.model_name}&url_name=activity_list_view"
                            onclick="openModal()"
                            hx-target="#modalBox"
                            hx-swap="innerHTML"
                            """,
                },
            ]


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
class AllActivityListView(LoginRequiredMixin, HorillaListView):
    """
    Activity List view
    """

    model = Activity
    view_id = "activity-list"
    filterset_class = ActivityFilter
    search_url = reverse_lazy("activity:activity_list_view")
    main_url = reverse_lazy("activity:activity_view")
    bulk_update_fields = [
        "status",
    ]

    @cached_property
    def col_attrs(self):
        query_params = {}
        if "section" in self.request.GET:
            query_params["section"] = self.request.GET.get("section")
        query_string = urlencode(query_params)
        attrs = {}
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
                "subject": {
                    **attrs,
                }
            }
        ]

    @cached_property
    def columns(self):
        instance = self.model()
        return [
            (instance._meta.get_field("subject").verbose_name, "subject"),
            (instance._meta.get_field("description").verbose_name, "description"),
            (
                instance._meta.get_field("activity_type").verbose_name,
                "get_activity_type_display",
            ),
            (instance._meta.get_field("source").verbose_name, "source"),
            (_("Related To"), "related_object"),
            (instance._meta.get_field("status").verbose_name, "get_status_display"),
        ]

    @cached_property
    def actions(self):
        """
        Return actions if user is superuser, has global perms, or owns any lead in the queryset.
        Actions are shown globally (for all rows) but backend views enforce ownership/perms.
        """
        instance = self.model()
        actions = []

        show_actions = (
            self.request.user.is_superuser
            or self.request.user.has_perm("activity.change_activity")
            or self.get_queryset().filter(owner=self.request.user).exists()
            or self.get_queryset().filter(assigned_to=self.request.user).exists()
        )

        if show_actions:
            actions.extend(
                [
                    {
                        "action": "Edit",
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_activity_edit_url}?new=true" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ]
            )

            if self.request.user.has_perm("activity.delete_activity"):
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


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
class AcivityKanbanView(LoginRequiredMixin, HorillaKanbanView):
    """
    Acivity Kanban view
    """

    model = Activity
    view_id = "activity-kanban"
    filterset_class = ActivityFilter
    search_url = reverse_lazy("activity:activity_list_view")
    main_url = reverse_lazy("activity:activity_view")
    group_by_field = "status"

    @cached_property
    def actions(self):
        """
        Return actions if user is superuser, has global perms, or owns any lead in the queryset.
        Actions are shown globally (for all rows) but backend views enforce ownership/perms.
        """
        instance = self.model()
        actions = []

        show_actions = (
            self.request.user.is_superuser
            or self.request.user.has_perm("activity.change_activity")
            or self.get_queryset().filter(owner=self.request.user).exists()
            or self.get_queryset().filter(assigned_to=self.request.user).exists()
        )

        if show_actions:
            actions.extend(
                [
                    {
                        "action": "Edit",
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_activity_edit_url}?new=true" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ]
            )

            if self.request.user.has_perm("activity.delete_activity"):
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

    @cached_property
    def columns(self):
        instance = self.model()
        return [
            (instance._meta.get_field("subject").verbose_name, "subject"),
            (instance._meta.get_field("activity_type").verbose_name, "activity_type"),
            (instance._meta.get_field("source").verbose_name, "source"),
            (_("Related To"), "related_object"),
        ]


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
class ActivityDetailView(RecentlyViewedMixin, LoginRequiredMixin, HorillaDetailView):

    model = Activity
    pipeline_field = "status"
    tab_url = reverse_lazy("activity:activity_detail_view_tabs")

    breadcrumbs = [
        (_("Schedule"), "activity:activity_view"),
        (_("Activities"), "activity:activity_view"),
    ]
    body = [
        "subject",
        "activity_type",
        "source",
        (_("Related To"), "related_object"),
        "status",
        "owner",
        "assigned_to",
    ]

    excluded_fields = [
        "id",
        "created_at",
        "updated_at",
        "additional_info",
        "history",
        "is_active",
    ]

    @cached_property
    def actions(self):
        """
        Return actions if user is superuser, has global perms, or owns any lead in the queryset.
        Actions are shown globally (for all rows) but backend views enforce ownership/perms.
        """
        instance = self.model()
        actions = []

        show_actions = (
            self.request.user.is_superuser
            or self.request.user.has_perm("activity.change_activity")
            or self.get_queryset().filter(owner=self.request.user).exists()
            or self.get_queryset().filter(assigned_to=self.request.user).exists()
        )

        if show_actions:
            actions.extend(
                [
                    {
                        "action": "Edit",
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_activity_edit_url}?new=true" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ]
            )

            if self.request.user.has_perm("activity.delete_activity"):
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


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
@method_decorator(htmx_required, name="dispatch")
class ActivityDetailTab(LoginRequiredMixin, HorillaDetailSectionView):

    model = Activity
    # edit_field = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()

        if obj.activity_type == "meeting":
            self.include_fields = [
                "activity_type",
                "subject",
                "source",
                "status",
                "title",
                "start_datetime",
                "end_datetime",
                "location",
                "is_all_day",
                "assigned_to",
                "participants",
                "meeting_host",
                "description",
                "assigned_to",
            ]
        elif obj.activity_type == "event":
            self.include_fields = [
                "activity_type",
                "subject",
                "source",
                "status",
                "title",
                "start_datetime",
                "end_datetime",
                "location",
                "is_all_day",
                "assigned_to",
                "participants",
                "description",
                "assigned_to",
            ]

        elif obj.activity_type == "task":
            self.include_fields = [
                "activity_type",
                "subject",
                "source",
                "status",
                "owner",
                "task_priority",
                "due_datetime",
                "description",
                "assigned_to",
            ]

        elif obj.activity_type == "log_call":
            self.include_fields = [
                "activity_type",
                "subject",
                "source",
                "status",
                "call_duration_display",
                "call_duration_seconds",
                "call_type",
                "call_purpose",
                "notes",
                "description",
                "assigned_to",
            ]

        context["body"] = self.body or self.get_default_body()
        return context


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
class ActivityDetailViewTabView(LoginRequiredMixin, HorillaDetailTabView):

    def __init__(self, **kwargs):
        request = getattr(_thread_local, "request", None)
        self.request = request
        self.object_id = self.request.GET.get("object_id")
        self.urls = {
            "details": "activity:activity_details_tab",
            "history": "activity:activity_history_tab_view",
        }

        super().__init__(**kwargs)


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
class ActivityHistoryTabView(LoginRequiredMixin, HorillaHistorySectionView):
    """
    History Tab View
    """

    model = Activity


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
class TaskListView(LoginRequiredMixin, HorillaListView):
    model = Activity
    clear_session_button_enabled = False
    bulk_select_option = False
    paginate_by = 5
    table_class = False
    table_width = False
    table_height_as_class = "h-[260px]"
    list_column_visibility = False

    columns = [
        ("Title", "title"),
        ("Due Date", "due_datetime"),
        ("Priority", "task_priority"),
        ("Status", "get_status_display"),
    ]

    def get_search_url(self):
        return reverse_lazy(
            "activity:task_list", kwargs={"object_id": self.kwargs["object_id"]}
        )

    def get_main_url(self):
        return reverse_lazy(
            "activity:task_list", kwargs={"object_id": self.kwargs["object_id"]}
        )

    @property
    def search_url(self):
        return self.get_search_url()

    @property
    def main_url(self):
        return self.get_main_url()

    @cached_property
    def actions(self):
        """
        Return actions if user is superuser, has global perms, or owns any lead in the queryset.
        Actions are shown globally (for all rows) but backend views enforce ownership/perms.
        """
        instance = self.model()
        actions = []

        show_actions = (
            self.request.user.is_superuser
            or self.request.user.has_perm("activity.change_activity")
            or self.get_queryset().filter(owner=self.request.user).exists()
        )

        if show_actions:
            actions.extend(
                [
                    {
                        "action": "Edit",
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_edit_url}?new=true" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ]
            )

            if self.request.user.has_perm("activity.delete_activity"):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        object_id = self.kwargs.get("object_id")
        view_type = self.request.GET.get("view_type", "pending")
        content_type_id = self.request.GET.get("content_type_id")

        if object_id and content_type_id:
            try:
                content_type = ContentType.objects.get(id=content_type_id)
                queryset = queryset.filter(
                    object_id=object_id, content_type=content_type, activity_type="task"
                )
            except ContentType.DoesNotExist:
                queryset = queryset.none()
        else:
            queryset = queryset.none()

        if view_type == "pending":
            queryset = queryset.filter(status="pending")
            self.view_id = "ActivityTaskListPending"
        elif view_type == "completed":
            queryset = queryset.filter(status="completed")
            self.view_id = "ActivityTaskListCompleted"

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_id"] = self.kwargs.get("object_id")
        context["view_type"] = self.request.GET.get("view_type", "pending")
        return context


@method_decorator(
    permission_required_or_denied("activity.delete_activity"), name="dispatch"
)
class ActivityDeleteView(HorillaSingleDeleteView):
    model = Activity

    def get_post_delete_response(self):
        activity_type = self.object.activity_type
        if "calendar" in self.request.META.get("HTTP_REFERER", ""):
            # For calendar deletions, return a simple success response
            return HttpResponse(
                "<script>$('#reloadMainContent').click();$('#reloadButton').click();</script>"
            )
        if activity_type == "task":
            return HttpResponse(
                "<script>$('#TaskTab').click();closeDeleteModeModal();$('#reloadButton').click();</script>"
            )
        elif activity_type == "meeting":
            return HttpResponse(
                "<script>$'#MeetingsTab').click();closeDeleteModeModal();$('#reloadButton').click();;</script>"
            )
        elif activity_type == "event":
            return HttpResponse(
                "<script>$('#EventTab').click();closeDeleteModeModal();$('#reloadButton').click();</script>"
            )
        elif activity_type == "log_call":
            return HttpResponse(
                "<script>$('#CallsTab).click();closeDeleteModeModal();$('#reloadButton').click();</script>"
            )
        else:
            return HttpResponse("<script>$('#reloadButton').click();</script>")


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
class MeetingListView(HorillaListView):
    model = Activity
    paginate_by = 10
    clear_session_button_enabled = False
    bulk_select_option = False
    table_class = False
    table_width = False
    table_height_as_class = "h-[260px]"
    list_column_visibility = False

    columns = [
        ("Title", "title"),
        # ("Assigned To", "assigned_to"),
        ("Start Date", "get_start_date"),
        ("End Date", "get_end_date"),
        ("Status", "status"),
    ]

    def get_search_url(self):
        return reverse_lazy(
            "activity:meeting_list", kwargs={"object_id": self.kwargs["object_id"]}
        )

    def get_main_url(self):
        return reverse_lazy(
            "activity:meeting_list", kwargs={"object_id": self.kwargs["object_id"]}
        )

    @property
    def search_url(self):
        return self.get_search_url()

    @property
    def main_url(self):
        return self.get_main_url()

    @cached_property
    def actions(self):
        """
        Return actions if user is superuser, has global perms, or owns any lead in the queryset.
        Actions are shown globally (for all rows) but backend views enforce ownership/perms.
        """
        instance = self.model()
        actions = []

        show_actions = (
            self.request.user.is_superuser
            or self.request.user.has_perm("activity.change_activity")
            or self.get_queryset().filter(owner=self.request.user).exists()
        )

        if show_actions:
            actions.extend(
                [
                    {
                        "action": "Edit",
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_edit_url}?new=true" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ]
            )

            if self.request.user.has_perm("activity.delete_activity"):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        object_id = self.kwargs.get("object_id")
        view_type = self.request.GET.get("view_type", "pending")

        content_type_id = self.request.GET.get("content_type_id")

        if object_id and content_type_id:
            try:
                content_type = ContentType.objects.get(id=content_type_id)
                queryset = queryset.filter(
                    object_id=object_id,
                    content_type=content_type,
                    activity_type="meeting",
                )
            except ContentType.DoesNotExist:
                queryset = queryset.none()
        else:
            queryset = queryset.none()

        if view_type == "pending":
            queryset = queryset.filter(status="pending")
            self.view_id = "ActivityMeetingListPending"
        elif view_type == "completed":
            queryset = queryset.filter(status="completed")
            self.view_id = "ActivityMeetingListCompleted"

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_id"] = self.kwargs.get("object_id")
        context["view_type"] = self.request.GET.get("view_type", "pending")
        return context


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
class CallListView(HorillaListView):
    model = Activity
    paginate_by = 10
    clear_session_button_enabled = False
    bulk_select_option = False
    table_class = False
    table_height_as_class = "h-[260px]"
    table_width = False
    list_column_visibility = False

    columns = [
        ("Purpose", "call_purpose"),
        ("Type", "call_type"),
        ("Duration", "call_duration_display"),
        ("Status", "status"),
    ]

    def get_search_url(self):
        return reverse_lazy(
            "activity:call_list", kwargs={"object_id": self.kwargs["object_id"]}
        )

    @property
    def search_url(self):
        return self.get_search_url()

    def get_main_url(self):
        return reverse_lazy(
            "activity:call_list", kwargs={"object_id": self.kwargs["object_id"]}
        )

    @property
    def main_url(self):
        return self.get_main_url()

    @cached_property
    def actions(self):
        """
        Return actions if user is superuser, has global perms, or owns any lead in the queryset.
        Actions are shown globally (for all rows) but backend views enforce ownership/perms.
        """
        instance = self.model()
        actions = []

        show_actions = (
            self.request.user.is_superuser
            or self.request.user.has_perm("activity.change_activity")
            or self.get_queryset().filter(owner=self.request.user).exists()
        )

        if show_actions:
            actions.extend(
                [
                    {
                        "action": "Edit",
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_edit_url}?new=true" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ]
            )

            if self.request.user.has_perm("activity.delete_activity"):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        object_id = self.kwargs.get("object_id")
        view_type = self.request.GET.get("view_type", "pending")

        content_type_id = self.request.GET.get("content_type_id")

        if object_id and content_type_id:
            try:
                content_type = ContentType.objects.get(id=content_type_id)
                queryset = queryset.filter(
                    object_id=object_id,
                    content_type=content_type,
                    activity_type="log_call",
                )
            except ContentType.DoesNotExist:
                queryset = queryset.none()
        else:
            queryset = queryset.none()

        if view_type == "pending":
            queryset = queryset.filter(status="pending")
            self.view_id = "ActivityCallListPending"
        elif view_type == "completed":
            queryset = queryset.filter(status="completed")
            self.view_id = "ActivityCallListCompleted"

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_id"] = self.kwargs.get("object_id")
        context["view_type"] = self.request.GET.get("view_type", "pending")
        return context


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
class EmailListView(HorillaListView):
    model = HorillaMail
    clear_session_button_enabled = False
    bulk_select_option = False
    paginate_by = 10
    table_class = False
    table_width = False
    table_height_as_class = "h-[260px]"
    list_column_visibility = False

    columns = [
        ("Subject", "render_subject"),
        ("Send To", "to"),
        ("Sent At", "sent_at"),
        ("Status", "get_mail_status_display"),
    ]

    def get_search_url(self):
        return reverse_lazy(
            "activity:email_list", kwargs={"object_id": self.kwargs["object_id"]}
        )

    @property
    def search_url(self):
        return self.get_search_url()

    def get_search_url(self):
        return reverse_lazy(
            "activity:email_list", kwargs={"object_id": self.kwargs["object_id"]}
        )

    @property
    def search_url(self):
        return self.get_search_url()

    action_col = {
        "draft": [
            {
                "action": "Send Email",
                "src": "assets/icons/email_black.svg",
                "img_class": "w-4 h-4",
                "attrs": """
                            hx-get="{get_edit_url}" 
                            hx-target="#horillaModalBox"
                            hx-swap="innerHTML" 
                            onclick="openhorillaModal()"
                            """,
            },
            {
                "action": "Delete",
                "src": "assets/icons/a4.svg",
                "img_class": "w-4 h-4",
                "attrs": """
                        hx-post="{get_delete_url}" 
                        hx-target="#modalBox"
                        hx-swap="innerHTML" 
                        hx-trigger="click"
                        hx-vals='{{"check_dependencies": "false"}}'
                        onclick="openModal()"
                    """,
            },
        ],
        "schedule": [{}],
        "sent": [
            {
                "action": "View Email",
                "src": "assets/icons/eye1.svg",
                "img_class": "w-4 h-4",
                "attrs": """
                            hx-get="{get_view_url}" 
                            hx-target="#contentModalBox"
                            hx-swap="innerHTML" 
                            onclick="openContentModal()"
                            """,
            },
        ],
    }

    @cached_property
    def actions(self):
        view_type = self.request.GET.get("view_type")
        action = self.action_col.get(view_type)
        return action

    def get_queryset(self):
        queryset = super().get_queryset()
        object_id = self.kwargs.get("object_id")
        view_type = self.request.GET.get("view_type", "sent")

        content_type_id = self.request.GET.get("content_type_id")

        if object_id and content_type_id:
            try:
                content_type = ContentType.objects.get(id=content_type_id)
                queryset = queryset.filter(
                    object_id=object_id, content_type=content_type
                )
            except ContentType.DoesNotExist:
                queryset = queryset.none()
        else:
            queryset = queryset.none()

        if view_type == "sent":
            queryset = queryset.filter(mail_status="sent")
            self.view_id = "ActivityEmailListSent"
        elif view_type == "draft":
            queryset = queryset.filter(mail_status="draft")
            self.view_id = "ActivityEmailListDraft"
        elif view_type == "scheduled":
            queryset = queryset.filter(mail_status="scheduled")
            self.view_id = "ActivityEmailListScheduled"

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_id"] = self.kwargs.get("object_id")
        context["view_type"] = self.request.GET.get("view_type", "sent")
        return context


@method_decorator(
    permission_required_or_denied(
        ["activity.view_activity", "activity.view_own_activity"]
    ),
    name="dispatch",
)
class EventListView(HorillaListView):
    model = Activity
    clear_session_button_enabled = False
    bulk_select_option = False
    paginate_by = 10
    table_class = False
    table_width = False
    table_height_as_class = "h-[260px]"
    list_column_visibility = False

    columns = [
        ("Title", "title"),
        ("Start Date", "get_start_date"),
        ("End Date", "get_end_date"),
        ("Location", "location"),
        # ("All day Event","is_all_day"),
        ("Status", "get_status_display"),
    ]

    def get_search_url(self):
        return reverse_lazy(
            "activity:event_list", kwargs={"object_id": self.kwargs["object_id"]}
        )

    @property
    def search_url(self):
        return self.get_search_url()

    @cached_property
    def actions(self):
        """
        Return actions if user is superuser, has global perms, or owns any lead in the queryset.
        Actions are shown globally (for all rows) but backend views enforce ownership/perms.
        """
        instance = self.model()
        actions = []

        show_actions = (
            self.request.user.is_superuser
            or self.request.user.has_perm("activity.change_activity")
            or self.get_queryset().filter(owner=self.request.user).exists()
        )

        if show_actions:
            actions.extend(
                [
                    {
                        "action": "Edit",
                        "src": "assets/icons/edit.svg",
                        "img_class": "w-4 h-4",
                        "attrs": """
                            hx-get="{get_edit_url}?new=true" 
                            hx-target="#modalBox"
                            hx-swap="innerHTML" 
                            onclick="openModal()"
                            """,
                    },
                ]
            )

            if self.request.user.has_perm("activity.delete_activity"):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        object_id = self.kwargs.get("object_id")
        view_type = self.request.GET.get("view_type", "pending")

        content_type_id = self.request.GET.get("content_type_id")

        if object_id and content_type_id:
            try:
                content_type = ContentType.objects.get(id=content_type_id)
                queryset = queryset.filter(
                    object_id=object_id,
                    content_type=content_type,
                    activity_type="event",
                )
            except ContentType.DoesNotExist:
                queryset = queryset.none()
        else:
            queryset = queryset.none()

        if view_type == "pending":
            queryset = queryset.filter(status="pending")
            self.view_id = "ActivityEventListPending"
        elif view_type == "completed":
            queryset = queryset.filter(status="completed")
            self.view_id = "ActivityEventListCompleted"

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_id"] = self.kwargs.get("object_id")
        context["view_type"] = self.request.GET.get("view_type", "pending")
        return context


@method_decorator(htmx_required, name="dispatch")
class TaskCreateForm(LoginRequiredMixin, HorillaSingleFormView):
    """
    Form view for task activity
    """

    model = Activity
    full_width_fields = ["description"]
    modal_height = False
    hidden_fields = ["object_id", "content_type", "activity_type"]
    fields = [
        "object_id",
        "content_type",
        "title",
        "subject",
        "owner",
        "task_priority",
        "assigned_to",
        "due_datetime",
        "status",
        "description",
        "activity_type",
    ]

    @cached_property
    def form_url(self):
        pk = self.kwargs.get("pk") or self.request.GET.get("id")
        if pk:
            return reverse_lazy("activity:task_update_form", kwargs={"pk": pk})
        return reverse_lazy("activity:task_create_form")

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        object_id = request.GET.get("object_id")
        model_name = request.GET.get("model_name")
        app_label = request.GET.get("app_label")

        if pk:
            try:
                activity = get_object_or_404(Activity, pk=pk)
            except Http404:
                messages.error(
                    request,
                    f"{self.model._meta.verbose_name.title()} not found or no longer exists.",
                )
                return HttpResponse(
                    "<script>$('#reloadButton').click();closeModal();</script>"
                )
            object_id = object_id or activity.object_id
            model_name = model_name or activity.content_type.model
            app_label = app_label or activity.content_type.app_label

        if object_id and model_name:
            try:
                model_class = apps.get_model(app_label=app_label, model_name=model_name)

                try:
                    instance = get_object_or_404(model_class, pk=object_id)
                except Http404:
                    messages.error(
                        request,
                        f"{self.model._meta.verbose_name.title()} not found or no longer exists.",
                    )
                    return HttpResponse(
                        "<script>$('#reloadButton').click();closeModal();</script>"
                    )

                owner_fields = getattr(model_class, "OWNER_FIELDS", ["owner"])
                user_is_owner = False

                for field in owner_fields:
                    if hasattr(instance, field):
                        value = getattr(instance, field)

                        if isinstance(value, models.Model):
                            if value.id == request.user.id:
                                user_is_owner = True
                                break
                        elif hasattr(value, "all"):
                            if request.user in value.all():
                                user_is_owner = True
                                break

                if not user_is_owner and not request.user.has_perm(
                    "activity.add_activity"
                ):
                    return render(request, "403.html")

                return super().get(request, *args, **kwargs)

            except LookupError:
                return render(request, "403.html")
        if pk:
            if not self.model.objects.filter(
                owner_id=self.request.user, pk=pk
            ).first() and not self.request.user.has_perm("activity.change_activity"):
                return super().get(request, *args, **kwargs)
        return render(request, "403.html")

    def get_initial(self):
        initial = super().get_initial()
        object_id = self.request.GET.get("object_id")
        model_name = self.request.GET.get("model_name")
        if object_id and model_name:
            initial["object_id"] = object_id
            content_type = ContentType.objects.get(model=model_name.lower())
            initial["content_type"] = content_type.id
            initial["owner"] = self.request.user
            initial["activity_type"] = "task"
        return initial

    def form_valid(self, form):
        """
        Handle form submission and save the task.
        """
        super().form_valid(form)
        return HttpResponse(
            "<script>htmx.trigger('#reloadButton','click');closeModal();</script>"
        )


@method_decorator(htmx_required, name="dispatch")
class MeetingsCreateForm(LoginRequiredMixin, HorillaSingleFormView):
    """
    Form view for meeting activity
    """

    model = Activity
    form_class = MeetingsForm
    fields = [
        "object_id",
        "content_type",
        "title",
        "subject",
        "start_datetime",
        "end_datetime",
        "status",
        "owner",
        "participants",
        "meeting_host",
        "is_all_day",
        "activity_type",
    ]
    modal_height = False

    @cached_property
    def form_url(self):
        pk = self.kwargs.get("pk") or self.request.GET.get("id")
        if pk:
            return reverse_lazy("activity:meeting_update_form", kwargs={"pk": pk})
        return reverse_lazy("activity:meeting_create_form")

    def get_initial(self):
        initial = super().get_initial()
        if self.request.method == "POST":
            initial["is_all_day"] = self.request.POST.get("is_all_day") == "on"
        else:
            object_id = self.request.GET.get("object_id")
            model_name = self.request.GET.get("model_name")
            all_day = self.request.GET.get("is_all_day")
            toggle_is_all_day = self.request.GET.get("toggle_is_all_day")

            # If toggle_is_all_day is present and we're in edit mode, force is_all_day to False
            if toggle_is_all_day == "true" and self.kwargs.get("pk"):
                initial["is_all_day"] = False

            elif all_day is not None:
                all_days = True if all_day == "on" else False
                initial["is_all_day"] = all_days

            elif hasattr(self, "object") and self.object:
                initial["is_all_day"] = self.object.is_all_day

            if object_id and model_name:
                initial["object_id"] = object_id
                content_type = ContentType.objects.get(model=model_name.lower())
                initial["content_type"] = content_type.id
                initial["activity_type"] = "meeting"
                initial["owner"] = self.request.user

            return initial

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        object_id = request.GET.get("object_id")
        model_name = request.GET.get("model_name")
        app_label = request.GET.get("app_label")

        if pk:
            try:
                activity = get_object_or_404(Activity, pk=pk)
            except Http404:
                messages.error(
                    request,
                    f"{self.model._meta.verbose_name.title()} not found or no longer exists.",
                )
                return HttpResponse(
                    "<script>$('#reloadButton').click();closeModal();</script>"
                )
            object_id = object_id or activity.object_id
            model_name = model_name or activity.content_type.model
            app_label = app_label or activity.content_type.app_label

        if object_id and model_name:
            try:
                model_class = apps.get_model(app_label=app_label, model_name=model_name)
                try:
                    instance = get_object_or_404(model_class, pk=object_id)
                except Http404:
                    messages.error(
                        request,
                        f"{self.model._meta.verbose_name.title()} not found or no longer exists.",
                    )
                    return HttpResponse(
                        "<script>$('#reloadButton').click();closeModal();</script>"
                    )

                owner_fields = getattr(model_class, "OWNER_FIELDS", ["owner"])
                user_is_owner = False

                for field in owner_fields:
                    if hasattr(instance, field):
                        value = getattr(instance, field)

                        if isinstance(value, models.Model):
                            if value.id == request.user.id:
                                user_is_owner = True
                                break
                        elif hasattr(value, "all"):
                            if request.user in value.all():
                                user_is_owner = True
                                break

                if not user_is_owner and not request.user.has_perm(
                    "activity.add_activity"
                ):
                    return render(request, "403.html")

                return super().get(request, *args, **kwargs)

            except LookupError:
                return render(request, "403.html")
        if pk:
            if not self.model.objects.filter(
                owner_id=self.request.user, pk=pk
            ).first() and not self.request.user.has_perm("activity.change_activity"):
                return super().get(request, *args, **kwargs)
        return render(request, "403.html")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST":
            return kwargs

        initial = self.get_initial()
        get_data = self.request.GET.dict()
        for key, value in get_data.items():
            if value:
                initial[key] = value
        kwargs["initial"] = initial
        return kwargs

    def form_valid(self, form):
        """
        Handle form submission and save the meeting.
        """
        super().form_valid(form)
        return HttpResponse(
            "<script>htmx.trigger('#MeetingsTab','click');closeModal();</script>"
        )


@method_decorator(htmx_required, name="dispatch")
class CallCreateForm(LoginRequiredMixin, HorillaSingleFormView):
    """
    Form view for call activity
    """

    model = Activity
    form_class = LogCallForm
    modal_height = False
    full_width_fields = ["notes"]

    fields = [
        "object_id",
        "content_type",
        "subject",
        "owner",
        "call_purpose",
        "call_type",
        "call_duration_display",
        "status",
        "notes",
        "activity_type",
    ]

    @cached_property
    def form_url(self):
        pk = self.kwargs.get("pk") or self.request.GET.get("id")
        if pk:
            return reverse_lazy("activity:call_update_form", kwargs={"pk": pk})
        return reverse_lazy("activity:call_create_form")

    def get_initial(self):
        initial = super().get_initial()
        object_id = self.request.GET.get("object_id")
        model_name = self.request.GET.get("model_name")
        pk = self.kwargs.get("pk") or self.request.GET.get("id")
        if not pk:
            initial["call_duration_display"] = (
                "00:00:00"  # Default duration for creation
            )

        if object_id and model_name:
            initial["object_id"] = object_id
            content_type = ContentType.objects.get(model=model_name.lower())
            initial["content_type"] = content_type.id
            initial["activity_type"] = "log_call"
            initial["owner"] = self.request.user

        return initial

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        object_id = request.GET.get("object_id")
        model_name = request.GET.get("model_name")
        app_label = request.GET.get("app_label")

        if pk:
            try:
                activity = get_object_or_404(Activity, pk=pk)
            except Http404:
                messages.error(
                    request,
                    f"{self.model._meta.verbose_name.title()} not found or no longer exists.",
                )
                return HttpResponse(
                    "<script>$('#reloadButton').click();closeModal();</script>"
                )
            object_id = object_id or activity.object_id
            model_name = model_name or activity.content_type.model
            app_label = app_label or activity.content_type.app_label

        if object_id and model_name:
            try:
                model_class = apps.get_model(app_label=app_label, model_name=model_name)
                try:
                    instance = get_object_or_404(model_class, pk=object_id)
                except Http404:
                    messages.error(
                        request,
                        f"{self.model._meta.verbose_name.title()} not found or no longer exists.",
                    )
                    return HttpResponse(
                        "<script>$('#reloadButton').click();closeModal();</script>"
                    )

                owner_fields = getattr(model_class, "OWNER_FIELDS", ["owner"])
                user_is_owner = False

                for field in owner_fields:
                    if hasattr(instance, field):
                        value = getattr(instance, field)

                        if isinstance(value, models.Model):
                            if value.id == request.user.id:
                                user_is_owner = True
                                break
                        elif hasattr(value, "all"):
                            if request.user in value.all():
                                user_is_owner = True
                                break

                if not user_is_owner and not request.user.has_perm(
                    "activity.add_activity"
                ):
                    return render(request, "403.html")

                return super().get(request, *args, **kwargs)

            except LookupError:
                return render(request, "403.html")
        if pk:
            if not self.model.objects.filter(
                owner_id=self.request.user, pk=pk
            ).first() and not self.request.user.has_perm("activity.change_activity"):
                return super().get(request, *args, **kwargs)
        return render(request, "403.html")

    def form_valid(self, form):
        """
        Handle form submission and save the meeting.
        """
        super().form_valid(form)
        return HttpResponse(
            "<script>htmx.trigger('#CallsTab','click');closeModal();</script>"
        )


@method_decorator(htmx_required, name="dispatch")
class EventCreateForm(LoginRequiredMixin, HorillaSingleFormView):
    """
    Form view for event activity
    """

    model = Activity
    form_class = EventForm
    modal_height = False
    full_width_fields = ["notes"]

    fields = [
        "object_id",
        "content_type",
        "title",
        "subject",
        "owner",
        "start_datetime",
        "end_datetime",
        "location",
        "assigned_to",
        "status",
        "is_all_day",
        "activity_type",
    ]

    @cached_property
    def form_url(self):
        pk = self.kwargs.get("pk") or self.request.GET.get("id")
        if pk:
            return reverse_lazy("activity:event_update_form", kwargs={"pk": pk})
        return reverse_lazy("activity:event_create_form")

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        object_id = request.GET.get("object_id")
        model_name = request.GET.get("model_name")
        app_label = request.GET.get("app_label")

        if pk:
            try:
                activity = get_object_or_404(Activity, pk=pk)
            except Http404:
                messages.error(
                    request,
                    f"{self.model._meta.verbose_name.title()} not found or no longer exists.",
                )
                return HttpResponse(
                    "<script>$('#reloadButton').click();closeModal();</script>"
                )
            object_id = object_id or activity.object_id
            model_name = model_name or activity.content_type.model
            app_label = app_label or activity.content_type.app_label

        if object_id and model_name:
            try:
                model_class = apps.get_model(app_label=app_label, model_name=model_name)

                try:
                    instance = get_object_or_404(model_class, pk=object_id)
                except Http404:
                    messages.error(
                        request,
                        f"{self.model._meta.verbose_name.title()} not found or no longer exists.",
                    )
                    return HttpResponse(
                        "<script>$('#reloadButton').click();closeModal();</script>"
                    )

                owner_fields = getattr(model_class, "OWNER_FIELDS", ["owner"])
                user_is_owner = False

                for field in owner_fields:
                    if hasattr(instance, field):
                        value = getattr(instance, field)

                        if isinstance(value, models.Model):
                            if value.id == request.user.id:
                                user_is_owner = True
                                break
                        elif hasattr(value, "all"):
                            if request.user in value.all():
                                user_is_owner = True
                                break

                if not user_is_owner and not request.user.has_perm(
                    "activity.add_activity"
                ):
                    return render(request, "403.html")

                return super().get(request, *args, **kwargs)

            except LookupError:
                return render(request, "403.html")
        if pk:
            if not self.model.objects.filter(
                owner_id=self.request.user, pk=pk
            ).first() and not self.request.user.has_perm("activity.change_activity"):
                return super().get(request, *args, **kwargs)
        return render(request, "403.html")

    def get_initial(self):
        initial = super().get_initial()
        if self.request.method == "POST":
            initial["is_all_day"] = self.request.POST.get("is_all_day") == "on"
        else:
            object_id = self.request.GET.get("object_id")
            model_name = self.request.GET.get("model_name")
            all_day = self.request.GET.get("is_all_day")
            toggle_is_all_day = self.request.GET.get("toggle_is_all_day")

            # If toggle_is_all_day is present and we're in edit mode, force is_all_day to False
            if toggle_is_all_day == "true" and self.kwargs.get("pk"):
                initial["is_all_day"] = False

            # If we have GET parameter for is_all_day, use it
            elif all_day is not None:
                all_days = True if all_day == "on" else False
                initial["is_all_day"] = all_days

            # If we're editing an existing event and no GET parameter, use the model value
            elif hasattr(self, "object") and self.object:
                initial["is_all_day"] = self.object.is_all_day

            if object_id and model_name:
                initial["object_id"] = object_id
                content_type = ContentType.objects.get(model=model_name.lower())
                initial["content_type"] = content_type.id
                initial["activity_type"] = "event"
                initial["owner"] = self.request.user

            return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST":
            return kwargs

        initial = self.get_initial()
        get_data = self.request.GET.dict()
        for key, value in get_data.items():
            if value:
                initial[key] = value
        kwargs["initial"] = initial
        return kwargs

    def form_valid(self, form):
        """
        Handle form submission and save the meeting.
        """

        super().form_valid(form)
        return HttpResponse(
            "<script>htmx.trigger('#EventTab','click');closeModal();</script>"
        )

    def form_invalid(self, form):

        # Render the form with errors for HTMX to update the UI
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(htmx_required, name="dispatch")
class ActivityCreateView(LoginRequiredMixin, HorillaSingleFormView):
    model = Activity
    form_class = ActivityCreateForm
    success_url = reverse_lazy("activity:activity_list")
    form_title = "Create Activity"
    view_id = "activity-form-view"
    full_width_fields = ["description", "notes"]

    ACTIVITY_FIELD_MAP = {
        "event": [
            "activity_type",
            "subject",
            "source",
            "content_type",
            "object_id",
            "owner",
            "status",
            "title",
            "start_datetime",
            "end_datetime",
            "location",
            "is_all_day",
            "assigned_to",
            "participants",
            "description",
        ],
        "meeting": [
            "activity_type",
            "subject",
            "source",
            "content_type",
            "object_id",
            "owner",
            "status",
            "title",
            "start_datetime",
            "end_datetime",
            "location",
            "is_all_day",
            "assigned_to",
            "participants",
            "meeting_host",
            "description",
        ],
        "task": [
            "activity_type",
            "subject",
            "source",
            "content_type",
            "object_id",
            "status",
            "owner",
            "task_priority",
            "due_datetime",
            "description",
        ],
        "email": [
            "activity_type",
            "subject",
            "source",
            "content_type",
            "object_id",
            "status",
            "sender",
            "to_email",
            "email_subject",
            "body",
            "bcc",
            "sent_at",
            "scheduled_at",
            "is_sent",
            "description",
        ],
        "log_call": [
            "activity_type",
            "subject",
            "source",
            "content_type",
            "object_id",
            "owner",
            "status",
            "call_duration_display",
            "call_duration_seconds",
            "call_type",
            "call_purpose",
            "notes",
            "description",
        ],
    }

    def get_initial(self):
        initial = super().get_initial()

        is_create = not (self.kwargs.get("pk") or self.object)

        if self.request.method == "POST":
            initial["is_all_day"] = self.request.POST.get("is_all_day") == "on"
        else:
            object_id = self.request.GET.get("object_id")
            model_name = self.request.GET.get("model_name")
            all_day = self.request.GET.get("is_all_day")
            toggle_is_all_day = self.request.GET.get("toggle_is_all_day")

            if is_create:
                initial["activity_type"] = "event"
            else:
                initial["activity_type"] = getattr(
                    self.object, "activity_type", None
                ) or initial.get("activity_type", "event")

            if toggle_is_all_day == "true" and self.kwargs.get("pk"):
                initial["is_all_day"] = False
            elif all_day is not None:
                all_days = True if all_day == "on" else False
                initial["is_all_day"] = all_days
            elif hasattr(self, "object") and self.object:
                initial["is_all_day"] = self.object.is_all_day

            if object_id and model_name:
                initial["object_id"] = object_id
                content_type = ContentType.objects.get(model=model_name.lower())
                initial["content_type"] = content_type.id

        return initial

    def get_form_class(self):
        activity_type = (
            self.request.POST.get("activity_type")
            or self.request.GET.get("activity_type")
            or getattr(self, "activity_type", None)
        )
        if not activity_type:
            activity_type = list(self.ACTIVITY_FIELD_MAP.keys())[0]

        selected_fields = self.ACTIVITY_FIELD_MAP.get(
            activity_type, self.ACTIVITY_FIELD_MAP["event"]
        )

        class DynamicActivityForm(ActivityCreateForm):
            class Meta(ActivityCreateForm.Meta):
                model = self.model
                fields = selected_fields
                widgets = (
                    ActivityCreateForm.Meta.widgets.copy()
                    if hasattr(ActivityCreateForm.Meta, "widgets")
                    else {}
                )

        return DynamicActivityForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        activity_type = self.request.POST.get("activity_type") or self.request.GET.get(
            "activity_type"
        )
        if activity_type:
            kwargs["initial"] = kwargs.get("initial", {})
            kwargs["initial"]["activity_type"] = activity_type

        if self.request.method == "GET":
            kwargs["initial"] = kwargs.get("initial", {})
            for field in self.ACTIVITY_FIELD_MAP.get(
                activity_type, self.ACTIVITY_FIELD_MAP["event"]
            ):
                if field in self.request.GET:
                    value = self.request.GET.get(field)
                    if value:
                        if field in ["start_datetime", "end_datetime"] and kwargs[
                            "initial"
                        ].get("is_all_day"):
                            continue
                        kwargs["initial"][field] = value
                elif field in self.request.GET.getlist(field):
                    values = self.request.GET.getlist(field)
                    if values:
                        kwargs["initial"][field] = values
            if "content_type" in self.request.GET:
                kwargs["initial"]["content_type"] = self.request.GET.get("content_type")
            if "object_id" in self.request.GET:
                kwargs["initial"]["object_id"] = self.request.GET.get("object_id")
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_url"] = self.form_url
        context["modal_height"] = True
        context["view_id"] = self.view_id
        return context

    @cached_property
    def form_url(self):
        pk = self.kwargs.get("pk") or self.request.GET.get("id")
        if pk:
            return reverse_lazy("activity:activity_edit_form", kwargs={"pk": pk})
        return reverse_lazy("activity:activity_create_form")

    def get(self, request, *args, **kwargs):

        pk = self.kwargs.get("pk")

        if request.user.has_perm("activity.change_activity") or request.user.has_perm(
            "activity.add_activity"
        ):
            return super().get(request, *args, **kwargs)
        if pk:
            if (
                self.model.objects.filter(owner_id=self.request.user, pk=pk).exists()
                or self.model.objects.filter(
                    assigned_to=self.request.user, pk=pk
                ).exists()
            ):
                return super().get(request, *args, **kwargs)

        return render(self.request, "403.html")

    def form_valid(self, form):
        """
        Handle form submission and save the meeting.
        """

        super().form_valid(form)
        if "calendar-view" in self.request.META.get("HTTP_REFERER"):
            return HttpResponse(
                "<script>$('#reloadMainContent').click();closeModal();</script>"
            )
        return HttpResponse("<script>$('#reloadButton').click();closeModal();</script>")
