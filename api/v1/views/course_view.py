from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin, make_payment
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from api.v1.utils import distribute_student_to_group
from courses.models import Course, UserProductAccess, UserBalance
from users.models import Subscription, Balance

User = get_user_model()


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()




class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы."""

    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk=None):
        """Оплата доступа к курсу (подписка на курс)."""

        course = get_object_or_404(Course, pk=pk)
        user = request.user

        # Получаем баланс пользователя
        try:
            user_balance = UserBalance.objects.get(user=user)
        except UserBalance.DoesNotExist:
            return Response({'detail': 'Баланс пользователя не найден.'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, хватает ли бонусов для оплаты
        if user_balance.balance < course.price:
            return Response({'detail': 'Недостаточно средств.'}, status=status.HTTP_400_BAD_REQUEST)

        # Выполняем транзакцию
        with transaction.atomic():
            # Списываем бонусы
            user_balance.balance -= course.price
            user_balance.save()

            # Открываем доступ к курсу
            UserProductAccess.objects.get_or_create(user=user, course=course)

            # Распределяем пользователя по группам
            distribute_student_to_group(user, course)

        return Response({'detail': 'Оплата успешна, доступ к курсу открыт.'}, status=status.HTTP_201_CREATED)