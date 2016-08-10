from django.conf.urls.defaults import *
from django.conf import settings
import os
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^', include('grave.web.urls')),
    (r'^api/', include('grave.api.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': '/home/jirka/grave/static'}),


    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        #(r'^site_media/(?P<path>.*)$', 'staticfiles.views.serve'),
        #(r'^media/(?P<path>.*)$', 'staticfiles.views.serve')
    )