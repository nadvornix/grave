from django.conf.urls.defaults import *
#from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
#    url(r'^$', 'navody.views.index', name="inzeraty_index"),
#    url(r'^view/(?P<hash>[0-9a-zA-Z]+)-(?P<url_string>[-a-z0-9]*)$', 'navody.views.view'),
#    url(r'^edit/((?P<hash>[0-9a-zA-Z]+)-(?P<url_string>[-a-z]*))?$', 'navody.views.edit'),
    url(r'^(?P<nick>[-0-9a-zA-Z_]+)?(/(?P<format>[a-z]+)?)?$', 'grave.api.views.index'),
)
