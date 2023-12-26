from django.db import models

class Producibles(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=250)
    smiles = models.CharField(max_length=1024)

class Detectables(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=250)
    smiles = models.CharField(max_length=1024)

class Pathways(models.Model):
    producible = models.PositiveIntegerField()
    detectable = models.PositiveIntegerField()

class Target(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
       return f"{self.name} is the target"