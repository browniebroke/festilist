from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'festlist.views.home', name='home'),
    url(r'^auth/?$', 'festlist.views.authorise', name='authorise'),
    url(r'^create/?$', 'festlist.views.create', name='create'),
    url(r'^generate/?$', 'festlist.views.generate_playlist', name='generate'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
