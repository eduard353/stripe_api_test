from django.db import models
import stripe
from django.core.validators import MaxValueValidator, MinValueValidator
import os

stripe.api_key = os.getenv("STRIPE_API_KEY")


class Item(models.Model):
    stripe_item_id = models.CharField(max_length=100, default='', editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0), ])
    stripe_price_id = models.CharField(max_length=100, default='', editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Переопределяем метод для автоматического создание объектов в Stripe
        if self.stripe_item_id == '':
            item = stripe.Product.create(name=self.name, description=self.description)
            price = stripe.Price.create(
                unit_amount=int(self.price * 100),
                currency='usd',
                product=item.id,
            )
            self.stripe_item_id = item.id

        else:
            # Если объект уже существует, то изменяем его, а не создаем новый
            stripe.Price.modify(self.stripe_price_id, active=False)
            price = stripe.Price.create(
                unit_amount=int(self.price * 100),
                product=self.stripe_item_id,
            )
            stripe.Product.modify(
                self.stripe_item_id,
                name=self.name,
                description=self.description,
                default_price=price.id
            )
        self.stripe_price_id = price.id
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # При удалении объекта в Stripe делаем его архивным
        try:
            stripe.Product.modify(self.stripe_item_id, active=False)
        except Exception as e:
            print(e)
            print('Не удалось перевести в архив продукт: ', self.name)
        super().delete()

    class Meta:

        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Tax(models.Model):
    display_name = models.CharField(max_length=200)
    inclusive = models.BooleanField(default=True)
    percentage = models.DecimalField(max_digits=3, decimal_places=1,
                                     validators=[MaxValueValidator(100), MinValueValidator(0)])
    stripe_tax_id = models.CharField(max_length=100, default='', editable=False)

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        # Переопределяем метод для автоматического создание объектов в Stripe
        # Если мы изменяем Налог, то сатрый варинт делаем архивным и создаем новый
        if self.stripe_tax_id != '':
            stripe.TaxRate.modify(
                self.stripe_tax_id,
                active=False,
            )
        tax = stripe.TaxRate.create(display_name=self.display_name,
                                    percentage=self.percentage,
                                    inclusive=self.inclusive, )

        self.stripe_tax_id = tax.id

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            stripe.TaxRate.modify(self.stripe_tax_id, active=False)
        except Exception as e:
            print(e)
            print('Не удалось перевести в архив Налог: ', self.display_name)
        super().delete()

    class Meta:

        verbose_name = "Налог"
        verbose_name_plural = "Налоги"


class Discount(models.Model):
    name = models.CharField(max_length=200)
    percent = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)])
    stripe_coupon_id = models.CharField(max_length=100, default='', editable=False)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.stripe_coupon_id != '':
            stripe.Coupon.delete(self.stripe_coupon_id)
        coupon = stripe.Coupon.create(percent_off=self.percent, duration="once")
        self.stripe_coupon_id = coupon.id
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            stripe.Coupon.delete(self.stripe_coupon_id)
        except Exception as e:
            print(e)
            print('Не удалось удалить купон: ', self.name)
        super().delete()

    class Meta:

        verbose_name = "Купон"
        verbose_name_plural = "Купоны"


class Order(models.Model):
    items = models.ManyToManyField(Item)
    coupon = models.ForeignKey(Discount, blank=True, null=True, on_delete=models.DO_NOTHING)
    tax = models.ForeignKey(Tax, blank=True, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
