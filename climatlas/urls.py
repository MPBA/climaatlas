from django.conf.urls import patterns, include, url
from django.contrib import admin
from .views import MainView, StazioniClimaticheView, StazioniClimaticheDetailView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'climatlas.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(regex='^$', view=MainView.as_view(), name='home'),
    url(regex='^stazioni/anagrafica/$', view=StazioniClimaticheView.as_view(), name='stazioni_climatiche'),
    url(regex='^stazione/anagrafica/(?P<pk>\d+)/$', view=StazioniClimaticheDetailView.as_view(), name='stazione_detail'),
    url(r'^admin/', include(admin.site.urls)),
)