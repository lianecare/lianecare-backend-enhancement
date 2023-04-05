from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView, RedirectView
from rest_framework.authtoken.views import obtain_auth_token


from lianecare.solace.views import HomePageView

urlpatterns = [
    #path("", TemplateView.as_view(template_name="pages/coming-soon.html"), name="home"),
    path("", HomePageView.as_view(), name='home'),
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("images/favicons/lianecare-favicon-32x32.png")),),
    path("privacy-policy/", TemplateView.as_view(template_name="pages/privacy-policy.html"), name="privacy-policy"),
    path("consenso-informato/", TemplateView.as_view(template_name="pages/consenso-informato.html"), name="consenso-informato"),
    path("cookie-policy/", TemplateView.as_view(template_name="pages/cookie-policy.html"), name="cookie-policy"),
    path("termini-condizioni/", TemplateView.as_view(template_name="pages/terms-conditions.html"), name="terms-conditions"),
    path("chi-siamo/", TemplateView.as_view(template_name="pages/chi-siamo.html"), name="chi-siamo"),
    path("template/", TemplateView.as_view(template_name="pages/template.html"), name="template"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("lianecare.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path("exports/", include("lianecare.exports.urls")),
    path("", include("lianecare.solace.urls", namespace="solace")),
    path("corsi/", include("lianecare.courses.urls", namespace="courses")),
    path("abbonamenti/", include("lianecare.memberships.urls", namespace="memberships")),
    path("ordini/", include("lianecare.orders.urls", namespace="orders")),
    path("test/", include("lianecare.quizes.urls", namespace="quizes")),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/v1/", include("config.api_router", namespace="api")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
    # Select2
    path("select2/", include("django_select2.urls")),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
