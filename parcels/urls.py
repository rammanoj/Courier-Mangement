from django.conf.urls import url
from . import views

urlpatterns = [
    url('^create/$', views.ParcelCreateView.as_view(), name='parcel-create'),
    url('^update/(?P<pk>\d+)/$', views.ParcelUpdateView.as_view(), name='parcel-update'),
    url('^delete/(?P<pk>\d+)/$', views.ParcelDeleteView.as_view(), name='parcel-delete'),
    url('^$', views.ParcelListView.as_view(), name='parcel-list'),
    url('^(?P<pk>\d+)/$', views.ParcelDetailView.as_view(), name='parcel-detail'),
    url('^confirm/student/$', views.StudentConfirmView.as_view(), name='student-confirm'),
]