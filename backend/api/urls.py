from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from config.settings import DEBUG, CLOUD, MEDIA_ROOT
urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('notifications/', include('notifications.urls')),
    path('billing/', include('billing.urls')),
    path('stripe/', include('payments.urls'))
]

# URLs for local development
if DEBUG and not CLOUD:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        'media/', document_root=MEDIA_ROOT)
