from django.contrib.auth import get_user_model
from django.test import Client as TestClient, TestCase
from django.urls import reverse

from crm.models import Client

User = get_user_model()


class LegalPagesTests(TestCase):
    def test_public_legal_pages(self):
        for name in ('crm:privacy', 'crm:copyright', 'crm:about'):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)


class CrmFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 't@test.local', 'pass12345')
        self.client = TestClient()

    def test_dashboard_requires_login(self):
        self.assertEqual(self.client.get(reverse('crm:dashboard')).status_code, 302)

    def test_register_with_pdn_consent(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'new@test.local',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'pdn_consent': True,
        })
        self.assertEqual(response.status_code, 302)

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
