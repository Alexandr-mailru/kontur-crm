from django import forms
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Client, Deal, Task


class ClientForm(forms.ModelForm):
    pdn_basis_confirm = forms.BooleanField(
        required=True,
        label='',
        error_messages={
            'required': 'Подтвердите правовое основание для хранения данных контакта.',
        },
    )

    class Meta:
        model = Client
        fields = ['company', 'contact_name', 'email', 'phone', 'data_processing_basis', 'notes']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'input'}),
            'contact_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'phone': forms.TextInput(attrs={'class': 'input'}),
            'data_processing_basis': forms.Select(attrs={'class': 'input'}),
            'notes': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        privacy = reverse_lazy('crm:privacy')
        self.fields['pdn_basis_confirm'].label = mark_safe(
            format_html(
                'Подтверждаю наличие правового основания для обработки персональных данных '
                'контакта (согласие, договор или иное основание по <a href="{}" target="_blank" '
                'rel="noopener">политике</a>)',
                privacy,
            )
        )
        self.fields['pdn_basis_confirm'].widget.attrs['class'] = 'check-input'


class ClientEditForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['company', 'contact_name', 'email', 'phone', 'data_processing_basis', 'notes']
        widgets = ClientForm.Meta.widgets


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ['client', 'title', 'amount', 'stage', 'expected_close']
        widgets = {
            'client': forms.Select(attrs={'class': 'input'}),
            'title': forms.TextInput(attrs={'class': 'input'}),
            'amount': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
            'stage': forms.Select(attrs={'class': 'input'}),
            'expected_close': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'client', 'deal', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'client': forms.Select(attrs={'class': 'input'}),
            'deal': forms.Select(attrs={'class': 'input'}),
            'due_date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        }
