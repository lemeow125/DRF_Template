from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import SearchResult
from unfold.contrib.filters.admin import RangeDateFilter


@admin.register(SearchResult)
class SearchResultAdmin(ModelAdmin):
    model = SearchResult
    search_fields = ("id", "title", "link")
    list_display = ["id", "title", "timestamp"]

    list_filter_submit = True
    list_filter = (
        ("timestamp", RangeDateFilter),
        ("timestamp", RangeDateFilter),
    )
