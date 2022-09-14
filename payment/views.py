from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Item
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


def items_list(request):
    items = Item.objects.all()
    return render(request, 'payment/home.html', {'items': items})

@csrf_exempt
@api_view(['GET'])
def buy_item(request, pk):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000'
        price = Item.objects.get(id=pk)
        stripe.api_key = env.api_key
        try:

            checkout_session = stripe.checkout.Session.create(


                mode='payment',
                success_url=domain_url + '/success',
                cancel_url=domain_url + '/cancel',
                line_items=[
                    {
                        'price': price.stripe_price_id,
                        'quantity': 1,

                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


