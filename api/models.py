from django.db import models

class City (models.Model):
    name = models.CharField(max_length = 255)
    l_lat = models.DecimalField(max_digits = 9, decimal_places = 6)
    l_lng = models.DecimalField(max_digits = 9, decimal_places = 6)
    r_lat = models.DecimalField(max_digits = 9, decimal_places = 6)
    r_lng = models.DecimalField(max_digits = 9, decimal_places = 6)


class CityBox (models.Model):
    row = models.IntegerField()
    col = models.IntegerField()
    city = models.ForeignKey(City)


class UbikeStat ((models.Model)):
    name = models.CharField(max_length = 255)
    lat = models.DecimalField(max_digits = 9, decimal_places = 6)
    lng = models.DecimalField(max_digits = 9, decimal_places = 6)
    sbi = models.IntegerField()
    bemp = models.IntegerField()
    box = models.ForeignKey(CityBox)
