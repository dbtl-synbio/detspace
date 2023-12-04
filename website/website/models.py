from django.db import models

class Target(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
       return f"{self.name} is the target"

