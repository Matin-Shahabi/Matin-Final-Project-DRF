from django.db import models
from users.models import BaseModel



class Category(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=300,default="No Description yet")
    image = models.ImageField(
        upload_to="categories/",
        null=True,
        blank=True
    )
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")

    def __str__(self):
        return self.name