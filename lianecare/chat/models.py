from django.core.exceptions import ValidationError
from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _

from django.conf import settings


# Create your models here.
class Message(TimeStampedModel, models.Model):
    class MessStatus(models.IntegerChoices):
        NO_READ = 0, _('Non letto')
        READ = 1, _('Letto')

    proposal = models.ForeignKey('solace.Proposal', on_delete=models.CASCADE, related_name="chat")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+", null=True, blank=True,
                           default=None)
    msg = models.TextField(_("Messaggio"))
    status = models.CharField(choices=MessStatus.choices, max_length=55, default=MessStatus.NO_READ)

    def __str__(self):
        return "Messaggio di %s per %s" % (self.sender, self.to)

    class Meta:
        ordering = ('created',)

    def clean(self):
        if self.to:
            if self.sender == self.to:
                raise ValidationError(_('The sender and the recipient can not be the same person.'))
