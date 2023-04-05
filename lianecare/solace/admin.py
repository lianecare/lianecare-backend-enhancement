from django.contrib import admin
from lianecare.users.models import User
# Register your models here.
from lianecare.solace.models.professionals import CaregiverProMore, CaregiverPro
from lianecare.solace.models.people import Company, PersonMore, FamilyMember, Person, EmployeeMore, Employee
from lianecare.solace.models.service import Category, SubCategory, Service, JobPost, Proposal


# admin.site.site_title = "Solace administration"
# admin.site.site_header = "Solace Backend"


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', ]
    inlines = [SubCategoryInline, ]


class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1


@admin.register(EmployeeMore)
class EmployeeMoreAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    list_display = ['user_full_name', 'user_email', 'gender', 'birthday', 'city', 'postcode', 'employer',
                    'has_basic_course', 'has_pro_course']
    search_fields = ['user__first_name', 'user__last_name']
    list_filter = ('city', 'gender', 'employer')

    # inlines = [FamilyMemberInline, ]

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'

    def user_full_name(self, obj):
        return ("%s %s" % (obj.user.first_name, obj.user.last_name)).capitalize()

    user_full_name.short_description = 'Nome completo'


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    exclude = ('code',)  # esclude il campo dalla form di modifica
    list_display = ['name', 'number_employees', 'code', 'license_number', 'city', 'referent', 'email']
    search_fields = ['name', 'city']
    list_filter = ('city',)
    ordering = ('name',)
    # inlines = (EmployeeMoreInline,)

    # list_display_links = ('first_name', 'last_name') # elementi che si possono cliccare per passare alla modifica
    # list_editable = () campi editabili al volo es booleani
    # date_hierarchy = 'created'

    # the url and title fields will display on the same line and the content
    # field will be displayed below them on its own line
    # fields = (('url', 'title'), 'content')

    # fieldsets = (
    #     (None, {
    #         'fields': (('url', 'title'), 'content', 'sites')
    #         'classes': ('wide', 'extrapretty'),
    #          'description': 'Testo esplicativo del fieldset',
    #     }),
    #     ('Advanced options', {
    #         'classes': ('collapse',),
    #         'fields': ('registration_required', 'template_name'),
    #     }),
    # )


class ServiceInline(admin.StackedInline):
    model = Service
    extra = 1


class CaregiverProMoreInline(admin.StackedInline):
    model = CaregiverProMore
    extra = 1


@admin.register(CaregiverProMore)
class CaregiverProMoreAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    exclude = ('availability',)
    list_display = ['upper_case_name', 'user_email', 'identity_checked' ,'gender', 'birthday', 'nationality', 'city', 'has_basic_course',
                    'has_pro_course', 'how_know_us']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    list_filter = ('city', 'gender','how_know_us')
    list_editable = ['identity_checked']
    list_per_page = 10
    fieldsets = (
        ('Dati personali', {
            'fields': ('user', 'gender', 'birthday', 'phone', 'nationality', 'bio', 'photo', 'how_know_us')
        }),
        ('Indirizzo', {
            'classes': ('collapse',),
            'fields': (
                ('address', 'house_number', 'city', 'postcode'),
                ('region', 'country'),
                ('latitude', 'longitude')),
        }),
        ('Abilità', {
            'classes': ('collapse',),
            'fields': (
                'has_car', 'driving_license', 'is_graduate', 'is_certificated', 'is_smoker', 'first_aid',
                'child_trainer',
                'identity_checked'),
        }),
        ('Corsi', {
            'classes': ('collapse',),
            'fields': (
                'has_basic_course', 'has_pro_course',),
        }),
    )

    def user_email(self, obj):
        return obj.user.email

    def upper_case_name(self, obj):
        return ("%s %s" % (obj.user.first_name, obj.user.last_name)).capitalize()

    upper_case_name.short_description = 'Nome completo'


class ProposalInline(admin.TabularInline):
    model = Proposal
    extra = 0



@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    search_fields = ['city']
    list_filter = ('is_active', 'status')
    list_display = ['jobid', 'user_email', 'category', 'city', 'when', 'experience', 'has_references', 'is_active', 'status',
                    'number_candidates']
    list_per_page = 10

    def user_email(self, obj):
        return obj.user.email
    def jobid(self, obj):
        try:
            return obj.pk
        except:
            return None


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['jobid', 'jobpost', 'caregiverpro', 'category', 'city', 'status_caregiverpro', 'status_employee']
    search_fields = ['caregiverpro__email', 'jobpost__user__email', 'jobpost__pk']
    list_filter = ('status_caregiverpro',)
    list_per_page = 10
    def category(self, obj):
        try:
            return obj.jobpost.category
        except:
            return None
    def city(self, obj):
        try:
            return obj.jobpost.city
        except:
            return None
    def jobid(self, obj):
        try:
            return obj.jobpost.pk
        except:
            return None
