from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Item, Order
import stripe
from rest_framework.decorators import api_view
from . import env


def cancel_pay(request):
    return render(request, 'payment/cancel.html')


def success_pay(request):
    return render(request, 'payment/success.html')

@api_view(['GET'])
def get_item(request, pk):
    item = Item.objects.get(pk=pk)
    return render(request, 'payment/get_item.html', {'item': item})


@api_view(['GET'])
def get_order(request, pk):
    order = Order.objects.get(pk=pk)
    items = Item.objects.filter(order__id=pk)
    return render(request, 'payment/get_order.html', {'order': order, 'items': items})


def items_list(request):
    items = Item.objects.all()
    return render(request, 'payment/home.html', {'items': items})

@csrf_exempt
@api_view(['GET'])
def buy_item(request, pk):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000'
        item = Item.objects.get(id=pk)
        stripe.api_key = env.api_key
        try:

            checkout_session = stripe.checkout.Session.create(


                mode='payment',
                success_url=domain_url + '/success',
                cancel_url=domain_url + '/cancel',
                line_items=[
                    {
                        'price': item.stripe_price_id,
                        'quantity': 1,

                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
@api_view(['GET'])
def buy_order(request, pk):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000'
        items = Item.objects.filter(order__id=pk)
        line_items = []
        for item in items:
            line_items.append(
                {'price': item.stripe_price_id,
                'quantity': 1,}
            )
        stripe.api_key = env.api_key
        try:

            checkout_session = stripe.checkout.Session.create(


                mode='payment',
                success_url=domain_url + '/success',
                cancel_url=domain_url + '/cancel',
                line_items=line_items
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


