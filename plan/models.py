import datetime
from django.db import models
from django.conf import settings


PAYMENT_CHOICES = (
    ('S', 'Success'),
    ('F', 'Failed'),
    ('C', 'Canceled'),
)


# Create your models here.
class PremiumPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='premium_plans'
    )
    description = models.CharField(max_length=200, 
                                default="PremiumPlan of our website")
    amount = models.FloatField(default=30000)
    started_date = models.DateTimeField(auto_now_add=True)
    finished_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    def set_finish_date(self):
        date_started =  self.started_date
        time_ended = date_started + datetime.timedelta(days=30)
        self.finished_date = time_ended
        return 1

    

class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    plan = models.ForeignKey(PremiumPlan, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.FloatField(default=30000)
    status = models.CharField(max_length=2, choices=PAYMENT_CHOICES, null=True, blank=True)
    authority = models.CharField(max_length=255)
    ref_id = models.CharField(max_length=400, null=True, blank=True)
    card_pan = models.CharField(max_length=400, null=True, blank=True)
    card_hash = models.CharField(max_length=400, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
