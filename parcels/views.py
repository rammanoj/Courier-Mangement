from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from accounts import mails
from parcels import models
from . import forms


class ParcelCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = forms.ParcelForm
    template_name = 'parcels/parcel_form.html'
    success_url = '/parcel/create/'
    success_message = 'Parcel has been successfully added!'
    
    def get(self, request, *args, **kwargs):
        if request.user.groups.all()[0].name != 'Clerk':
            return HttpResponse('Only Clerk can add a Parcel delivery')
        context = super(ParcelCreateView, self).get(request, *args, **kwargs)
        return context

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        form.instance.date_taken = timezone.now()
        return super(ParcelCreateView, self).form_valid(form)
    
    def post(self, request, *args, **kwargs):
        if self.request.user.groups.all()[0].name != 'Clerk':
            return HttpResponse('Only Clerks have the access to add the Deliveries!')
        return super(ParcelCreateView, self).post(request, *args, **kwargs)


class ParcelUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = forms.ParcelForm
    template_name = 'parcels/parcel_update_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(models.Parcel, pk=self.kwargs['pk'])
    
    def get(self, request, *args, **kwargs):
        if request.user.groups.all()[0].name not in ['Admin', 'Clerk']:
            return HttpResponse('Only Admins and CLerks can add a Parcel delivery')

        if request.user.groups.all()[0].name == 'Clerk' and request.user != self.get_object().added_by:
            return HttpResponse('Permission Denied!')
        return super(ParcelUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.groups.all()[0].name not in ['Admin', 'Clerk']:
            return HttpResponse('Only Admins and CLerks can add a Parcel delivery')

        if request.user.groups.all()[0].name == 'Clerk' and request.user != self.get_object().added_by:
            return HttpResponse('Permission Denied!')

        return super(ParcelUpdateView, self).post(request, *args, **kwargs)


class ParcelDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Parcel
    success_url = '/parcel/'

    def delete(self, request, *args, **kwargs):
        if request.user.groups.all()[0].name != 'Admin':
            return HttpResponse('Only Admins and CLerks can add a Parcel delivery')

        return super(ParcelDeleteView, self).delete(request, *args, **kwargs)


class ParcelListView(LoginRequiredMixin, ListView):
    model = models.Parcel
    paginate_by = 4

    def get_queryset(self):
        user = self.request.user.groups.all()[0].name
        try:
            name = self.request.GET['id']
            if name is not None and user != 'Student':
                return models.Parcel.objects.filter(student__contains=name)
        except KeyError:
            pass
        if user == 'Student':
            return models.Parcel.objects.filter(student=self.request.user.profile.userid)
        else:
            return models.Parcel.objects.all()


class ParcelDetailView(LoginRequiredMixin, DetailView):
    model = models.Parcel


class StudentConfirmView(LoginRequiredMixin, UpdateView):
    model = models.Parcel

    def post(self, request, *args, **kwargs):
        if request.user.groups.all()[0].name == 'Student':
            return HttpResponse('Permission Denied')
        student = request.POST.get('student', None)
        pin = request.POST.get('pin', None)
        parcel = request.POST.get('parcel', None)
        p = models.Parcel.objects.get(parcel_id=parcel)
        if student is None or pin is None or parcel is None:
            messages.success(request, 'Fill form completely')
            return redirect('parcel-detail', pk=p.pk)
        try:
            st = User.objects.get(profile__userid=student)
        except ObjectDoesNotExist:
            messages.success(request, 'Given Student deos not exist')
            return redirect('parcel-detail', pk=p.pk)

        if st.profile.pin == pin:
            p.status = True
            p.save()

            models.Delivary.objects.create(clerk=request.user, parcel=p)

            # Send mail on delivery.
            kwargs = {'mail_type': 7}
            mails.main(to_mail=st.email, **kwargs)
            request.session['message'] = 'Successfully delivered to student'
            messages.success(request, 'Successfully delivered to student')
            return redirect('parcel-detail', pk=p.pk)
        else:
            messages.success(request, 'Enter valid pin')
            return redirect('parcel-detail', pk=p.pk)
