import logging
from config import celery_app

logger = logging.getLogger(__name__)


@celery_app.task()
def find_candidates_for_jobpost_and_send_email(jobpost_id, subcategories_pks):
    from .utils import create_email_for_employee
    from .utils import create_proposals_for_jobpost
    from .utils import data_for_email_caregivers_new_proposals
    from lianecare.utils.helpers import send_mail_by_esp_template

    """Task to find possible Caregivers Pro for a new Job Post and then to create new proposals."""

    list_proposals = create_proposals_for_jobpost(jobpost_id, subcategories_pks)
    if list_proposals:
        # Send email to caregivers by SendGrid
        to_list, ctx_email = data_for_email_caregivers_new_proposals(list_proposals)
        if to_list:
            template_id = "d-dc68a15267f64fa49c3a2c361bfe88b6"
            tags = ["newProposaltoCaregiver"]
            sent_mail_caregiver = send_mail_by_esp_template(to_list, ctx_email, template_id, tags=tags)

        # Send email to employee by Django
        if list_proposals[0].jobpost.user.more.notify_new_proposal:
            data = {
                'proposals': list_proposals,
            }
            employee_email = list_proposals[0].jobpost.user.email
            sent_mail_employee = create_email_for_employee(employee_email, data)


@celery_app.task()
def notify_user_for_new_message(to_user, to_user_email, from_user, cta_url):
    from .utils import send_email_new_private_message
    send_email_new_private_message(to_user, to_user_email, from_user, cta_url)
