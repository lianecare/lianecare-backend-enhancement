import logging
import json

from allauth.account.views import SignupView
from django.contrib import messages
from django.http import HttpResponse
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Case, When
from django.views.generic import DetailView, UpdateView, ListView, CreateView, DeleteView
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.views.decorators.csrf import ensure_csrf_cookie


from lianecare.chat.forms import SendMessageForm
from .enums import ProposalStatus, JobPostStatus
from .forms import PersonSignupForm, CaregiverSignupForm, PersonUpdateForm, FamilyMemberFormSetInline, \
    CaregiverProUpdateForm, JobPostForm, JobPostUpdateForm, PersonSettingsUpdateForm, CaregiverSettingsUpdateForm
from .models import CaregiverPro, Category, Service, PersonMore, CaregiverProMore, JobPost, Proposal
from .tasks import notify_user_for_new_message

logger = logging.getLogger(__name__)
User = get_user_model()


# HOME #
class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


# PERSON REGISTRATION #
class PersonSignupView(SignupView):
    template_name = 'solace/person_signup.html'
    form_class = PersonSignupForm
    redirect_field_name = "next"
    success_url = None


person_signup_view = PersonSignupView.as_view()


# PERSON DETAIL #
class PersonDetailView(LoginRequiredMixin, DetailView):
    model = PersonMore
    slug_field = "user__username"
    slug_url_kwarg = "username"
    template_name = 'solace/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job_posts'] = JobPost.objects.filter(user=self.object.user, is_active=True).select_related(
            'category').prefetch_related('subcategories')
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('user')


person_detail_view = PersonDetailView.as_view()


# PERSON SETTINGS #
class PersonSettingsView(LoginRequiredMixin, UpdateView):
    model = PersonMore
    form_class = PersonSettingsUpdateForm
    template_name = 'solace/person_settings.html'

    def get_object(self):
        return PersonMore.objects.select_related('user', 'employer').get(user=self.request.user)

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, _("Impostazioni modificate"))
        return reverse("solace:person_settings")


person_settings_view = PersonSettingsView.as_view()


# PERSON UPDATE #
class PersonUpdateView(LoginRequiredMixin, UpdateView):
    model = PersonMore
    form_class = PersonUpdateForm
    template_name = 'solace/person_update.html'

    def get_object(self):
        return PersonMore.objects.get(user=self.request.user)

    # Metodo per istanziare il formset
    def get_formset(self, data=None):
        return FamilyMemberFormSetInline(instance=self.object.user, data=data)

    def get_success_url(self):
        return reverse("solace:person_detail", kwargs={"username": self.request.user.username})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            # context['formset'] = FamilyMemberFormSetInline(self.request.POST, instance=self.object)
            context['formset'] = self.get_formset(data=self.request.POST)
        else:
            # context['formset'] = FamilyMemberFormSetInline(instance=self.object)
            context['formset'] = self.get_formset()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset and formset.is_valid():
            formset.save()
        else:
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)


person_update_view = PersonUpdateView.as_view()


# PERSON JOB POSTS LIST #
class PersonJobPostsView(LoginRequiredMixin, ListView):
    model = JobPost
    template_name = 'solace/jobpost/person_jobpost_list.html'
    context_object_name = 'jobposts_list'
    paginate_by = 8

    def get_queryset(self):
        return JobPost.objects.filter(user=self.request.user,
                                      status__in=[JobPostStatus.ACTIVE, JobPostStatus.NO_SHOW]).select_related(
            'category').prefetch_related(
            'subcategories')


person_job_posts_view = PersonJobPostsView.as_view()


