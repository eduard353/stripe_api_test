from django.db import models
from . import env
import stripe


stripe.api_key = env.api_key

class Item(models.Model):
    stripe_item_id = models.CharField(max_length=100, default='', editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=100, default='', editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        item = stripe.Product.create(name=self.name, description=self.description)
        price = stripe.Price.create(
            unit_amount=self.price * 100,
            currency="usd",
            product=item.id,

        )
        self.stripe_item_id = item.id
        self.stripe_price_id = price.id
        super().save(*args, **kwargs)


    def delete(self):
        try:
            stripe.Product.modify(self.stripe_item_id, active=False)
        except Exception as e:
            print(e)
            print('Не удалось перевести в архив продукт: ', self.name)
        super().delete()

    class Meta:

        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Order(models.Model):

    items = models.ManyToManyField(Item)

    def __str__(self):
        return str(self.pk)

    class Meta:

        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
