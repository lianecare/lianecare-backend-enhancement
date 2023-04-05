from django.contrib import admin
from lianecare.quizes.models import Result, Quiz, Answer, Question


# admin.site.register(Quiz)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ['text', 'quiz_name']
    search_fields = ['text']
    list_filter = ('quiz__name',)

    def quiz_name(self, obj):
        return "\n".join([p.name for p in obj.quiz.all()])


admin.site.register(Question, QuestionAdmin)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_select_related = ('user',)
    list_display = ['quiz', 'user', 'user_email', 'score', 'passed']
    #readonly_fields = ['quiz', 'user', 'score', 'passed']
    list_filter = ('quiz', 'score', 'passed')
    search_fields = ['user__username', 'user__email']
    list_display_links = None

    def user_email(self, obj):
        return obj.user.email


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'numbers_of_questions', 'minimum_score']
    list_filter = ('course', 'minimum_score')
    search_fields = ['name', 'user__email']

    def user_email(self, obj):
        return obj.user.email
