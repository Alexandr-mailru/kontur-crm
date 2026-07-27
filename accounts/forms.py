from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class RegisterForm(UserCreationForm):
    pdn_consent = forms.BooleanField(
        required=True,
        label='',
        error_messages={'required': 'Нужно согласие на обработку персональных данных.'},
    )

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.setdefault('class', 'input')
        self.fields['email'].required = True
        privacy = reverse_lazy('crm:privacy')
        self.fields['pdn_consent'].label = mark_safe(
            format_html(
                'Согласен(на) на <a href="{}" target="_blank" rel="noopener">обработку персональных данных</a> '
                'для создания аккаунта и работы CRM',
                privacy,
            )
        )
        self.fields['pdn_consent'].widget.attrs['class'] = 'check-input'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'input'
