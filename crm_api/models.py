from django.db import models
from epicevents import settings

from authentication.models import User


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=250, verbose_name="Company Name", blank=False)

    class Meta:
        verbose_name = "Company"

    def __str__(self):
        return self.name


class Client(models.Model):
    first_name = models.CharField(max_length=25, verbose_name="First Name", blank=False)
    last_name = models.CharField(max_length=25, verbose_name="Last Name", blank=False)
    email = models.EmailField(max_length=100, verbose_name='E-Mail', unique=True)
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    mobile = models.CharField(max_length=20, verbose_name="Mobile Number")
    company = models.ForeignKey(to=Company, on_delete=models.RESTRICT)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Date Created')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='Date Updated')

    class Meta:
        verbose_name = "Client"
        ordering = ["company"]


class Contract(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Date Created')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='Date Updated')
    status = models.BooleanField(default=False, verbose_name="Active contract")
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, verbose_name="Amount")
    payment_due = models.DateTimeField(blank=True, null=True, verbose_name="Payment Due")
    sales_contact = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True,
                                      blank=True, limit_choices_to={'user_team': 3})
    client = models.ForeignKey(to=Client, on_delete=models.RESTRICT)

    class Meta:
        verbose_name = "Contract"

    def __str__(self):
        return self.str(self.id)


class Event(models.Model):
    CHOICES_STATUS = (
        (1, 'Begin'),
        (2, 'In Progress'),
        (3, 'Ended')

    )
    status = models.PositiveSmallIntegerField(choices=CHOICES_STATUS, verbose_name="Status")
    contract = models.OneToOneField(to=Contract, on_delete=models.CASCADE)
    support_contact = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True,
                                        blank=True, limit_choices_to={'user_team': 2})
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Date Created')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='Date Updated')
    event_date = models.DateTimeField(blank=True, null=True, verbose_name="Date of the Event")
    attendees = models.IntegerField(blank=True, null=True, verbose_name="Number of attendees")
    note = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Event"
