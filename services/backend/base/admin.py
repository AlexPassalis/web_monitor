from django.contrib import admin
from base.models import TrackedWebsite, WebsiteSnapshot


@admin.register(TrackedWebsite)
class TrackedWebsiteAdmin(admin.ModelAdmin):
    list_display = ('url', 'minute_count', 'hour_count', 'day_count')
    search_fields = ('url',)
    filter_horizontal = ('minute', 'hour', 'day')
    fields = ('url', 'minute', 'hour', 'day')

    def minute_count(self, obj):
        return obj.minute.count()

    minute_count.short_description = 'minute Users'

    def hour_count(self, obj):
        return obj.hour.count()

    hour_count.short_description = 'hour Users'

    def day_count(self, obj):
        return obj.day.count()

    day_count.short_description = 'day Users'


@admin.register(WebsiteSnapshot)
class WebsiteSnapshotAdmin(admin.ModelAdmin):
    list_display = ('tracked_website', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tracked_website__url',)
    readonly_fields = ('created_at',)
