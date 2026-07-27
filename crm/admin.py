from django.contrib import admin

from .models import Client, Deal, Task


class DealInline(admin.TabularInline):
    model = Deal
    extra = 0
    fields = ('title', 'amount', 'stage', 'expected_close')


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ('title', 'due_date', 'is_done')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company', 'contact_name', 'email', 'owner', 'data_processing_basis', 'created_at')
    list_filter = ('data_processing_basis', 'owner')
    search_fields = ('company', 'contact_name', 'email', 'phone')
    inlines = [DealInline, TaskInline]


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'amount', 'stage', 'owner', 'expected_close')
    list_filter = ('stage', 'owner')
    search_fields = ('title', 'client__company')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'deal', 'due_date', 'is_done', 'owner')
    list_filter = ('is_done', 'owner')
