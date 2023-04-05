import logging
import random
import string

from django.contrib.auth.models import AbstractUser, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

class User(AbstractUser):
    class Types(models.TextChoices):
        PERSON = "PERSON", _("Persona")
        EMPLOYEE = "EMPLOYEE", _("Dipendente")
        PRO = "PRO", _("Caregiver PRO")
        STAFF = "STAFF", _("STAFF")

    base_type = Types.PERSON

    """Default user for Lianecare."""
    type = models.CharField(_("Tipo"), max_length=50, choices=Types.choices, default=base_type)


    def get_absolute_url(self):
        """Get url for user's detail view."""
        return reverse("users:detail", kwargs={"username": self.username})

    def username_generator(self, size=4, chars=string.digits, name=string.ascii_lowercase):
        """ Method for generating username starting from first name and last name of user."""
        if self.first_name and self.last_name:
            username = self.first_name.lower() + self.last_name[:2].lower() + ''.join(
                random.choice(chars) for _ in range(size))
        else:
            username = ''.join(random.choice(name) for _ in range(8)) + ''.join(
                random.choice(chars) for _ in range(size))
        try:
            User.objects.get(username=username)
            return self.username_generator(size=4, chars=string.digits, name=string.ascii_lowercase)
        except User.DoesNotExist:
            return username

    @property
    def full_name(self):
        """Returns the person's full name."""
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def initials(self):
        """Returns the person's name initials."""
        return '%s%s' % (
            self.first_name[0].upper() if self.first_name else 'X',
            self.last_name[0].upper() if self.last_name else 'X')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = self.base_type if not self.type else self.type
            self.username = self.username_generator()
        super(User, self).save(*args, **kwargs)


# Signal: create profile user type and put in group
# @receiver(post_save, sender=User)
# def ensure_user_in_group(sender, **kwargs):
#      if kwargs.get('created', False):
#          user = kwargs.get('instance')
#          type_group, created = Group.objects.get_or_create(name=user.type)
#          user.groups.add(type_group)
