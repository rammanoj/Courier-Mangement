import datetime
import random
from _sha256 import sha256

from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from accounts import mails
from . import models
from django import forms


class Register(UserCreationForm):

    USER_TPYE = (('Student', 'Student'),
                 ('Clerk', 'Clerk'))

    userid = forms.CharField(required=False, max_length=200, label='Your Id')
    user_type = forms.ChoiceField(choices=USER_TPYE, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username Already taken!')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email Already Chosen')
        return email

    def clean_password(self):
        password1 = self.cleaned_data.get('password1', None)
        password2 = self.cleaned_data.get('password2', None)

        if len(password1) < 8:
            raise forms.ValidationError('Password Min length is 8')

        if password1 is None or password2 is None:
            raise forms.ValidationError('Password is required!')

        if password1 != password2:
            raise forms.ValidationError('Enter same passwords, both the times')

        return password1

    def save(self, commit=True):
        user = super(Register, self).save(commit=False)
        if self.cleaned_data.get('user_type', None) == 'Clerk':
            user.is_active = False
        else:
            user.is_active = True
        user.save()

        g = Group.objects.get(name=self.cleaned_data.get('user_type', None))
        g.user_set.add(user)

        userid = self.cleaned_data.get('userid')
        models.Profile.objects.create(user=user, userid=userid)

        email = self.cleaned_data.get('email', None)
        hash_code = sha256((str(random.getrandbits(256)) + email).encode('utf-8')).hexdigest()
        models.MailVerification.objects.create(user=user, hash_code=hash_code, mail_type=0)

        kwargs = {'mail_type': 0, 'id': hash_code}
        mails.main(to_mail=email, **kwargs)
        return user

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'userid', 'user_type')


class UserUpdateForm(forms.ModelForm):
    pin = forms.CharField(max_length=100)

    def clean_pin(self):
        if len(self.cleaned_data['pin']) < 5:
            raise forms.ValidationError('Min length of Pin is 5')
        print(self.cleaned_data['pin'])
        return self.cleaned_data['pin']

    def clean_username(self):
        qs = User.objects.filter(email=self.cleaned_data['username'])
        qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Username Already Exist!!')
        return self.cleaned_data['username']

    def clean_email(self):
        qs = User.objects.filter(email=self.cleaned_data['email'])
        qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Email Already Exist!!')
        return self.cleaned_data['email']

    def save(self, commit=True):
        print("Came here")
        user = super(UserUpdateForm, self).save()
        user.profile.pin = self.cleaned_data['pin']
        print(user.profile.pin)
        user.profile.save()

        return user

    class Meta:
        model = User
        fields = ('username', 'email', 'pin')


class UsersUpdateForm(forms.ModelForm):

    def clean_username(self):
        qs = User.objects.filter(email=self.cleaned_data['username'])
        qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Username Already Exist!!')
        return self.cleaned_data['username']

    def clean_email(self):
        qs = User.objects.filter(email=self.cleaned_data['email'])
        if self.instance.pk is not None:
            qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Email Already Exist!!')
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ('username', 'email')


class ForgotPasswordUpdateView(forms.Form):
    password1 = forms.CharField(required=True)
    password2 = forms.CharField(required=True)