from django.contrib import admin

from base.models import Webpage, WebpageMonitoring, WebpageScreenshot


class WebpageMonitoringInline(admin.TabularInline):
    model = WebpageMonitoring
    extra = 1


@admin.register(Webpage)
class WebpageAdmin(admin.ModelAdmin):
    list_display = ('url', 'minute_count', 'hour_count', 'day_count')
    search_fields = ('url',)
    fields = ('url',)
    inlines = [WebpageMonitoringInline]  # noqa: RUF012

    @admin.display(description='minute Users')
    def minute_count(self, obj: Webpage) -> int:
        return obj.monitorings.filter(interval='minute').count()  # type: ignore[attr-defined]

    @admin.display(description='hour Users')
    def hour_count(self, obj: Webpage) -> int:
        return obj.monitorings.filter(interval='hour').count()  # type: ignore[attr-defined]

    @admin.display(description='day Users')
    def day_count(self, obj: Webpage) -> int:
        return obj.monitorings.filter(interval='day').count()  # type: ignore[attr-defined]


@admin.register(WebpageScreenshot)
class WebpageScreenshotAdmin(admin.ModelAdmin):
    list_display = ('webpage', 'perceptual_hash', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('webpage__url',)
    readonly_fields = ('created_at', 'perceptual_hash')
