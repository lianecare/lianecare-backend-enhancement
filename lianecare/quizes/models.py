import random
from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# Create your models here.
from lianecare.courses.models import Course


class Quiz(TimeStampedModel, models.Model):
    name = models.CharField(_("Nome"), max_length=120)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    numbers_of_questions = models.IntegerField(_("Numero domande"))
    minimum_score = models.IntegerField(help_text=_("Punteggio minimo per passare"))

    class Meta:
        verbose_name_plural = _('Quizes')
        ordering = ('created',)

    def __str__(self):
        return f"{self.name}"

    def get_questions(self):
        questions = list(self.question_set.all())
        random.shuffle(questions)
        return questions[:self.numbers_of_questions]


class Question(TimeStampedModel, models.Model):
    text = models.CharField(max_length=255)
    quiz = models.ManyToManyField(Quiz)

    def __str__(self):
        return str(self.text)

    def get_answers(self):
        return self.answers.all()

    class Meta:
        verbose_name = _('Domanda')
        verbose_name_plural = _('Domande')


class Answer(TimeStampedModel, models.Model):
    text = models.TextField()
    correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')

    def __str__(self):
        return "Domanda: %s, Risposta: %s, Corretta: %s" % (self.question.text, self.text, self.correct)

    class Meta:
        verbose_name = _('Risposta')
        verbose_name_plural = _('Risposte')


class Result(TimeStampedModel, models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.FloatField(_("Punteggio"))
    passed = models.BooleanField(_("Superato?"), default=False)

    def __str__(self):
        return "%s, %s, Esito: %s" % (self.user.email, self.quiz.name, self.passed)

    class Meta:
        verbose_name = _('Esito test')
        verbose_name_plural = _('Esiti test')
