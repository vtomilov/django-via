from django.contrib import admin

# Register your models here.
from .models import Project, Image

admin.site.register(Project)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    search_fields = ['project', 'edited_by']
    list_display = ('filename', 'project', 'edited_by', 'region_count', 'regions_by_user', 'edit_date')
    list_filter = ('edited_by', 'project')

    def region_count(self, instance):
        return len(instance.regions)

    def regions_by_user(self, instance):
        stats = {
            "unknown": 0
        }
        for r in instance.regions:
            if "user_edited" in r:
                if r["user_edited"] not in stats:
                    stats[r["user_edited"]] = 0
                stats[r["user_edited"]] += 1
            else:
                stats["unknown"] += 1
        return stats
