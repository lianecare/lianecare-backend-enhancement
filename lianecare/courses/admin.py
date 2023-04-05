from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from .models import Course, Module, Enrollment, EnrollmentStatus


# Register your models here.
class ModuleInline(SortableInlineAdminMixin, admin.StackedInline):
    model = Module
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'sequence', 'n_modules', 'price', 'type', 'is_active', 'is_salable', 'created', 'course_offer']
    search_fields = ['title', 'overview']
    list_filter = ('type', 'is_active')
    list_editable = ['price', 'sequence', 'is_active', 'is_salable', 'type']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]


class EnrollmentStatusInline(admin.TabularInline):
    model = EnrollmentStatus
    readonly_fields = ('module', 'order', 'viewed')
    extra = 0


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'course', 'created', 'status', 'get_progress']
    search_fields = ['user_email', 'overview']
    list_filter = ('course', 'status')
    readonly_fields = ('order', 'session_stripe_id')

    inlines = [EnrollmentStatusInline]

    def user_email(self, obj):
        return obj.user.email
