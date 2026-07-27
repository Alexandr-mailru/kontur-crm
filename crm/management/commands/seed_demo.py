from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from crm.models import Client, Deal, Task

User = get_user_model()

DEMO_CLIENTS = [
    ('ООО «СеверСтрой»', 'Ирина Волкова', 'irina@severstroy.demo', '+7 921 100-20-30', 'consent'),
    ('ИП Кузнецов', 'Алексей Кузнецов', 'kuznetsov@demo.ru', '+7 903 555-12-12', 'contract'),
    ('Кафе «Берег»', 'Мария Соколова', 'maria@bereg.demo', '', 'consent'),
    ('ТехноПлюс', 'Дмитрий Орлов', 'd.orlov@techno.demo', '+7 812 900-44-55', 'contract'),
]

DEMO_DEALS = [
    ('СеверСтрой', 'Поставка оборудования', '450000', 'proposal'),
    ('ИП Кузнецов', 'Сайт-визитка', '85000', 'contact'),
    ('Кафе «Берег»', 'Договор на доставку', '120000', 'new'),
    ('ТехноПлюс', 'CRM-консалтинг', '200000', 'won'),
    ('СеверСтрой', 'Сервисное обслуживание', '60000', 'won'),
]

DEMO_TASKS = [
    ('Позвонить Ирине', 'СеверСтрой', 'Сегодня'),
    ('Отправить КП', 'ИП Кузнецов', 'Завтра'),
    ('Встреча с Марией', 'Кафе «Берег»', 'Через 3 дня'),
]


class Command(BaseCommand):
    help = 'Демо-данные: пользователь demo + клиенты, сделки, задачи'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={'email': 'demo@kontur-crm.local'},
        )
        if created:
            user.set_password('demo12345')
            user.save()
            self.stdout.write('Создан пользователь demo / demo12345')

        Client.objects.filter(owner=user).delete()

        client_map = {}
        for company, contact, email, phone, basis in DEMO_CLIENTS:
            client = Client.objects.create(
                owner=user,
                company=company,
                contact_name=contact,
                email=email,
                phone=phone,
                data_processing_basis=basis,
            )
            client_map[company] = client

        for company_key, title, amount, stage in DEMO_DEALS:
            client = client_map.get(company_key)
            if client:
                Deal.objects.create(
                    owner=user,
                    client=client,
                    title=title,
                    amount=Decimal(amount),
                    stage=stage,
                    expected_close=date.today() + timedelta(days=14),
                )

        today = date.today()
        task_data = [
            ('Позвонить Ирине', 'ООО «СеверСтрой»', today),
            ('Отправить КП', 'ИП Кузнецов', today + timedelta(days=1)),
            ('Встреча с Марией', 'Кафе «Берег»', today + timedelta(days=3)),
        ]
        for title, company, due in task_data:
            client = client_map.get(company)
            if client:
                Task.objects.create(owner=user, client=client, title=title, due_date=due)

        self.stdout.write(self.style.SUCCESS(
            f'Готово: клиентов {Client.objects.filter(owner=user).count()}, '
            f'сделок {Deal.objects.filter(owner=user).count()}, '
            f'задач {Task.objects.filter(owner=user).count()}.'
        ))
