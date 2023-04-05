import logging

import uuid as uuid

from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import m2m_changed
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from ..enums import WhenJobPost, ExperienceYears, JobPostStatus, ProposalStatus
from ..tasks import find_candidates_for_jobpost_and_send_email
from lianecare.users.models import User

logger = logging.getLogger(__name__)


class Category(TimeStampedModel, models.Model):
    code = models.CharField(_("Codice"), max_length=20, unique=True)
    name = models.CharField(_("Nome"), max_length=100)
    icon = models.CharField(_("Icona"), max_length=25, blank=True, null=True, default=None)
    active = models.BooleanField(_("Attiva?"), default=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _("Categoria")
        verbose_name_plural = _("Categorie")

    def __str__(self):
        return self.name


class SubCategory(TimeStampedModel, models.Model):
    parent = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="subcategories")
    code = models.CharField(_("Codice"), max_length=20)
    name = models.CharField(_("Nome"), max_length=100)
    description = models.CharField(_("Descrizione"), max_length=255, blank=True)
    active = models.BooleanField(_("Attiva?"), default=True)
    requirement = models.BooleanField(_("Certificazioni?"), default=False)

    class Meta:
        ordering = ('name',)
        verbose_name = _("Sottocategoria")
        verbose_name_plural = _("Sottocategorie")
        constraints = [
            models.UniqueConstraint(
                fields=['parent', 'code'],
                name='unique_subcategory_category')
        ]

    def __str__(self):
        return self.name


class ServiceManager(models.Manager):
    def get_candidates_for_jobpost(self, jobpost, subcategories_pks=None):
        """Restituisce la lista di servizi con relativi Caregiver per almeno una categoria inserita e nella stessa città"""
        # Get Service for almost one subcategory
        if subcategories_pks:
            query = self.filter(is_active=True, subcategories__in=subcategories_pks).distinct()
        else:
            sc_list = jobpost.get_subcategories_list
            query = self.filter(is_active=True, subcategories__in=sc_list).distinct()

        # Todo: filter for distance and other parameters
        # Service.objects.raw('SELECT id, first_name, last_name, birth_date FROM myapp_person')
        query = query.filter(caregiver__caregiverpromore__city=jobpost.city)
        query = query.select_related('caregiver')
        return query

    # def with_distance(self):
    #    return self.annotate(
    #        distance=Expression)
    #    )


class Service(TimeStampedModel, models.Model):
    caregiver = models.ForeignKey("CaregiverPro", on_delete=models.CASCADE, related_name="services")
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    subcategories = models.ManyToManyField("SubCategory", _("Services"))
    experience = models.PositiveIntegerField(_("Anni di esperienza"), default=0)
    price = models.FloatField(_("Prezzo medio"))
    has_references = models.BooleanField(_("Referenze?"), blank=True, null=True, default=None)
    max_distance = models.PositiveIntegerField(_("Distanza max (km)"), blank=True, null=True, default=10)
    note = models.TextField(_("Note aggiuntive"), blank=True, default='')
    is_active = models.BooleanField(_("Attivo?"), default=True)

    objects = ServiceManager()

    class Meta:
        verbose_name = _("Servizio")
        verbose_name_plural = _("Servizi")
        constraints = [
            models.UniqueConstraint(
                fields=['caregiver', 'category'],
                name='unique_category_for_caregiver')
        ]


