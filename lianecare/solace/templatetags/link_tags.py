from django.template import Library
from django.urls     import reverse
from django.conf import settings

register = Library()

@register.simple_tag(takes_context = True)
def fullURL(context, name, *args, **kwargs):
    return f'{settings.SOLACE_BASEURL}{reverse(name, args = args, kwargs = kwargs)}'
