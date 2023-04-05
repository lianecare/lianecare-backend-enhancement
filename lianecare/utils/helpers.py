from django.conf import settings
from django.core.mail import EmailMessage


def send_mail_by_esp_template(to, data, template_id, **kwargs):
    to_list = [to] if isinstance(to, str) else to
    message = EmailMessage(
        subject=None,  # use the subject in our stored template
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to_list)
    message.template_id = template_id
    message.track_opens = kwargs.get('track_opens', True)
    message.track_clicks = kwargs.get('track_clicks', True)
    message.tags = kwargs.get('tags', None)
    message.merge_data = data
    message.merge_global_data = kwargs.get('global_data', None)

    return message.send()
