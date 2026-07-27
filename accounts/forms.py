from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class RegisterForm(UserCreationForm):
    terms_accept = forms.BooleanField(
        required=True,
        label='',
        error_messages={'required': 'Нужно принять пользовательское соглашение.'},
    )
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
            if hasattr(field.widget, 'attrs') and not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'input')
        self.fields['email'].required = True
        terms = reverse('crm:terms')
        privacy = reverse('crm:privacy')
        self.fields['terms_accept'].label = mark_safe(
            format_html(
                'Принимаю <a href="{}" target="_blank" rel="noopener">пользовательское соглашение</a>',
                terms,
            )
        )
        self.fields['terms_accept'].widget.attrs['class'] = 'check-input'
        self.fields['pdn_consent'].label = mark_safe(
            format_html(
                'Согласен(на) на <a href="{}" target="_blank" rel="noopener">обработку персональных данных</a> '
                'для создания аккаунта и работы CRM',
                privacy,
            )
        )
        self.fields['pdn_consent'].widget.attrs['class'] = 'check-input'
        self.order_fields(['username', 'email', 'password1', 'password2', 'terms_accept', 'pdn_consent'])

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'input'
