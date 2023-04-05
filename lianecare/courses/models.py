import logging

import uuid

from django.contrib import admin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from model_utils.fields import MonitorField
from easy_thumbnails.fields import ThumbnailerImageField
from django.db.models import Avg
from django.conf import settings

from lianecare.orders.models import Order
from lianecare.users.models import User

logger = logging.getLogger(__name__)


# Create your models here.
class Course(TimeStampedModel, models.Model):
    class CourseTypes(models.TextChoices):
        BASIC = "BASIC", _("Base")
        PRO = "PRO", _("Avanzato")

    title = models.CharField(_("Titolo"), max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField(blank=True)
    cover = ThumbnailerImageField(upload_to='courses', blank=True, default='')
    price = models.IntegerField(_("Prezzo"), default=0, help_text="Prezzo in centesimi")
    type = models.CharField(_("Tipo corso"), choices=CourseTypes.choices, default=CourseTypes.BASIC, max_length=25)
    is_active = models.BooleanField(_('Attivo'), default=True)
    product_stripe = models.OneToOneField('djstripe.Product', null=True, blank=True, on_delete=models.SET_NULL,
                                          help_text=_("ID prodotto in Stripe"))
    price_stripe = models.OneToOneField('djstripe.Price', null=True, blank=True, on_delete=models.SET_NULL,
                                        help_text=_("ID prezzo in Stripe"))
    is_salable = models.BooleanField(_("In vendita"), default=True)
    user_type = models.CharField(_("Tipo"), max_length=50, choices=User.Types.choices, default=User.base_type)
    sequence = models.IntegerField(_("Sequenza"), default=0)
    course_offer = models.TextField(_("offerta del corso"), max_length=250, null=True, blank=True, default='')

    class Meta:
        ordering = ['sequence', '-created']
        verbose_name = _("Corso")
        verbose_name_plural = _("Corsi")

    def __str__(self):
        return self.title

    @property
    def n_modules(self):
        return self.modules.count()

    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)

    def get_absolute_url(self):
        return reverse("courses:course_detail", kwargs={"slug": self.slug})


class Module(TimeStampedModel, models.Model):
    course = models.ForeignKey('Course', related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    video_url = models.URLField()
    minutes = models.PositiveIntegerField(_('Durata: minuti'), blank=False, default=1)
    seconds = models.PositiveIntegerField(_('Durata: secondi'), blank=False, default=0)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    is_active = models.BooleanField(_('Attivo'), default=True)

    class Meta:
        ordering = ['order']
        verbose_name = _("Modulo")
        verbose_name_plural = _("Moduli")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Get url for Module's detail view.
        Returns:
            str: URL for Module detail.
        """
        return reverse("courses:module_detail", kwargs={"slug": self.course.slug, "pk": self.id})

    # def minutes_text(self):
    #     h, m = divmod(self.duration, 60)
    #     return "%d:%02d" % (h, m)
    @property
    def minutes_text(self):
        return "%d:%02d" % (self.minutes, self.seconds)


class Enrollment(TimeStampedModel, models.Model):
    TIPO_STATO = (
        (0, _('Da iniziare')),  # al momento dell'acquisto
        (1, _('In corso')),  # se un modulo visto
        (2, _('Completato')),  # tutti i moduli visti
        (3, _('Superato')),  # test superato
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="my_courses")
    course = models.ForeignKey('Course', related_name='students', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, null=True, blank=True, default=None, on_delete=models.SET_NULL,
                              help_text=_("ID ordine"))
    session_stripe_id = models.CharField(max_length=255, unique=True, blank=True, null=True, default=None)
    modules = models.ManyToManyField('Module', through='EnrollmentStatus')
    status = models.IntegerField(choices=TIPO_STATO, default=0, verbose_name=_('Stato'))

    # test
    class Meta:
        ordering = ['-created']
        unique_together = ('user', 'course')

    # objects = EnrollmentManager()

    def start_course(self):
        """
        Inizializza i moduli con i loro stato "non visto" e fa partire il corso
        """
        module_list = Module.objects.filter(course=self.course, is_active=True)
        lista_en = [EnrollmentStatus(module=module, enrollment_id=self.id, order=module.order) for module in
                    module_list]
        EnrollmentStatus.objects.bulk_create(lista_en)

    def get_progress(self):
        """Calcola la percentuale di visualizzazione del corso"""
        total_modules = self.modules.all().count()
        total_modules_viewed = self.enrollmentstatus_set.filter(viewed=True).count()
        perc = (total_modules_viewed / total_modules) * 100
        return '{0}%'.format(perc)

    get_progress.short_description = _("Avanzamento")


class EnrollmentStatus(TimeStampedModel, models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE)
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    viewed = models.BooleanField(_('Visto'), default=False)

    class Meta:
        ordering = ['order']

    # def get_absolute_url(self):
    #    return reverse("solace:student_module_detail", kwargs={"uuid": self.uuid})


@receiver(post_save, sender=Enrollment)
def automatic_start_course(sender, **kwargs):
    """
    All'iscrizione di un utente ad un corso, creazione dei moduli con gli stati di visualizzazione.
    """
    if kwargs.get('created', False):
        enrollment = kwargs.get('instance')
        enrollment.start_course()
