from django.contrib import admin
from lianecare.orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_email', 'product_description', 'amount_total', 'created']
    date_hierarchy = 'created'
    search_fields = ['user_email', 'user']
    list_filter = ('product_description',)

    def user_email(self, obj):
        return obj.user.email
