from django.db import models
from django.utils.translation import gettext_lazy as _


class UserTypes(models.TextChoices):
    PERSON = "PERSON", _("Persona")
    EMPLOYEE = "EMPLOYEE", _("Dipendente")
    PRO = "PRO", _("Caregiver PRO")


class CareNeed(models.TextChoices):
    CHILD = 'CHILD', _('Babysitter')
    CLEANING = 'CLEANING', _('House cleaning')
    COMPANION = 'COMPANION', _('Companion care')
    COOKING = 'COOKING', _('Cooking/Meal preparation')
    # CRAFT = 'CRAFT', _('Crafts')
    ERRANDS = 'ERRANDS', _('Groceries/Errands')
    HOUSE = 'HOUSE', _('Small household chores')
    LANGUAGE = 'LANGUAGE', _('Remote language support')
    # LAUNDRY = 'LAUNDRY', _('Organizing/Laundry')
    # MOVING = 'MOVING', _('Packing/Moving')
    PETS = 'PETS', _('Pet sitter')
    TUTORING = 'TUTORING', _('Remote tutoring')


class StudyType(models.TextChoices):
    MIDDLE = 'MIDDLE', _('Scuola Media')
    DIPLOMA = 'DIPLOMA', _('Diploma Superiore')
    DEGREE = 'DEGREE', _('Laurea Triennale')
    MDEGREE = 'MDEGREE', _('Laurea Specialistica')
    MASTERI = 'MASTERI', _('Master I Livello')
    MASTERII = 'MASTERII', _('Master II Livello')
    SPECIALIZATION = 'SPECIALIZATION', _('Corso di specializzazione')
    OTHER = 'OTHER', _('Altre qualifiche')
    PhD = 'PHD', _('Dottorato di ricerca')


class GenderType(models.TextChoices):
    __empty__ = ''
    FEMALE = 'FEMALE', _('Femmina')
    MALE = 'MALE', _('Maschio')
    # ND = 'ND', _('Not specified')


class Answer(models.IntegerChoices):
    NO = 0, _('No')
    YES = 1, _('Yes')
    __empty__ = _('Seleziona')


class HowKnowUs(models.TextChoices):
    __empty__ = ''
    GOOGLE = 'GOOGLE', _('Google')
    YOUTUBE = 'YOUTUBE', _('Youtube')
    FORUM = 'FORUM', _('Gruppi o Forum')
    FACEBOOK = 'FACEBOOK', _('Facebook')
    LINKEDIN = 'LINKEDIN', _('Linkedin')
    BANNERAD = 'BANNER', _('Banner Ads')
    FRIENDS = 'FRIENDS', _('Amici e Famiglia')
    PRESS = 'PRESS', _('Press: News, Magazine, Blog')
    FLYER = 'FLYER', _('volantino')
    OTHER = 'OTHER', _('Altro')


class Diagnosis(models.TextChoices):
    __empty__ = ''
    OTHER = 'OTHER', _('Altro')
    FOOD_ALLERGIES = 'FOOD_ALLERGIES', _('Allergie alimentari')
    ASTHMA = 'ASTHMA', _('Asma')
    ASPER = 'ASPERGERS', _('Aspergers')
    AUTISM = 'AUTISM', _('Autismo')
    CANCER = 'CANCER', _('Cancro')
    BLINDNESS = 'BLINDNESS', _('Cecità / Deficit visivo')
    CELIAC = 'CELIAC', _('Celiachia')
    SEIZURE = 'SEIZURE', _('Crisi convulsive')
    DIABETES = 'DIABETES', _('Diabete')
    DYSLEXIA = 'DYSLEXIA', _('Dislessia')
    MUSCOLAR_DYSTROPHY = 'MUSCOLAR_DYSTROPHY', _('Distrofia muscolare')
    HEART_DEFECTS = 'HEART_DEFECTS', _('Disturbi cardiaci')
    MOBILITY_CHALLENGES = 'MOBILITY_CHALLENGES', _('Disturbi motori')
    SENSORY_DISORDER = 'SENSORY_DISORDER', _('Disturbi sensoriali')
    ADHD = 'ADHD', _("Disturbo da deficit dell'attenzione e iperattività (ADHD)")
    EPILEPSY = 'EPILEPSY', _('Epilessia')
    CYSTIC_FIBROSIS = 'CYSTIC_FIBROSIS', _('Fibrosi cistica')
    MENTAL_ILLNESS = 'MENTAL_ILLNESS', _('Malattia mentale')
    DWARFISM = 'DWARFISM', _('Nanismo')
    OBESITY = 'OBESITY', _('Obesità')
    CEREBRAL_PALSY = 'CEREBRAL_PALSY', _('Paralisi cerebrale')
    DEVELOPMENT_DELAYS = 'DEVELOPMENT_DELAYS', _('Ritardo nello sviluppo')
    SPEECH_DELAY = 'SPEECH_DELAY', _('Ritardo nel parlato')
    SCLEROSIS = 'SCLEROSIS', _('Sclerosi Multipla')
    FETAL_SYNDROME = 'FETAL_SYNDROME', _('Sindrome alcolica fetale')
    DOWN = 'DOWN', _('Sindrome di Down')
    DEAFNESS = 'DEAFNESS', _('Sordità')


class WhenJobPost(models.IntegerChoices):
    ZERO = 0, _("indifferente")
    # DAY = 1, _('Il prima possibile')
    WEEK = 7, _("entro 7 gg")
    TWO_WEEKS = 14, _("entro 14 gg")
    MONTH = 30, _("entro 30 gg")
    __empty__ = _('Seleziona')


class ExperienceYears(models.IntegerChoices):
    ZERO = 0, _("Indifferente")
    THREE = 3, _('+3 anni')
    FIVE = 5, _("+5 anni")
    TEN = 10, _("+10 anni")
    __empty__ = _('Seleziona')


class JobPostStatus(models.TextChoices):
    __empty__ = ''
    NO_SHOW = 'NO_SHOW', _('Non visibile')
    ACTIVE = 'ACTIVE', _('Pubblicato')
    KO_DELETE = 'DELETE', _('Non voglio dirlo')
    KO_DONT_NEED = 'KO_NO_NEED', _('Non ne ho più bisogno')
    KO_OTHER_PLATFORM = 'KO_OTHER_PLATFORM', _('Ho trovato un Caregiver con altre piattaforme')
    KO_OTHER = 'KO_OTHER', _('Ho trovato il Caregiver in altro modo')
    OK_SOLACE = 'OK_SOLACE', _('Ho trovato il Caregiver con LianeCare')


class ProposalStatus(models.IntegerChoices):
    DELETE = -4, _('Eliminato')
    EXPIRED = -3, _('Scaduto')
    REFUSED = -2, _('Rifiutato')
    IGNORED = -1, _('Ignorato')
    PROPOSED = 0, _('Proposto')
    CHAT = 1, _('Chat')
    APPROVED = 2, _('Approvato')
    REVIEWED = 3, _('Recensito')
