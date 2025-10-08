from django.contrib import admin
from .models import Lead,LeadStatus
from auditlog.models import LogEntry

# Register your leads models here.
admin.site.register(Lead)
admin.site.register(LeadStatus)

admin.site.unregister(LogEntry)

# # Then, register with your custom admin class
@admin.register(LogEntry)
class CustomLogEntryAdmin(admin.ModelAdmin):
    list_display = ('object_repr', 'content_type', 'action', 'actor', 'timestamp')
    list_filter = ('content_type', 'action', 'actor', 'timestamp')
    search_fields = ('object_repr', 'changes', 'actor__username')