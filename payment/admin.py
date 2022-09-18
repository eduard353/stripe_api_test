from django.contrib import admin

from .models import Item, Order, Discount, Tax  # , Currency


# admin.site.register(Item)
# admin.site.register(Order)
# admin.site.register(Discount)
# admin.site.register(Tax)
# admin.site.register(Currency)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stripe_item_id', 'stripe_price_id')
    list_filter = ('name', 'price')
    search_fields = ('name', 'price')
    ordering = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id',)
    list_filter = ('id',)
    search_fields = ('id',)
    ordering = ('id',)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'percent')
    list_filter = ('name', 'percent')
    search_fields = ('name', 'percent')
    ordering = ('name',)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'percentage')
    list_filter = ('display_name', 'percentage')
    search_fields = ('display_name', 'percentage')
    ordering = ('display_name',)
