from django.db import models
from django.db.models import Q, Count


class Week(models.Model):
    date = models.DateField(unique=True)
    complete = models.BooleanField(default=False)

    def subscribers_count(self):
        return self.subscriber_set.all().count()

    def inactive_subscribers(self):
        return self.subscriber_set.filter(Q(active=False) | Q(bounces__gt=1))

    def inactive_subscribers_count(self):
        return self.inactive_subscribers().count()

    def active_subscribers(self):
        return self.subscriber_set.filter(active=True).filter(bounces__lte=1)

    def active_subscribers_count(self):
        return self.active_subscribers().count()

    def previous_week(self):
        pre = self.get_previous_by_date()
        return pre

    def change_in_subscribers(self):
        pre = self.previous_week()
        return self.subscribers_count() - pre.subscribers_count()

    def change_in_active_subscribers(self):
        pre = self.previous_week()
        return self.active_subscribers_count() - pre.active_subscribers_count()

    def new_subscribers(self):
        diff = Subscriber.objects.filter(week__in=(self.pk, self.previous_week().pk)).values('email').annotate(count=Count('email')).filter(count=1)
        email = self.subscriber_set.filter(email__in=diff.values('email'))
        return email.count()

    def active_to_inactive(self):
        current_inactive = self.inactive_subscribers().values('email')
        change = self.previous_week().active_subscribers().filter(email__in=current_inactive)
        return change.count()

    def inactive_to_active(self):
        current_active = self.active_subscribers().values('email')
        change = self.previous_week().inactive_subscribers().filter(email__in=current_active)
        return change.count()


class Subscriber(models.Model):
    email = models.CharField(db_index=True, max_length=40)
    email_domain = models.CharField(db_index=True, max_length=24)
    active = models.BooleanField(db_index=True)
    week = models.ForeignKey('Week', db_index=True)
    bounces = models.IntegerField(db_index=True)


