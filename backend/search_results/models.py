from django.db import models


class SearchResult(models.Model):
    title = models.CharField(max_length=1000)
    link = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
