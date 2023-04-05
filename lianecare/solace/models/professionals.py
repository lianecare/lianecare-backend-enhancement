import logging
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from model_utils.models import TimeStampedModel
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField
from easy_thumbnails.fields import ThumbnailerImageField
from ..enums import HowKnowUs, GenderType
from ..utils import calculateAge
from ...users.models import User

logger = logging.getLogger(__name__)


# Create your models here.
# class CaregiverProManager(models.Manager):
#    def get_total_abbonamenti_for_month(self):
#       """
#       Ritorna il numero degli abbonamenti per mese
#      :return:
#     """
#        return self.annotate(month=TruncMonth('start_validity')).values('month').annotate(
#            tot=Count('id')).order_by()

def availability_default():
    return list([0, 0, 0, 0, 0, 0, 0] for x in range(4))


class CaregiverProManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.PRO)


class CaregiverPro(User):
    base_type = User.Types.PRO
    objects = CaregiverProManager()

    @property
    def more(self):
        return self.caregiverpromore

    class Meta:
        proxy = True


class CaregiverProMore(TimeStampedModel, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(_("Sesso"), choices=GenderType.choices, default='', max_length=25)
    birthday = models.DateField(_('Data di nascita'), blank=True, null=True)
    phone = models.CharField(_('Telefono'), blank=True, null=True, max_length=50)
    nationality = models.CharField(_('Nazionalità'), blank=True, max_length=100, default='')
    bio = models.TextField(_("Presentazione"), blank=True)
    photo = ThumbnailerImageField(upload_to='caregiverpro', blank=True, null=True, default=None)
    how_know_us = models.CharField(choices=HowKnowUs.choices, max_length=35, blank=True)
    # Availability
    availability = ArrayField(
        ArrayField(models.IntegerField(), size=7, ),
        size=4, default=availability_default())

    # Ability
    has_car = models.BooleanField(_('Automunita?'), blank=True, null=True, default=None)
    driving_license = models.BooleanField(_("Ha la patente?"), blank=True, null=True, default=None)
    is_graduate = models.BooleanField(_("Hai una laurea in ambito medico?"), blank=True, null=True, default=None)
    is_certificated = models.BooleanField(_("Hai una certificazione in ambito medico?"), blank=True, null=True,
                                          default=None)
    is_smoker = models.BooleanField(_("Fuma?"), blank=True, null=True, default=None)
    first_aid = models.BooleanField(_("Primo soccorso"), blank=True, null=True, default=None)
    child_trainer = models.BooleanField(_("Formatore per l'infanzia"), blank=True, null=True, default=None)
    identity_checked = models.BooleanField(_("Identità verificata?"), blank=True, null=True, default=None)
    # skills = HStoreField(blank=True, null=True, default=None)

    # Settings
    newsletter = models.BooleanField(default=False)
    notify_new_proposal = models.BooleanField(default=True)
    notify_new_message = models.BooleanField(default=True)

    # Coordinates
    house_number = models.CharField(_("Civico"), max_length=10, default=None)
    address = models.CharField(_("Indirizzo"), max_length=255, default=None)
    city = models.CharField(_("Città"), max_length=255, blank=True)
    postcode = models.CharField(_("CAP"), max_length=5, blank=True, validators=[
        RegexValidator(regex='[\d]{5}', message=_('Il codice postale non è valido.'), code='invalid_zipcode')],
                                default='00100')
    region = models.CharField(_("Regione"), max_length=65, blank=True)
    country = models.CharField(_("Nazione"), max_length=65, blank=True)
    latitude = models.FloatField(_("Latitudine"), blank=True, null=True, default=None)
    longitude = models.FloatField(_("Longitudine"), blank=True, null=True, default=None)

    # Courses
    has_basic_course = models.BooleanField(_("Corso base"), default=False)
    has_pro_course = models.BooleanField(_("Corso PRO"), default=False)

    #Validate caregiver pro
    validate_care_pro = models.BooleanField(_('Validate'), blank=True, null=True, default=False)

    def __str__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)

    # def get_absolute_url(self):
    #     return reverse('caregiverspro-detail', kwargs={'pk': self.pk})

    def get_percentage_of_profile(self):
        status = 14
        status += 5 if self.check_avaialability() else 0
        status += 10 if self.has_basic_course else 0
        status += 20 if self.has_pro_course else 0
        status += 5 if self.photo else 0
        status += 5 if self.bio else 0
        status += 25 if self.user.services.count() > 0 else 0
        status += 2 if self.nationality else 0
        status += 2 if self.has_car is not None else 0
        status += 2 if self.driving_license is not None else 0
        status += 2 if self.is_graduate is not None else 0
        status += 2 if self.is_certificated is not None else 0
        status += 2 if self.is_smoker is not None else 0
        status += 2 if self.first_aid is not None else 0
        status += 2 if self.child_trainer is not None else 0
        return status

    def get_age(self):
        if self.birthday:
            return calculateAge(self.birthday)
        return 0

    def check_avaialability(self):
        esito = False
        for row in self.availability:
            for col in row:
                if col == 1:
                    esito = True
                    break
            if esito: break
        return esito

    class Meta:
        verbose_name = _('Caregiver PRO')
        verbose_name_plural = _('Caregivers PRO')

    def clean(self):
        if not self.pk:
            if calculateAge(self.birthday) < 18:
                raise ValidationError({
                    'birthday': ValidationError(_('Devi avere almeno 18 anni per registrarti su LianeCare.'),
                                                code='error'),
                })