# PERSON INSERT JOB POST #
class PersonCreateJobPostView(LoginRequiredMixin, CreateView):
    model = JobPost
    form_class = JobPostForm
    template_name = 'solace/jobpost/jobpost_create_form.html'
    success_msg = _("Job Post inserito con successo")

    def get_success_url(self):
        return reverse("solace:person_job_posts")

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        job_post = form.save(commit=False)
        job_post.user = self.request.user
        job_post.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display Job Post Categories that belong to a given user"""
        kwargs = super(PersonCreateJobPostView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


person_create_job_post_view = PersonCreateJobPostView.as_view()


# PERSON UPDATE JOB POST #
class PersonUpdateJobPostView(LoginRequiredMixin, UpdateView):
    model = JobPost
    form_class = JobPostUpdateForm
    success_msg = _("Job Post modificato")
    template_name = 'solace/jobpost/jobpost_update_form.html'

    def get_success_url(self):
        return reverse("solace:person_job_posts")


person_update_job_post_view = PersonUpdateJobPostView.as_view()


# PERSON JOBPOST DETAIL WITH PROPOSALS LIST #
class PersonDetailJobPostView(LoginRequiredMixin, SingleObjectMixin, ListView):
    # model = JobPost
    paginate_by = 10
    template_name = 'solace/jobpost/jobpost_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=JobPost.objects.all().select_related('category'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobpost'] = self.object
        return context

    def get_queryset(self):
        return self.object.proposal_set.filter(status_employee__gte=ProposalStatus.PROPOSED).select_related(
            'caregiverpro', 'caregiverpro__caregiverpromore')


person_detail_jobpost_view = PersonDetailJobPostView.as_view()


# PERSON PROPOSAL DETAILS #
class PersonProposalDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Proposal
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    template_name = 'solace/proposal/person_proposal_detail.html'
    form_class = SendMessageForm

    def get_success_url(self):
        return reverse('solace:person_proposal_detail', kwargs={'uuid': self.object.uuid})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        to = self.object.caregiverpro
        sender = self.request.user
        mes = form.save(commit=False)
        mes.proposal = self.object
        mes.sender = sender
        mes.to = to
        mes.save()
        if to.more.notify_new_message and self.object.status_caregiverpro >= 0:
            object = self.get_object()
            cta_url = object.get_absolute_url_for_type_user(User.Types.PRO)
            notify_user_for_new_message.delay(to.first_name, to.email, sender.first_name, cta_url)
        return super().form_valid(form)

    def get_queryset(self):
        return Proposal.objects.filter(jobpost__user=self.request.user,
                                       status_employee__gte=ProposalStatus.PROPOSED).select_related(
            'caregiverpro').prefetch_related('chat', 'chat__sender')


person_proposal_detail_view = PersonProposalDetailView.as_view()


# CAREGIVER REGISTRATION #
class CaregiverSignupView(SignupView):
    template_name = 'solace/caregiverpro/caregiver_signup.html'
    form_class = CaregiverSignupForm
    redirect_field_name = "next"
    success_url = None


caregiver_signup_view = CaregiverSignupView.as_view()


# LANDING CAREGIVER REGISTRATION #
class CaregiverSignupLandingView(SignupView):
    template_name = 'solace/caregiverpro/caregiver_signup_landing.html'
    form_class = CaregiverSignupForm
    redirect_field_name = "next"
    success_url = None


# CAREGIVER DETAILS #
class CaregiverDetailView(LoginRequiredMixin, DetailView):
    model = CaregiverPro
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = 'solace/caregiverpro/caregiver_detail.html'

    # def get_object(self):
    #    return CaregiverPro.objects.get(user__username=self.request.user.username)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('caregiverpromore')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = Service.objects.filter(caregiver=self.object)
        if self.request.user == self.object:
            values = services.values_list('category__id', flat=True)
            context['categories'] = Category.objects.filter(active=True).exclude(id__in=list(values))
        else:
            services = services.filter(is_active=True)
        if 'job_id' in self.request.GET and self.request.GET.get('job_id') is not None:
            get_job_details = JobPost.objects.get(pk =self.request.GET.get('job_id') )
            services = services.order_by(
                    Case(When(category_id=get_job_details.category.pk, then=0), default=1)
            )
        context['services'] = services
        return context


caregiver_detail_view = CaregiverDetailView.as_view()


# CAREGIVER UPDATE #
class CaregiverUpdateView(LoginRequiredMixin, UpdateView):
    model = CaregiverProMore
    form_class = CaregiverProUpdateForm
    template_name = 'solace/caregiverpro/caregiver_update.html'

    def get_object(self):
        return CaregiverProMore.objects.select_related('user').get(user=self.request.user)

    def get_success_url(self):
        return reverse("solace:caregiver_detail", kwargs={"username": self.request.user.username})


caregiver_update_view = CaregiverUpdateView.as_view()


# CAREGIVER SETTINGS #
class CaregiverSettingsView(LoginRequiredMixin, UpdateView):
    model = CaregiverProMore
    form_class = CaregiverSettingsUpdateForm
    template_name = 'solace/caregiverpro/caregiver_settings.html'

    def get_object(self):
        return CaregiverProMore.objects.get(user=self.request.user)

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, _("Impostazioni modificate"))
        return reverse("solace:caregiver_settings")


caregiver_settings_view = CaregiverSettingsView.as_view()


# CAREGIVER PROPOSALS LIST #
class CaregiverProposalsView(LoginRequiredMixin, ListView):
    model = Proposal
    template_name = 'solace/proposal/caregiver_proposals_list.html'
    context_object_name = 'proposals_list'
    paginate_by = 10

    def get_queryset(self):
        return Proposal.objects.select_related('jobpost', 'jobpost__user', 'jobpost__category').filter(
            caregiverpro=self.request.user, status_caregiverpro__gte=ProposalStatus.PROPOSED).exclude(
            status_employee=ProposalStatus.DELETE)


caregiver_proposals_view = CaregiverProposalsView.as_view()


# CAREGIVER PROPOSAL DETAILS #
class CaregiverProposalDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Proposal
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    template_name = 'solace/proposal/caregiver_proposal_detail.html'
    form_class = SendMessageForm

    def get_success_url(self):
        return reverse('solace:caregiver_proposal_detail', kwargs={'uuid': self.object.uuid})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        to = self.object.jobpost.user
        sender = self.request.user
        mes = form.save(commit=False)
        mes.proposal = self.object
        mes.sender = sender
        mes.to = to
        mes.save()
        if to.more.notify_new_message and self.object.status_employee >= 0:
            object = self.get_object()
            cta_url = object.get_absolute_url_for_type_user(User.Types.EMPLOYEE)
            notify_user_for_new_message.delay(to.first_name, to.email, sender.first_name, cta_url)
        return super().form_valid(form)

    def get_queryset(self):
        return Proposal.objects.filter(caregiverpro=self.request.user,
                                       status_caregiverpro__gte=ProposalStatus.PROPOSED).exclude(
            status_employee=ProposalStatus.DELETE).select_related('jobpost', 'jobpost__user', 'jobpost__category',
                                                                  'jobpost__user__personmore').prefetch_related('chat',
                                                                                                                'chat__sender')


caregiver_proposal_detail_view = CaregiverProposalDetailView.as_view()


@login_required
def ignore_proposal(request, pk):
    """Method for ignoring a Proposal"""
    try:
        empl = request.GET.get('empl')
        proposal = Proposal.objects.get(uuid=pk)
        if empl:
            proposal.status_employee = ProposalStatus.IGNORED
            proposal.save(update_fields=['status_employee'])
        else:
            proposal.status_caregiverpro = ProposalStatus.IGNORED
            proposal.save(update_fields=['status_caregiverpro'])
        messages.success(request, "Proposta eliminata")
    except Proposal.DoesNotExist:
        messages.error(request, "Errore interno, per favore riprova.")
        logger.error('Proposal does not exist')

    # next = request.GET.get('next', '/')
    if empl:
        return redirect("solace:person_jobpost_proposals", proposal.jobpost_id)
    else:
        return redirect("solace:caregiver_proposals")


@ensure_csrf_cookie
def check_email_exists(request):
    """Method for Checking Email Exists"""
    try:
        obj = User.objects.annotate(email_name=Lower('email'))
        obj.get(email_name=eval(request.body).get('email').lower())
        response = json.dumps("Email already in use!")
        return HttpResponse(response)
    except Exception as e:
        response = json.dumps(True)
        return HttpResponse(response)
