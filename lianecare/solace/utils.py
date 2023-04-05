import math
import os
from datetime import date
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models.service import JobPost, Service, Proposal
from lianecare.utils.helpers import send_mail_by_esp_template


def calculateAge(birthDate):
    today = date.today()
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
    return age


def getDistanceBetweenPoints(origin, destination):
    """
    Calculate the Haversine distance.

    Parameters
    ----------
    origin : tuple of float (lat, long)
    destination : tuple of float (lat, long)

    Returns: distance_in_km : float

    Examples
    --------
    >>> origin = (48.1372, 11.5756)  # Munich
    >>> destination = (52.5186, 13.4083)  # Berlin
    >>> round(distance(origin, destination), 1)
    504.2
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def create_proposals_from_services(jobpost_id, services_query):
    """Create Proposals for a Job Post and a list di CaregiverPro and return a list of new Proposal object.
    If a proposal already exists for a Caregiver, it will not be added to the list."""
    proposals = []
    for service in services_query:
        obj, created = Proposal.objects.get_or_create(
            jobpost_id=jobpost_id,
            caregiverpro_id=service.caregiver_id,
        )
        if created:
            proposals.append(obj)
    return proposals


def create_proposals_for_jobpost(jobpost_id, subcategories_pks):
    """Find possible Caregivers Pro for a new Job Post and create new proposals. Return the list of Proposal objects."""
    try:
        jobpost = JobPost.objects.get(id=jobpost_id)
        service_query = Service.objects.get_candidates_for_jobpost(jobpost, subcategories_pks)
        if service_query:
            proposals = create_proposals_from_services(jobpost_id, service_query)
            return proposals
    except JobPost.DoesNotExist:
        pass


def data_for_email_caregivers_new_proposals(proposals):
    ctx_email = {}
    to_list = []
    for proposal in proposals:
        caregiverpro = proposal.caregiverpro
        profile = caregiverpro.more
        if profile.notify_new_proposal:
            to_list.append(caregiverpro.email)
            jobpost = proposal.jobpost
            person = proposal.jobpost.user.more
            if person.photo:
                url_photo = os.path.join(settings.MEDIA_URL, person.photo['avatar'].url)
            else:
                url_photo = os.path.join(settings.MEDIA_URL, 'default-profile.png')
            ctx_email[caregiverpro.email] = {
                "firstName": caregiverpro.first_name,
                "jobPost_user": jobpost.user.first_name,
                "jobPost_user_photo_url": url_photo,
                "jobPost_category": jobpost.category.name,
                "jobPost_city": jobpost.city,
                "jobPost_note": jobpost.note[:335] + '...' if len(jobpost.note) > 335 else jobpost.note
            }
    return to_list, ctx_email


def create_email_for_employee(to, data):
    subject = render_to_string("solace/email/match_for_employee_subject.txt", data).strip()
    text_body = render_to_string("solace/email/match_for_employee_body.txt", data)
    html_body = render_to_string("solace/email/match_for_employee_body.html", data)

    msg = EmailMultiAlternatives(subject=subject, from_email=settings.DEFAULT_FROM_EMAIL,
                                 to=[to], body=text_body)

    msg.attach_alternative(html_body, "text/html")
    msg.tags = ["newProposaltoEmployee"]
    msg.track_opens = True
    msg.track_clicks = True
    return msg.send()


def send_email_new_private_message(to_user, to_user_email, from_user,
                                   cta_url="https://solace.lianecare.com/accounts/login/"):
    """Sends an email for new private messages."""
    ctx_email = {
        to_user_email: {
            "firstName": to_user,
            "from_user": from_user,
            "cta_url": cta_url
        }
    }
    template_id = "d-419c2a3f22cb4cb5820ab617f5bf53a9"
    tags = ["newMessage"]
    return send_mail_by_esp_template(to_user_email, ctx_email, template_id, tags=tags, track_opens=True,
                                     track_clicks=False)
