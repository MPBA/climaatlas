from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .views import MainView, StazioniClimaticheView, StazioniClimaticheDetailView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'climatlas.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(regex='^$', view=MainView.as_view(), name='home'),
    url(regex='^stazioni/anagrafica/$', view=StazioniClimaticheView.as_view(), name='stazioni_climatiche'),
    url(regex='^stazione/anagrafica/(?P<pk>\d+)/$', view=StazioniClimaticheDetailView.as_view(), name='stazione_detail'),

    ### Import analysis app ###
    (r'^view/', include("analysis.urls")),

    ### Import exhibit app ###
    (r'^exhibit/', include("exhibit.urls")),

    ### Import upload tools app ###
    (r'^upload/', include("dataupload.urls")),

    ### Import WYSIWYG editor ###
    url(r'^redactor/', include('redactor.urls')),

    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += patterns('django.contrib.flatpages.views',
    (r'^(?P<url>.*/)$', 'flatpage'),
)