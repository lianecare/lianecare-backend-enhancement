import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import DetailView

from lianecare.courses.models import Course, Enrollment
from lianecare.quizes.models import Quiz, Question, Answer, Result
from lianecare.solace.models import CaregiverProMore


class QuizDetailView(DetailView):
    pass


@login_required
def quiz_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'quizes/quiz_detail.html', {'obj': quiz})


@login_required
def quiz_data_view(request, pk):
    quiz = Quiz.objects.get(pk=pk)
    questions = []
    for q in quiz.get_questions():
        answers = []
        for a in q.get_answers():
            answers.append(a.text)
        questions.append({str(q): answers})
    return JsonResponse({
        'data': questions,
    })


@login_required
def save_quiz_view(request, pk):
    if request.method == 'POST':
        questions = []
        data_ = json.loads(request.body.decode('utf-8'))
        # data_ = dict(data.lists())

        for k in data_.keys():
            question = Question.objects.get(text=k)
            questions.append(question)

        user = request.user
        quiz = Quiz.objects.select_related('course').get(pk=pk)
        course = quiz.course

        score = 0
        multipler = 100 / quiz.numbers_of_questions
        results = []
        correct_answer = None
        passed = False

        for q in questions:
            a_selected = data_.get(q.text)

            if a_selected != "":
                question_answers = Answer.objects.filter(question=q)
                for a in question_answers:
                    if a_selected == a.text:
                        if a.correct:
                            score += 1
                            correct_answer = a.text
                    else:
                        if a.correct:
                            correct_answer = a.text
                results.append({str(q): {'correct_answer': correct_answer, 'answered': a_selected}})
            else:
                results.append({str(q): 'not answered'})

        score_ = score * multipler
        if score_ >= quiz.minimum_score:
            passed = True

        Result.objects.create(quiz=quiz, user=user, score=score_, passed=passed)
        if passed:
            Enrollment.objects.filter(user=user, course=course).update(status=3)
            if course.type == Course.CourseTypes.BASIC:
                CaregiverProMore.objects.filter(user=user).update(has_basic_course=True)
            else:
                CaregiverProMore.objects.filter(user=user).update(has_pro_course=True)

        return JsonResponse(
            {'passed': passed, 'score': score_, 'corret_answers': score, 'number_answers': quiz.numbers_of_questions})
