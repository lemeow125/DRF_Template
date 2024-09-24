from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import SearchResult


@admin.register(SearchResult)
class SearchResultAdmin(ModelAdmin):
    model = SearchResult
    search_fields = ('id', 'title', 'link')
    list_display = ['id', 'title']
