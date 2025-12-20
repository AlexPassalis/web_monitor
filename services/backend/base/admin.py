from django.contrib import admin

from base.models import Webpage, WebpageScreenshot


@admin.register(Webpage)
class WebpageAdmin(admin.ModelAdmin):
    list_display = ('url', 'minute_count', 'hour_count', 'day_count')
    search_fields = ('url',)
    filter_horizontal = ('minute', 'hour', 'day')
    fields = ('url', 'minute', 'hour', 'day')

    @admin.display(description='minute Users')
    def minute_count(self, obj: Webpage) -> int:
        return obj.minute.count()

    @admin.display(description='hour Users')
    def hour_count(self, obj: Webpage) -> int:
        return obj.hour.count()

    @admin.display(description='day Users')
    def day_count(self, obj: Webpage) -> int:
        return obj.day.count()


@admin.register(WebpageScreenshot)
class WebpageScreenshotAdmin(admin.ModelAdmin):
    list_display = ('tracked_website', 'perceptual_hash', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('tracked_website__url',)
    readonly_fields = ('created_at', 'perceptual_hash')
