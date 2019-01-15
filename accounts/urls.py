from django.conf.urls import url
from . import views

urlpatterns = [
    url('^login/$', views.login, name='login'),
    url('^signup/$', views.UserCreateView.as_view(), name='user-create'),
    url('^mail_verify/(?P<hash_code>\w+)/$', views.MailVerify.as_view(), name='mail-verify'),
    url(r'^password/$', views.change_password, name='change_password'),
    url(r'^update/(?P<pk>\d+)/$', views.UserUpdateView.as_view(), name='user-update'),

    # password forgot
    url('^forgot_password/$', views.ForgotPassword.as_view(), name='forgot-password'),
    url('^forgot_password_update/(?P<id>\w+)/$', views.ForgotUserPasswordUpdateView.as_view())
]