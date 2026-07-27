from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client as TestClient, TestCase
from django.urls import reverse

from crm.models import Client, Deal, Task

User = get_user_model()


class LegalPagesTests(TestCase):
    def test_public_legal_pages_have_content(self):
        for name in ('crm:privacy', 'crm:terms', 'crm:copyright', 'crm:about'):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<h1>', html=False)

    def test_privacy_accessible_without_login(self):
        response = self.client.get(reverse('crm:privacy'))
        self.assertContains(response, 'ФЗ')


class CrmFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 't@test.local', 'pass12345')
        self.other = User.objects.create_user('other', 'o@test.local', 'pass12345')
        self.client = TestClient()

    def test_dashboard_requires_login(self):
        self.assertEqual(self.client.get(reverse('crm:dashboard')).status_code, 302)

    def test_register_saves_email(self):
        self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'new@test.local',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'terms_accept': True,
            'pdn_consent': True,
        })
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@test.local')

    def test_register_without_pdn_consent_fails(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'baduser',
            'email': 'bad@test.local',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='baduser').exists())

    def test_register_without_terms_fails(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'baduser2',
            'email': 'bad2@test.local',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'pdn_consent': True,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='baduser2').exists())

    def test_register_page_shows_consent_links(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('crm:terms'))
        self.assertContains(response, 'пользовательское соглашение')
        self.assertContains(response, reverse('crm:privacy'))

    def test_client_create_page_shows_pdn_confirm_text(self):
        self.client.login(username='tester', password='pass12345')
        response = self.client.get(reverse('crm:client_create'))
        self.assertContains(response, 'правового основания')
        self.assertContains(response, reverse('crm:privacy'))

    def test_client_create_requires_pdn_basis(self):
        self.client.login(username='tester', password='pass12345')
        response = self.client.post(reverse('crm:client_create'), {
            'company': 'ООО Тест',
            'contact_name': 'Иван',
            'email': 'ivan@test.local',
            'phone': '',
            'data_processing_basis': 'consent',
            'notes': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Client.objects.filter(company='ООО Тест').exists())

        response = self.client.post(reverse('crm:client_create'), {
            'company': 'ООО Тест',
            'contact_name': 'Иван',
            'email': 'ivan@test.local',
            'phone': '',
            'data_processing_basis': 'consent',
            'notes': '',
            'pdn_basis_confirm': True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Client.objects.filter(company='ООО Тест').exists())

    def test_user_cannot_see_other_users_clients(self):
        Client.objects.create(
            owner=self.other,
            company='Чужой клиент',
            contact_name='Петр',
            email='p@test.local',
            data_processing_basis='consent',
        )
        self.client.login(username='tester', password='pass12345')
        response = self.client.get(reverse('crm:client_list'))
        self.assertNotContains(response, 'Чужой клиент')


class RedirectSafetyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 't@test.local', 'pass12345')
        self.client = TestClient()
        self.client.login(username='tester', password='pass12345')
        self.client_obj = Client.objects.create(
            owner=self.user,
            company='Тест',
            contact_name='Иван',
            email='i@test.local',
            data_processing_basis='consent',
        )
        self.deal = Deal.objects.create(
            owner=self.user,
            client=self.client_obj,
            title='Тест',
            amount=Decimal('1000'),
            stage='new',
        )

    def test_task_toggle_redirects_to_fallback_on_external_next(self):
        task = Task.objects.create(owner=self.user, title='Задача')
        response = self.client.post(
            reverse('crm:task_toggle', args=[task.pk]),
            {'next': 'https://evil.example/'},
        )
        self.assertRedirects(response, reverse('crm:task_list'), fetch_redirect_response=False)

    def test_deal_stage_redirects_on_valid_next(self):
        response = self.client.post(
            reverse('crm:deal_stage', args=[self.deal.pk]),
            {'stage': 'won', 'next': reverse('crm:dashboard')},
        )
        self.assertRedirects(response, reverse('crm:dashboard'), fetch_redirect_response=False)
