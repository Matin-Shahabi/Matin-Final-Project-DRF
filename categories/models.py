from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=300,default="No Description yet")
    is_active = models.BooleanField(default=True)
    image = models.ImageField(
        upload_to="categories/",
        null=True,
        blank=True
    )
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")

    def __str__(self):
        return self.name