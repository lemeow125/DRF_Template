

from celery import shared_task
from .models import SearchResult


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 0, 'countdown': 5})
def create_search_result(title, link):
    if SearchResult.objects.filter(title=title, link=link).exists():
        return ("SearchResult entry already exists")
    else:
        SearchResult.objects.create(
            title=title,
            link=link
        )
        return f"Created new SearchResult entry titled: {title}"
