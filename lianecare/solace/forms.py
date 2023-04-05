from allauth.account.forms import SignupForm
from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import Textarea, TextInput, HiddenInput, \
    inlineformset_factory, formset_factory, NullBooleanSelect
from django.utils.translation import gettext_lazy as _
from django_select2.forms import Select2MultipleWidget

from .enums import GenderType, HowKnowUs, JobPostStatus
from .models import Person, Company, CaregiverPro, Service, CaregiverProMore, JobPost, Category, \
    SubCategory
from .models.people import FamilyMember, PersonMore
from lianecare.users.models import User


class PersonSignupForm(SignupForm):
    first_name = forms.CharField(label=_('Nome'), max_length=65,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label=_('Cognome'), max_length=65)
    city = forms.CharField(label=_("Città"), max_length=255)
    gender = forms.ChoiceField(label=_("Sesso"), choices=GenderType.choices, required=False)
    birthday = forms.DateField(label=_('Data di nascita'), localize=True)
    company_code = forms.CharField(label=_("Codice Azienda"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['city'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['gender'].widget.attrs.update({'class': 'form-control'})
        self.fields['company_code'].widget.attrs.update({'class': 'form-control'})

    def clean_company_code(self):
        company_code = self.cleaned_data["company_code"]
        if company_code:
            try:
                Company.objects.get(code=company_code)
            except Company.DoesNotExist:
                raise ValidationError(_("Il codice azienda non è valido"), code='invalid')
        return company_code

    def clean_first_name(self):
        return self.cleaned_data['first_name'].capitalize()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].capitalize()

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(PersonSignupForm, self).save(request)

        company = None
        company_code = self.cleaned_data['company_code']
        if company_code:
            company = Company.objects.get(code=company_code)
            user.type = User.Types.EMPLOYEE
            user.save(update_fields=['type'])

        type_group, created = Group.objects.get_or_create(name=user.type)
        user.groups.add(type_group)

        person = PersonMore.objects.create(user=user, city=self.cleaned_data['city'],
                                           gender=self.cleaned_data['gender'],
                                           birthday=self.cleaned_data['birthday'],
                                           employer=company)
        # Return the original result.
        return user


class PersonUpdateForm(forms.ModelForm):
    class Meta:
        model = PersonMore
        fields = ['photo', 'family_bio', 'city', 'postcode', 'region', 'country', 'latitude', 'longitude', 'address',
                  'house_number']
        widgets = {
            'address': TextInput(attrs={'class': 'form-control'}),
            'house_number': TextInput(attrs={'class': 'form-control'}),
            'city': HiddenInput(),
            'postcode': HiddenInput(),
            'latitude': HiddenInput(),
            'longitude': HiddenInput(),
            'region': HiddenInput(),
            'country': HiddenInput(),
            'family_bio': Textarea(
                attrs={'rows': 5, 'class': 'form-control',
                       'placeholder': 'Inserisci una breve descrizione della tua situaizone familiare'}),
        }


class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = ['name', 'gender', 'birthday', 'diagnosis']
        # localized_fields = ('birthday',)
        labels = {
            'diagnosis': _("Eventuali patologie"),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'gender': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            # 'birthday': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'},
            #                            format='%Y-%m-%d'),
            'birthday': forms.DateInput(
                attrs={'type': 'text', 'class': 'datepicker form-control', 'required': 'required',
                       'placeholder': 'gg/mm/aaaa'}),
            'diagnosis': Select2MultipleWidget,
        }


FamilyMemberFormSetInline = inlineformset_factory(Person, FamilyMember,
                                                  fields=('name', 'gender', 'birthday', 'diagnosis'),
                                                  form=FamilyMemberForm,
                                                  extra=0)


class PersonSettingsUpdateForm(forms.ModelForm):
    class Meta:
        model = PersonMore
        fields = ["notify_new_message", "notify_new_proposal"]


class CaregiverSignupForm(SignupForm):
    first_name = forms.CharField(label=_('Nome'), max_length=65)
    last_name = forms.CharField(label=_('Cognome'), max_length=65)
    address = forms.CharField(label=_("Indirizzo"), max_length=255,widget=forms.TextInput(attrs={
        'autocomplete':'false'
    }))
    house_number = forms.CharField(label=_("Civico"), max_length=10)
    gender = forms.ChoiceField(label=_("Sesso"), choices=GenderType.choices)
    birthday = forms.DateField(label=_('Data di nascita'), localize=True)
    how_know_us = forms.ChoiceField(label=_("Come ci hai conosciuto?"), choices=HowKnowUs.choices)
    phone = forms.CharField(label=_("Cellulare"), max_length=20)

    latitude = forms.CharField(widget=forms.HiddenInput())
    longitude = forms.CharField(widget=forms.HiddenInput())
    region = forms.CharField(widget=forms.HiddenInput())
    postcode = forms.CharField(widget=forms.HiddenInput())
    country = forms.CharField(widget=forms.HiddenInput())
    city = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['house_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['gender'].widget.attrs.update({'class': 'form-control'})
        self.fields['how_know_us'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})
        self.fields['birthday'].widget.attrs.update({'class': 'form-control'})

    def save(self, request):
        user = super(CaregiverSignupForm, self).save(request)
        user.type = User.Types.PRO
        user.save(update_fields=['type'])

        type_group, created = Group.objects.get_or_create(name=user.type)
        user.groups.add(type_group)

        pro = CaregiverProMore.objects.create(user=user,
                                              gender=self.cleaned_data['gender'],
                                              birthday=self.cleaned_data['birthday'],
                                              how_know_us=self.cleaned_data['how_know_us'],
                                              phone=self.cleaned_data['phone'],
                                              address=self.cleaned_data['address'],
                                              house_number=self.cleaned_data['house_number'],
                                              postcode=self.cleaned_data['postcode'],
                                              city=self.cleaned_data['city'],
                                              region=self.cleaned_data['region'],
                                              country=self.cleaned_data['country'],
                                              latitude=self.cleaned_data['latitude'],
                                              longitude=self.cleaned_data['longitude'])
        return user


class CaregiverSettingsUpdateForm(forms.ModelForm):
    class Meta:
        model = CaregiverProMore
        fields = ["notify_new_message", "notify_new_proposal"]


class CaregiverProUpdateForm(forms.ModelForm):
    class Meta:
        model = CaregiverProMore
        fields = ['phone', 'nationality', 'bio', 'photo', 'has_car', 'driving_license', 'is_graduate',
                  'is_certificated', 'is_smoker', 'first_aid', 'child_trainer', 'address', 'city', 'postcode', 'region',
                  'country', 'latitude', 'longitude', 'house_number']
        labels = {
            'has_car': _("Sei automunito?"),
            'driving_license': _("Hai la patente di guida?"),
            'is_smoker': _("Fumi?"),
            'is_graduate': _("Possiedi una laurea in ambito sanitario?"),
            'is_certificated': _("Possiedi una certificazione in ambito sanitario?"),
            'child_trainer': _("Sei un formatore ufficiale per l'infanzia?"),
            'first_aid': _("Hai un attestato di Primo Soccorso?"),
        }
        widgets = {
            'phone': TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'has_car': NullBooleanSelect(attrs={'class': 'form-control'}),
            'driving_license': NullBooleanSelect(attrs={'class': 'form-control'}),
            'is_graduate': NullBooleanSelect(attrs={'class': 'form-control'}),
            'is_certificated': NullBooleanSelect(attrs={'class': 'form-control'}),
            'is_smoker': NullBooleanSelect(attrs={'class': 'form-control'}),
            'child_trainer': NullBooleanSelect(attrs={'class': 'form-control'}),
            'first_aid': NullBooleanSelect(attrs={'class': 'form-control'}),
            'nationality': TextInput(attrs={'class': 'form-control'}),
            # 'birthday': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'},
            #                             format='%Y-%m-%d'),
            'address': TextInput(attrs={'class': 'form-control'}),
            'house_number': TextInput(attrs={'class': 'form-control'}),
            'city': HiddenInput(),
            'postcode': HiddenInput(),
            'region': HiddenInput(),
            'country': HiddenInput(),
            'latitude': HiddenInput(),
            'longitude': HiddenInput(),
            'bio': Textarea(
                attrs={'rows': 5, 'class': 'form-control',
                       'placeholder': 'Inserisci una breve descrizione di te. I profili con una descrizione hanno più possibilità di essere scelti.'}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['category', 'subcategories', 'price', 'max_distance', 'note', 'experience']

        widgets = {
            'price': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'max_distance': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
            'note': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'subcategories': forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
        }


class JobPostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        #values = JobPost.objects.filter(user=user,
            #status__in=[JobPostStatus.ACTIVE, JobPostStatus.NO_SHOW]).values_list('category__id', flat=True)
        super(JobPostForm, self).__init__(*args, **kwargs)
        #self.fields['category'].queryset = Category.objects.filter(active=True).exclude(id__in=list(values))
        self.fields['category'].queryset = Category.objects.filter(active=True)

    class Meta:
        model = JobPost
        fields = ['category', 'subcategories', 'when', 'note', 'has_references', 'experience', 'address', 'city',
                  'postcode', 'region', 'country', 'latitude', 'longitude', 'house_number']
        labels = {
            'category': _("Categoria"),
            'subcategories': _("Servizi"),
            'when': _("Quando?"),
            'note': _("Descrizione del Job Post"),
        }
        widgets = {
            'address': TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'house_number': TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'city': HiddenInput(),
            'postcode': HiddenInput(),
            'latitude': HiddenInput(),
            'longitude': HiddenInput(),
            'region': HiddenInput(),
            'country': HiddenInput(),
            'has_references': NullBooleanSelect(attrs={'class': 'form-control', 'required': 'required'}),
            'experience': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'when': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'required': 'required',
                                          'placeholder': 'Descrivi i servizi di cui necessiti e la persona che stai cercando.'}),
            'category': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'subcategories': forms.CheckboxSelectMultiple(attrs={'class': 'form-control', 'required': 'required'}),
        }


class JobPostUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(JobPostUpdateForm, self).__init__(*args, **kwargs)
        self.fields['subcategories'].queryset = SubCategory.objects.filter(active=True, parent=self.instance.category)

    class Meta:
        model = JobPost
        fields = ['category', 'subcategories', 'when', 'note', 'has_references', 'experience', 'address',
                  'house_number']
        labels = {
            'category': _("Categoria"),
            'subcategories': _("Servizi"),
            'when': _("Quando?"),
            'note': _("Descrizione accurata di ciò che si sta cercando"),
        }
        widgets = {
            'address': TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'house_number': TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'has_references': NullBooleanSelect(attrs={'class': 'form-control', 'required': 'required'}),
            'experience': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'when': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'required': 'required',
                                          'placeholder': 'Descrivi i servizi di cui necessiti e la persona che stai cercando.'}),
            'category': forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'subcategories': forms.CheckboxSelectMultiple(attrs={'class': 'form-control', 'required': 'required'}),
        }
