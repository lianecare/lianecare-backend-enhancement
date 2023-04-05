import logging
import uuid
from random import choice
from string import ascii_lowercase, digits
from django.contrib.postgres.functions import RandomUUID
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from easy_thumbnails.fields import ThumbnailerImageField
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from ..enums import GenderType, CareNeed, HowKnowUs, Diagnosis
from ..fields import ChoiceArrayField
from ..utils import calculateAge
from ...users.models import User

logger = logging.getLogger(__name__)


class PersonManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().filter(user__type=User.Types.PERSON)


class Person(User):
    base_type = User.Types.PERSON
    objects = PersonManager()

    @property
    def more(self):
        return self.personmore

    class Meta:
        proxy = True


class PersonMore(TimeStampedModel, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(_("Sesso"), choices=GenderType.choices, default='', max_length=25)
    birthday = models.DateField(_("Data di nascita"), blank=True, null=True)
    family_bio = models.TextField(_("Biografia famigliare"), blank=True)
    # photo = models.ImageField(upload_to='persons/', blank=True, null=True, default=None)
    photo = ThumbnailerImageField(upload_to='persons', blank=True, default='')
    # Company
    employer = models.ForeignKey('Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="employees",
                                 default=None)
    how_know_us = models.CharField(choices=HowKnowUs.choices, max_length=35, blank=True)
    # Settings
    newsletter = models.BooleanField(default=False)
    notify_new_proposal = models.BooleanField(default=True)
    notify_new_message = models.BooleanField(default=True)

    # Coordinates
    house_number = models.CharField(_("Civico"), max_length=10, blank=True, null=True, default=None)
    address = models.CharField(_("Indirizzo"), max_length=255, blank=True, null=True, default=None)
    city = models.CharField(_("Città"), max_length=255, blank=True)
    postcode = models.CharField(_("CAP"), max_length=5, blank=True, validators=[
        RegexValidator(regex='[\d]{5}', message=_('The postcode is not valid.'), code='invalid_postcode')],
                                null=True, default=None)
    region = models.CharField(_("Regione"), max_length=65, blank=True, null=True, default=None)
    country = models.CharField(_("Nazione"), max_length=65, blank=True, null=True, default=None)
    latitude = models.FloatField(blank=True, null=True, default=None)
    longitude = models.FloatField(blank=True, null=True, default=None)

    # Courses
    has_basic_course = models.BooleanField(_("Corso base"), default=False)
    has_pro_course = models.BooleanField(_("Corso PRO"), default=False)

    class Meta:
        ordering = ('created',)
        verbose_name = _("Persona")
        verbose_name_plural = _("Persone")

    def __str__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)

    def get_age(self):
        if self.birthday:
            return calculateAge(self.birthday)
        return 0

    def get_absolute_url(self):
        """Get url for person's detail view.
        Returns:
            str: URL for Person detail.
        """
        return reverse("solace:person_detail", kwargs={"username": self.user.username})


class FamilyMember(TimeStampedModel, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="family_members",
                                default=None)
    name = models.CharField(_("Nome"), max_length=155)
    birthday = models.DateField(_("Data di nascita"), default=None)
    gender = models.CharField(_("Sesso"), choices=GenderType.choices, default='', max_length=25)
    diagnosis = ChoiceArrayField(models.CharField(_("Patologie"), choices=Diagnosis.choices, max_length=25), blank=True,
                                 default=list)

    class Meta:
        ordering = ('name',)
        verbose_name = _("Membro famigliare")
        verbose_name_plural = _("Membri famigliari")

    def get_age(self):
        if self.birthday:
            return calculateAge(self.birthday)
        return 0

    def get_diagnosis(self):
        if self.diagnosis:
            return [Diagnosis(key).label for key in self.diagnosis]
            # return ','.join([Diagnosis(key).label for key in self.diagnosis])

    def __str__(self):
        return '%s - %s' % (self.name, self.birthday)


class EmployeeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__type=User.Types.EMPLOYEE)


class Employee(User):
    base_type = User.Types.EMPLOYEE
    objects = EmployeeManager()

    @property
    def more(self):
        return self.employeemore

    class Meta:
        proxy = True


class EmployeeMore(PersonMore):
    objects = EmployeeManager()

    class Meta:
        proxy = True
        verbose_name = _("Dipendente")
        verbose_name_plural = _("Dipendenti")

    def clean_employer(self):
        if not self.employer:
            raise ValidationError({'employer': _("Un dipendente deve avere un'azienda di riferimento.")},
                                  code='required')


class Company(TimeStampedModel, models.Model):
    id = models.UUIDField(primary_key=True, default=RandomUUID(), editable=False)
    code = models.CharField(_("Codice"), max_length=8, unique=True, null=None)
    name = models.CharField(_("Nome"), max_length=155)
    address = models.CharField(_("Indirizzo"), max_length=255)
    city = models.CharField(_("Città"), max_length=105)
    postcode = models.CharField(_("Codice postale"), max_length=5)
    referent = models.CharField(_("Referente"), max_length=55, blank=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    license_number = models.IntegerField(_("n. license"), default=100)

    class Meta:
        ordering = ('name',)
        verbose_name = _("Azienda")
        verbose_name_plural = _("Aziende")

    def __str__(self):
        return '%s - %s' % (self.name, self.code)

    @property
    def number_employees(self):
        """
        Method for getting the company's employees number
        :return: int total number
        """
        return self.employees.count()

    def get_random_code(self, length=8, chars=ascii_lowercase + digits, split=4, delimiter='-'):
        """
        Method for creating random company code.
        :param length: code lenght
        :param chars: chars type
        :param split: number of chars for delimiter
        :param delimiter: type delimiter
        :return: str code
        """
        code = ''.join([choice(chars) for i in range(length)])

        if split:
            code = delimiter.join([code[start:start + split] for start in range(0, len(code), split)])
        try:
            Company.objects.get(code=code)
            return self.get_random_code(length=length, chars=chars, split=split, delimiter=delimiter)
        except Company.DoesNotExist:
            return code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.get_random_code(split=None)
        super(Company, self).save(*args, **kwargs)
