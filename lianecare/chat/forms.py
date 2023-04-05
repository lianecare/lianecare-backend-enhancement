from django import forms
from django.forms import HiddenInput
from django.utils.translation import gettext_lazy as _

from lianecare.chat.models import Message


class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['msg']
        widgets = {
            'msg': forms.Textarea(attrs={'rows': 5, 'maxlength': 300, 'class': 'form-control', 'required': 'required',
                                         'placeholder': _('Inserisci qui il tuo messaggio')}),
        }
