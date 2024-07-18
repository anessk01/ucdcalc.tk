from django.db import models


# Create your models here.

class HomeAdder(models.Model):
    title = models.CharField(max_length=120)

    def __str__(self):
        return self.title

class Counter(models.Model):
    value = models.IntegerField(default=164852)

    def increment(self):
        self.value += 1
        self.save()

    @classmethod
    def get_counter_value(cls):
        counter, created = cls.objects.get_or_create(pk=1)
        return counter.value