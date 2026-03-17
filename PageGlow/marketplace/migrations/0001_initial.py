from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('category', models.CharField(
                    choices=[('language', 'Язык программирования'), ('framework', 'Фреймворк'), 
                    ('tool', 'Инструмент'), ('database', 'База данных'), ('other', 'Другое')],
                    default='other',
                    max_length=20
                )),
                ('icon', models.CharField(blank=True, help_text='CSS класс иконки (например: fab fa-python)', max_length=200)),
            ],
            options={
                'verbose_name': 'Навык',
                'verbose_name_plural': 'Навыки',
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('budget_min', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(1)])),
                ('budget_max', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(1)])),
                ('budget_type', models.CharField(choices=[('fixed', 'Фиксированная сумма'), ('hourly', 'Почасовая ставка')], default='fixed', max_length=10)),
                ('currency', models.CharField(default='RUB', max_length=3)),
                ('deadline', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(
                    choices=[('draft', 'Черновик'), ('published', 'Опубликован'), ('in_progress', 'В работе'),
                    ('review', 'На проверке'), ('completed', 'Завершен'), ('cancelled', 'Отменён')],
                    default='published',
                    max_length=20
                )),
                ('budget_remaining', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('category', models.CharField(
                    choices=[('web', 'Веб-разработка'), ('mobile', 'Мобильное приложение'), 
                    ('data', 'Data Science'), ('devops', 'DevOps'), ('design', 'Дизайн'), ('other', 'Другое')],
                    default='other',
                    max_length=50
                )),
                ('difficulty', models.CharField(
                    choices=[('easy', 'Легко'), ('medium', 'Средне'), ('hard', 'Сложно')],
                    default='medium',
                    max_length=20
                )),
                ('is_urgent', models.BooleanField(default=False, help_text='Срочный проект')),
                ('attachments', models.JSONField(blank=True, default=list, help_text='Ссылки на файлы/прототипы')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_projects', to=settings.AUTH_USER_MODEL)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_projects', to=settings.AUTH_USER_MODEL)),
                ('required_skills', models.ManyToManyField(related_name='projects', to='marketplace.skill')),
            ],
            options={
                'verbose_name': 'Проект',
                'verbose_name_plural': 'Проекты',
                'ordering': ['-created_at'],
            },
        ),
    ]
