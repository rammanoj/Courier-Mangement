import random
from _sha256 import sha256
import datetime
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import UpdateView, TemplateView
from accounts import models, mails
from . import forms
from django.views import generic
from django.contrib.auth import views as authview


class UserCreateView(SuccessMessageMixin, generic.CreateView):
    form_class = forms.Register
    template_name = 'accounts/signup.html'
    success_url = '/accounts/signup/'
    success_message = "Check the Verification Mail sent"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponse('Already LoggedIn')
        else:
            return super(UserCreateView, self).get(request, *args, **kwargs)


def login(request, *args, **kwargs):
    if request.method == 'GET' and request.user.is_authenticated:
        return HttpResponse('Already LoggedIn')
    return authview.login(request, *args, **kwargs)


class MailVerify(generic.TemplateView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return render(request, 'accounts/success.html', {
                'message': 'You are loggedin, please logout to continue!'
            })
        hash_code = self.kwargs['hash_code']
        mail = models.MailVerification.objects.filter(Q(hash_code=hash_code), Q(mail_type=0))
        if mail.exists():
            mail = mail[0]
            if mail.user.groups.all()[0].name == 'Clerk':
                message = 'Mail confirmed, wait till admin accepts it.'
            else:
                message = 'Mail successfully verified!'
            mail.delete()
            return render(request, 'accounts/success.html', {
                'message': message
            })
        else:
            return render(request, 'accounts/success.html', {
                'message': 'You mail is already Verified'
            })


def change_password(request):
    if not request.user.is_authenticated:
        return HttpResponse('Permisssion denied!')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return render(request, 'accounts/password_udpated.html', {})
        else:
            return render(request, 'accounts/change_password.html', {
                'form': form
            })
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })


class UserUpdateView(LoginRequiredMixin, UpdateView):
    form_class = forms.UserUpdateForm
    model = User
    template_name = 'accounts/user_update.html'
    success_url = '/parcel/'

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object():
            return HttpResponse('Permission Denied')
        if self.request.user.groups.all()[0].name != 'Student':
            self.form_class = forms.UsersUpdateForm
        return super(UserUpdateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        a = super(UserUpdateView, self).get_context_data(**kwargs)
        a['pin'] = self.get_object().profile.pin
        return a

    def post(self, request, *args, **kwargs):
        if request.user != self.get_object():
            return HttpResponse("permission Denied")
        if self.request.user.groups.all()[0].name != 'Student':
            self.form_class = forms.UsersUpdateForm
        return super(UserUpdateView, self).post(request, *args, **kwargs)


class ForgotUserPasswordUpdateView(UpdateView):
    serializer_class = forms.ForgotPasswordUpdateView
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return models.MailVerification.objects.filter(hash_code=self.kwargs['id'])

    def get_object(self):
        return get_object_or_404(self.get_queryset()).user

    def get(self, request, *args, **kwargs):
        if not self.get_queryset().exists():
            context = {'message': 'No Link Found as per given requirement', 'error': 1, 'title': 'Password Updation'}
            return render(request, 'registration/password_forgot.html', context=context)
        if self.get_queryset()[0].time_limit < timezone.now().date():
            return render(request, 'registration/password_forgot.html', {
                'message': 'Link expired, please perform the operation again',
                'error': 1,
                'title': 'Password Updation'})

        return render(request, 'registration/password_reset.html', {'mail_code': self.kwargs['id']})

    def post(self, request, *args, **kwargs):
        self.get_object()
        password1 = request.POST.get('password1', None)
        password2 = request.POST.get('password2', None)
        if password1 is None or password2 is None:
            context = {'message': 'Fill the form completely', 'error': 1, 'title': 'Password updation', 'mail_code':
                       self.kwargs['id']}
            return render(request, 'registration/password_reset.html', context)
        if len(password1) < 8:
            context = {'message': 'Min password length is 8', 'error': 1, 'title': 'Password Updation', 'mail_code':
                self.kwargs['id']}
            return render(request, 'registration/password_reset.html', context)
        if password1 != password2:
            context = {'message': 'Fill the same passwords both the times', 'error': 1, 'title': 'Password updation',
                       'mail_code': self.kwargs['id']}
            return render(request, 'registration/password_reset.html', context)
        # update user
        user = self.get_object()
        user.set_password(password1)
        user.save()
        # delete all the user logged-in instances
        # delete mail verification
        self.get_queryset().delete()
        context = {'message': 'Password successfully updated', 'error': 0}
        return render(request, 'registration/login.html', context)


class ForgotPassword(TemplateView):
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        return render(request, 'registration/password_forgot.html',
                      {})

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', None)
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'registration/password_forgot.html', {'message': 'Enter valid email', 'error': 1})
        if not User.objects.filter(email=email).exists():
            return render(request, 'registration/password_forgot.html', {'message': 'email not found on the server', 'error': 1})
        verify = models.MailVerification.objects.filter(user=User.objects.get(email=email), mail_type=2)
        if verify.exists():
            mail = verify[:1].get()
            mail.time_limit = timezone.now() + datetime.timedelta(days=1)
            hash_code = mail.hash_code
            mail.save()
        else:
            hash_code = sha256((str(random.getrandbits(256)) + email).encode('utf-8')).hexdigest()
            models.MailVerification(user=User.objects.get(email=email), hash_code=hash_code, mail_id=email,
                                    time_limit=(datetime.datetime.now().date() + datetime.timedelta(days=1)),
                                    mail_type=2).save()
        kwargs = {'mail_type': 2, 'id': hash_code}
        mails.main(to_mail=email, **kwargs)
        return render(request, 'registration/password_forgot.html',
                      {'message': 'Check your mail', 'error': 0})