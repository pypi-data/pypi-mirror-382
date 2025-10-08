from django.contrib import admin

from . import models


class MessageInline(admin.TabularInline):
    model = models.Message
    extra = 0


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'created_at',
        'title',
        'support_manager',
        'resolved',
    ]
    inlines = [
        MessageInline,
    ]
