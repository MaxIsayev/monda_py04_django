from django.contrib import admin
from . import models
from django.utils.translation import gettext as _
# Register your models here.

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'total_tasks', 'undone_tasks', 'recent_tasks', 'recent_undone_tasks', 'owner']
    list_display_links = ['id', 'name']
    list_filter = ['owner']
    search_fields = ['name']
    fieldsets = (
        ( None, {
            "fields": (
                'name', 'owner',
            ),
        }

        ),
    )

    def total_tasks(self, obj: models.Project):
        return obj.tasks.count()
    total_tasks.short_description = _("number of tasks")

    def undone_tasks(self, obj: models.Project):
        return obj.tasks.filter(is_done=False).count()
    undone_tasks.short_description = _('undone tasks')

    def recent_tasks(self, obj: models.Project):
        return "; ".join(obj.tasks.order_by('-created_at').values_list('name', flat=True)[:3])
    recent_tasks.short_description = _('recent tasks')

    def recent_undone_tasks(self, obj: models.Project):
        return "; ".join(obj.tasks.filter(is_done=False).order_by('-created_at').values_list('name', flat=True)[:3])
    recent_undone_tasks.short_description = _('recent undone tasks')

class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_done', 'deadline', 'project', 'owner', 'created_at']
    list_filter = ['is_done', 'project', 'owner', 'deadline', 'created_at']
    search_fields = ['name', 'description', 'project__name', 'owner__last_name', 'owner__username']
    list_editable = ['is_done', 'owner', 'project']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        (_('General'), {
            "fields": (
                ('name', 'deadline', 'is_done'), 'description',
            ),
        }),
        (_('Ownership'), {
            "fields": (
                ('owner', 'project'),
            ),
        }),
        (_('Temporal Tracking'), {
            "fields": (
                ('created_at', 'updated_at', 'id'),
            ),
        }),
    )

admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Task, TaskAdmin)