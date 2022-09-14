from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=100, default='1')

    def __str__(self):
        return self.name

    class Meta:

        verbose_name = "Товар"
        verbose_name_plural = "Товары"
