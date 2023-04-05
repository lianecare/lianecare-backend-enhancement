from braces.views import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView

from lianecare.courses.models import Course, Module, Enrollment, EnrollmentStatus
from django.utils.translation import gettext_lazy as _

# class OwnerCourseMixin(LoginRequiredMixin, PermissionRequiredMixin):
#     model = Course
#     fields = ['subject', 'title', 'slug', 'overview']
#     success_url = reverse_lazy('courses:course_list')
#     permission_required = 'courses.view_course'
from lianecare.quizes.models import Quiz, Result


class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class CourseListView(LoginRequiredMixin, ListView):
    template_name = 'courses/course_list.html'
    model = Course

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True, user_type = self.request.user.type)


class CourseDetailView(LoginRequiredMixin, DetailView):
    template_name = 'courses/course_detail.html'
    model = Course

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True, user_type = self.request.user.type)

    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()
        first_module = EnrollmentStatus.objects.filter(enrollment__user=request.user, enrollment__course=object).first()

        if first_module:
            return redirect("solace:student_module_detail", first_module.uuid)  # chiama la reverse
            # return redirect(first_module) # senza get_absolute_url non funziona
            # reverse("solace:person_detail", kwargs={"username": user.username})
        else:
            return super(CourseDetailView, self).dispatch(request, *args, **kwargs)


class ModuleDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
    template_name = 'courses/module_detail.html'
    model = Module
    raise_exception = True
    permission_denied_message = _("Non sei autorizzato a vedere il contenuto richiesto.")

    def test_func(self, user):
        """Verifica se l'utente è iscritto al corso e quindi abilitato a visionare il contenuto del modulo."""
        object = self.get_object()
        return Enrollment.objects.filter(user=user, course=object.course).first()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_modules'] = Module.objects.filter(course=self.object.course, is_active=True)
        return context

        # subjects = cache.get('all_subjects')
        # if not subjects:
        #     subjects = Subject.objects.annotate(total_courses=Count('courses'))
        #     cache.set('all_subjects', subjects)


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/my_courses_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        enroll_courses_list = Enrollment.objects.filter(user=self.request.user).values_list('course__id', flat=True)
        return qs.filter(id__in=enroll_courses_list)


class StudentModuleDetailView(LoginRequiredMixin, DetailView):
    template_name = 'courses/my_module_detail.html'
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    model = EnrollmentStatus
    raise_exception = True
    permission_denied_message = _("Non sei autorizzato a vedere il contenuto richiesto.")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(enrollment__user__in=[self.request.user]).select_related('module', 'enrollment',
                                                                                  'enrollment__course')

    # def test_func(self, user):
    #     """Verifica se l'utente è iscritto al corso e quindi abilitato a visionare il contenuto del modulo."""
    #     object = self.get_object()
    #     return user == object.enrollment.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.object.enrollment
        quiz = Quiz.objects.filter(course=enrollment.course).first()
        if quiz:
            check_test_user = Result.objects.filter(user=self.request.user, quiz=quiz, passed=True)
            context['test_passed'] = True if check_test_user else False

        context['quiz'] = quiz
        context['enrolled_modules'] = EnrollmentStatus.objects.filter(enrollment=enrollment).select_related('module')
        return context


@login_required()
def StudentModuleViewed(request, uuid):
    modules_list = EnrollmentStatus.objects.filter(enrollment__user__in=[request.user])

    en_status = get_object_or_404(modules_list, uuid=uuid)
    en_status.viewed = True
    en_status.save()

    enrollment = en_status.enrollment

    next_module = modules_list.filter(enrollment=enrollment, viewed=False).exclude(uuid=en_status.uuid).first()

    if next_module:
        if enrollment.status == 0:
            enrollment.status = 1
            enrollment.save()
        return redirect("solace:student_module_detail", next_module.uuid)
    else:
        if enrollment.status != 3:
            enrollment.status = 2
            enrollment.save()
        return redirect("solace:student_module_detail", en_status.uuid)


@login_required
def free_enroll(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        if course_id:
            course = Course.objects.get(pk=course_id)
            object, create = Enrollment.objects.get_or_create(user=request.user, course=course)
            return redirect("courses:course_detail", course.slug)
            # return redirect(course)
    else:
        return reverse("courses:course_list")
