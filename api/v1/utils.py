from courses.models import Group


def distribute_student_to_group(user, course):
    """Распределяет пользователя по одной из 10 групп курса."""

    groups = list(Group.objects.filter(course=course))

    if not groups:
        return  # Если нет доступных групп

    # Сортируем группы по количеству студентов
    groups.sort(key=lambda g: g.students.count())

    # Находим группу с наименьшим количеством студентов
    selected_group = groups[0]

    # Добавляем пользователя в выбранную группу
    selected_group.students.add(user)
