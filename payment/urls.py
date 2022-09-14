from django.urls import path
from . import views


urlpatterns = [
    path('item/<int:pk>', views.get_item, name='get_item'),
    path('buy/<int:pk>', views.buy_item, name='buy_item'),
    path('success', views.success_pay, name='success_pay'),
    path('cancel', views.cancel_pay, name='cancel_pay'),

    path('', views.items_list, name='items_list'),

]