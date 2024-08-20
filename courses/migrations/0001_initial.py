# Generated by Django 4.2.10 on 2024-08-20 00:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Название')),
                ('start_date', models.DateTimeField(verbose_name='Дата и время начала курса')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
            ],
            options={
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Название группы')),
            ],
            options={
                'verbose_name': 'Группа',
                'verbose_name_plural': 'Группы',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Название')),
                ('link', models.URLField(max_length=250, verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'Урок',
                'verbose_name_plural': 'Уроки',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='UserBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Баланс')),
            ],
            options={
                'verbose_name': 'Баланс',
                'verbose_name_plural': 'Балансы',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='UserProductAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_accesses', to='courses.course', verbose_name='Курс')),
            ],
            options={
                'verbose_name': 'Доступ к продукту',
                'verbose_name_plural': 'Доступы к продуктам',
                'ordering': ('-id',),
            },
        ),
    ]