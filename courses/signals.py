from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from users.models import Subscription


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """
    Распределение нового студента в группу курса.
    """

    if created:
        course = instance.course
        # Найти группу с наименьшим количеством студентов
        group = course.groups.annotate(student_count=Count('subscriptions')).order_by('student_count').first()

        if group:
            # Присвоить студенту группу
            instance.group = group
            instance.save()
