import logging
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from django.conf import settings

logger = logging.getLogger(__name__)


# Create your models here.
class Order(TimeStampedModel, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Stripe part
    session_stripe_id = models.CharField(_("STRIPE SESSION ID"), max_length=255, unique=True, null=True, default=None)
    payment_intent_stripe_id = models.CharField(_("STRIPE PAYMENT ID"), max_length=255, unique=True, null=True, default=None)
    customer_stripe_id = models.CharField(_("STRIPE CUSTOMER ID"), max_length=255, null=True, default=None)
    product_stripe_id = models.CharField(_("STRIPE PRODUCT ID"), max_length=255, blank=True, null=True, default=None)
    product_description = models.CharField(_("Descrizione"), max_length=255, blank=True, null=True, default=None)
    subscription_stripe_id = models.CharField(_("STRIPE SUBSCRIPTION ID"), max_length=255, blank=True, null=True, default=None)
    price_stripe_id = models.CharField(_("STRIPE PRICE ID"),max_length=255, blank=True, default=None, null=True)
    amount_total = models.IntegerField(_("Totale"), default=0)
    amount_subtotal = models.IntegerField(_("Subtotale"), default=0)
    # Product
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': ('course', 'membership')})
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created']
        verbose_name = _("Ordine")
        verbose_name_plural = _("Ordini")
