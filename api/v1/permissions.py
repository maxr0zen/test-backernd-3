from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import BasePermission, SAFE_METHODS

from courses.models import Course
from users.models import Subscription


def make_payment(request, course_id):
    user = request.user
    course = Course.objects.get(id=course_id)

    if Subscription.objects.filter(user=user, course=course).exists():
        raise ValidationError("Вы уже подписаны на этот курс.")

    user_balance = user.balance

    if user_balance.balance < course.cost:
        raise PermissionDenied("Недостаточно средств на балансе для оплаты курса.")

    # Списание стоимости курса с баланса пользователя
    user_balance.balance -= course.cost
    user_balance.save()

    # Создание подписки
    Subscription.objects.create(user=user, course=course)

    return {"detail": "Оплата прошла успешно. Вы подписаны на курс."}


class IsStudentOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        # Разрешение доступно для администраторов или для студентов, которые авторизованы
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_student)

    def has_object_permission(self, request, view, obj):
        # Доступ к объекту разрешен администратору или студенту, если он владеет объектом
        return request.user.is_staff or obj.user == request.user


class ReadOnlyOrIsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.method in SAFE_METHODS
