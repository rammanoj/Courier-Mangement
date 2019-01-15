from accounts import mails
from . import models
from django import forms
from accounts.models import Profile


class ParcelForm(forms.ModelForm):
    student = forms.CharField(max_length=100)

    def clean_student(self):
        if not Profile.objects.filter(userid=self.cleaned_data['student']).exists():
            raise forms.ValidationError('Enter the valid StudentId')
        return self.cleaned_data['student']

    def save(self, commit=True):
        parcel = super(ParcelForm, self).save()

        kwargs = {'mail_type': 6}
        student = Profile.objects.get(userid=parcel.student)
        mails.main(to_mail=student.user.email, **kwargs)

        return parcel

    class Meta:
        model = models.Parcel
        fields = ('parcel_id', 'delivery_service', 'student')