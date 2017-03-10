from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from colorful.fields import RGBColorField
from autoslug import AutoSlugField

from autoslug.settings import slugify as default_slugify

def underscore_slugify(value):
    return default_slugify(value).replace('-', '_')



class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def regenerate_token(self):
        pass

    def __str__(self):
        return "UserData for {}".format(self.user)


class Datum(models.Model):
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    DATE = "DATE"
    DATETIME = "DATETIME"
    TIMESTAMP = "TIMESTAMP"
    TYPE_CHOICES = [(INT, "Integer"),
                    (FLOAT, "Float"),
                    (STRING, "String"),
                    (DATE, "Date"),
                    (DATETIME, "Date & time"),
                    (TIMESTAMP, "Timestamp")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, null=False, blank=False)
    slug = AutoSlugField(populate_from="name", null=False, blank=False, slugify=underscore_slugify)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, default=STRING)
    unit = models.CharField(max_length=30, null=True, blank=True)
    color = RGBColorField(blank=False, null=False, default="#87BBFF")
    comment = models.CharField(max_length=100, blank=True, null=True)

    @property
    def color_rgba(self):
        fmt = "rgba({red}, {green}, {blue}, {alpha})"

        colors = {
            'red': int(self.color[1:3], 16),
            'green': int(self.color[3:5], 16),
            'blue': int(self.color[5:7], 16),
            'alpha': 1
        }

        return fmt.format(**colors)

    def __str__(self):
        return "{} ({}, {})".format(self.name, self.comment, self.slug)


class Value(models.Model):
    datum = models.ForeignKey(Datum, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(blank=False, null=False, default=timezone.now)
    int_value = models.IntegerField(null=True, blank=True)
    float_value = models.FloatField(null=True, blank=True)
    string_value = models.CharField(max_length=256, null=True, blank=True)
    date_value = models.DateField(null=True, blank=True)
    datetime_value = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        value = "UNDEFINED"
        if self.datum.type == Datum.FLOAT:
            value = self.float_value
        elif self.datum.type == Datum.TIMESTAMP:
            return "{} at {}".format(self.datum.name, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            raise NotImplementedError('no __str__ defined for datum type {}'.format(self.datum.type))
        return "{} at {}: {}".format(self.datum.name, self.timestamp, value)
