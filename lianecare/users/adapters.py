from typing import Any
import json

from django.conf import settings
from django.http import HttpRequest
from django.contrib.sites.shortcuts import get_current_site

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from lianecare.utils.helpers import send_mail_by_esp_template


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        email = emailconfirmation.email_address.email
        to = [email] if isinstance(email, str) else email
        ctx = {
            email: {
                "firstName": emailconfirmation.email_address.user.first_name,
                "emailAccount": emailconfirmation.email_address.email,
                "activate_url": activate_url,
                "key": emailconfirmation.key,
            }
        }

        template_id = "d-4a5e3ff5d99647aabceec066b7d07d6e"
        tags = ["verifyEmail"]
        send_mail_by_esp_template(to, ctx, template_id, tags=tags, track_clicks=False)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
