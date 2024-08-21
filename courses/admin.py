from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from .models import Course, Lesson, Group, UserBalance, UserProductAccess

User = get_user_model()

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'start_date', 'price')
    search_fields = ('title', 'author')
    list_filter = ('start_date',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'course')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'get_students_count')

    def get_students_count(self, obj):
        """Возвращает количество студентов в группе."""
        return obj.students.count()

    get_students_count.short_description = 'Количество студентов'

class UserBalanceForm(forms.ModelForm):
    class Meta:
        model = UserBalance
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        balance_amount = cleaned_data.get('balance')  # Проверяем только баланс

        if user and balance_amount:
            try:
                user_balance = UserBalance.objects.get(user=user)
                if user_balance.balance < balance_amount:
                    raise forms.ValidationError("Недостаточно средств для оплаты.")
            except UserBalance.DoesNotExist:
                # Если баланс для пользователя не найден, игнорируем, так как создадим новый баланс
                pass

@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    form = UserBalanceForm
    list_display = ('user', 'balance')
    search_fields = ('user__username',)

    def save_model(self, request, obj, form, change):
        if change:  # Если запись обновляется
            self.message_user(request, "Баланс нельзя обновить через эту панель. Создайте новый баланс для пользователя.", level='error')
        else:  # Если запись создается
            try:
                if not UserBalance.objects.filter(user=obj.user).exists():
                    obj.save()
                    # Вызываем логику открытия доступа к курсу
                    self._open_course_access(request, obj)
                    self.message_user(request, "Баланс успешно добавлен, и доступ к курсу открыт.")
                else:
                    self.message_user(request, "Баланс уже существует для этого пользователя.", level='error')
            except IntegrityError as e:
                self.message_user(request, f"Ошибка при создании записи о балансе: {str(e)}", level='error')

    def _open_course_access(self, request, user_balance):
        """Логика открытия доступа к курсу."""
        user = user_balance.user
        # Предположим, что курс выбирается каким-то образом, например, передается как параметр
        course_id = self._get_course_id_from_request(request)
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                if not UserProductAccess.objects.filter(user=user, course=course).exists():
                    UserProductAccess.objects.create(user=user, course=course)
            except Course.DoesNotExist:
                self.message_user(request, f"Курс с ID {course_id} не найден.", level='error')

    def _get_course_id_from_request(self, request):
        """Пример метода для получения ID курса из запроса или другого источника."""
        # Реализуйте метод для получения course_id. Это может быть из параметров запроса, формы и т.д.
        return request.GET.get('course_id')

@admin.register(UserProductAccess)
class UserProductAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'course')
    search_fields = ('user__username', 'course__title')
