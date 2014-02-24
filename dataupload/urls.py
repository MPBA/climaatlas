from django.conf.urls import patterns, include, url

urlpatterns = patterns('dataupload.views',
    # Examples:
    # url(r'^$', 'climatlas.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'upload')
)