class JobPost(TimeStampedModel, models.Model):
    # Who
    user = models.ForeignKey('Person', on_delete=models.CASCADE, related_name="job_posts")
    # What
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    subcategories = models.ManyToManyField("SubCategory")
    # When
    when = models.IntegerField(choices=WhenJobPost.choices)
    # Where
    address = models.CharField(_("Indirizzo"), max_length=255, blank=True, null=True, default=None)
    house_number = models.CharField(_("Civico"), max_length=10, blank=True, null=True, default=None)
    city = models.CharField(_("Città"), max_length=255, blank=True)
    postcode = models.CharField(_("CAP"), max_length=5, blank=True, null=True, default=None)
    region = models.CharField(_("Regione"), max_length=65, blank=True, null=True, default=None)
    country = models.CharField(_("Nazione"), max_length=65, blank=True, null=True, default=None)
    latitude = models.FloatField(blank=True, null=True, default=None)
    longitude = models.FloatField(blank=True, null=True, default=None)
    # extra
    experience = models.IntegerField(_("Anni di esperienza"), choices=ExperienceYears.choices)
    has_references = models.BooleanField(_("Referenze?"), default=False)
    note = models.TextField(_("Note aggiuntive"), blank=True, default='')
    is_active = models.BooleanField(_("Attivo?"), default=True)
    status = models.CharField(choices=JobPostStatus.choices, max_length=55, default=JobPostStatus.ACTIVE)
    # candidates
    candidates = models.ManyToManyField('CaregiverPro', through='Proposal')

    class Meta:
        verbose_name = _("Job Post")
        verbose_name_plural = _("Job Posts")
        ordering = ('-created',)

    def get_subcategories_list(self):
        qr = self.subcategories.all()
        qr = qr.values_list('id', flat=True)
        return list(qr)

    def find_caregivers_pro(self, subcategories_pks=[]):
        """
        Chiama il task per cercare dei possibili Caregivers Pro per uno specifico Job Post
        """
        if subcategories_pks:
            # launch asynchronous task
            find_candidates_for_jobpost_and_send_email.delay(self.id, subcategories_pks)

    def __str__(self):
        return "Job Post di %s " % (self.user.email)

    def number_candidates(self):
        """
        Method for getting the number of candidates
        :return: int total number
        """
        return self.candidates.count()

    number_candidates.short_description = "n° candidati"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.status in [JobPostStatus.ACTIVE, JobPostStatus.NO_SHOW]:
            # new_proposal_status = ProposalStatus.APPROVED if self.status == JobPostStatus.OK_SOLACE else ProposalStatus.DELETE
            new_proposal_status = ProposalStatus.DELETE
            self.proposal_set.update(status_employee=new_proposal_status)


# Signal
def jobpost_subcategories_changed(sender, **kwargs):
    # Signal when a job post's subcategory is changed and find other caregiver for the job post
    job_post = kwargs.get('instance')
    subcat_pks = kwargs.get('pk_set')
    action = kwargs.get('action')
    if action == 'post_add':
        job_post.find_caregivers_pro(list(subcat_pks))


m2m_changed.connect(jobpost_subcategories_changed, sender=JobPost.subcategories.through)


class ProposalManager(models.Manager):
    def get_proposals_in_km(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)


class Proposal(TimeStampedModel, models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
    jobpost = models.ForeignKey('JobPost', on_delete=models.CASCADE)
    caregiverpro = models.ForeignKey('CaregiverPro', on_delete=models.CASCADE)
    status_caregiverpro = models.IntegerField(choices=ProposalStatus.choices, default=ProposalStatus.PROPOSED)
    status_employee = models.IntegerField(choices=ProposalStatus.choices, default=ProposalStatus.PROPOSED)
    distance = models.FloatField(default=None, blank=True, null=True)

    objects = ProposalManager()

    class Meta:
        ordering = ('-created',)
        verbose_name = _("Proposta")
        verbose_name_plural = _("Proposte")
        constraints = [
            models.UniqueConstraint(
                fields=['caregiverpro', 'jobpost'],
                name='unique_caregiver')
        ]

    def get_absolute_url_for_type_user(self, user_type):
        """Get url for Proposal detail view for User type."""
        try:
            current_domain = Site.objects.get_current().domain
            if user_type == User.Types.EMPLOYEE:
                return 'https://{domain}{path}'.format(
                    domain=current_domain, path=reverse("solace:person_proposal_detail", kwargs={"uuid": self.uuid}))
            if user_type == User.Types.PRO:
                return 'https://{domain}{path}'.format(
                    domain=current_domain,
                    path=reverse("solace:caregiver_proposal_detail", kwargs={"uuid": self.uuid}))
        except NoReverseMatch:
            return
        return


def __str__(self):
    return "Proposta %s " % (self.uuid)
