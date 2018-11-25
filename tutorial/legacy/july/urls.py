from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', admin.site.urls),
    url(r'^api/v2/graphql$', 'july.views.graph', name='graph'),
    url(r'', 'july.views.frontend', name='frontend'),
)
