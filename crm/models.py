from django.conf import settings
from django.db import models


class Client(models.Model):
    BASIS_CHOICES = [
        ('consent', 'Согласие контакта'),
        ('contract', 'Договор'),
        ('other', 'Иное законное основание'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name='Менеджер',
    )
    company = models.CharField('Компания', max_length=200)
    contact_name = models.CharField('Контактное лицо', max_length=120)
    email = models.EmailField('Email', blank=True)
    phone = models.CharField('Телефон', max_length=32, blank=True)
    notes = models.TextField('Заметки', blank=True)
    data_processing_basis = models.CharField(
        'Основание обработки ПДн',
        max_length=20,
        choices=BASIS_CHOICES,
        default='consent',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['company']

    def __str__(self):
        return self.company


class Deal(models.Model):
    STAGE_CHOICES = [
        ('new', 'Новая'),
        ('contact', 'Контакт'),
        ('proposal', 'Предложение'),
        ('won', 'Успех'),
        ('lost', 'Отказ'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='deals', verbose_name='Клиент')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deals',
        verbose_name='Менеджер',
    )
    title = models.CharField('Название', max_length=200)
    amount = models.DecimalField('Сумма, ₽', max_digits=12, decimal_places=2, default=0)
    stage = models.CharField('Этап', max_length=20, choices=STAGE_CHOICES, default='new')
    expected_close = models.DateField('План закрытия', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    @property
    def stage_label(self):
        return dict(self.STAGE_CHOICES).get(self.stage, self.stage)


class Task(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Исполнитель',
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=True, blank=True,
        related_name='tasks', verbose_name='Клиент',
    )
    deal = models.ForeignKey(
        Deal, on_delete=models.CASCADE, null=True, blank=True,
        related_name='tasks', verbose_name='Сделка',
    )
    title = models.CharField('Задача', max_length=200)
    due_date = models.DateField('Срок', null=True, blank=True)
    is_done = models.BooleanField('Выполнена', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['is_done', 'due_date', '-created_at']

    def __str__(self):
        return self.title
