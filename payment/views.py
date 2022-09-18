from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Item, Order, Discount, Tax
import stripe
from rest_framework.decorators import api_view
from . import env


def cancel_pay(request):
    return render(request, 'payment/cancel.html')


def success_pay(request):
    return render(request, 'payment/success.html')


@api_view(['GET'])
def get_item(request, pk):
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        return render(request, 'payment/404.html')
    return render(request, 'payment/get_item.html', {'item': item})


@api_view(['GET'])
def get_order(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return render(request, 'payment/404.html')
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
        line_items = []
        discounts = []
        tax = False
        try:
            order = Order.objects.get(pk=pk)
            if order.coupon:
                discount = Discount.objects.get(pk=order.coupon_id)
                discounts.append({'coupon': discount.stripe_coupon_id, })
            if order.tax:
                tax = Tax.objects.get(pk=order.tax_id)
        except Order.DoesNotExist:
            return render(request, 'payment/404.html')

        items = Item.objects.filter(order__id=pk)

        for item in items:
            data = {'price': item.stripe_price_id, 'quantity': 1, }
            if tax:
                data['tax_rates'] = [tax.stripe_tax_id]
            line_items.append(
                data
            )
        stripe.api_key = env.api_key
        try:

            checkout_session = stripe.checkout.Session.create(

                mode='payment',
                success_url=domain_url + '/success',
                cancel_url=domain_url + '/cancel',
                line_items=line_items,
                discounts=discounts,

            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})
