from django.db import models

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    expiration_date = models.DateField()
    usage_limit = models.IntegerField(default=1)

    def _str_(self):
        return self.code