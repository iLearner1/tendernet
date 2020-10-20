from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.html import format_html, format_html_join

#from django.contrib.auth import forms
from django.contrib.auth.forms import PasswordResetForm

set_password_validation_rules = {"char_len": "Пароль должен содержать от 8 до 20 символов",
                                 "lc": "Пароль должен содержать строчные буквы",
                                 "uc": "Пароль должен содержать заглавные буквы",
                                 "isDig": "Пароль должен содержать цифры",
                                 "wsp": "Пароль не может содержать пробелы"
                                 }


def validate_password(password, confirm_password):
    errors = []

    # password length check
    if (len(password) < 8) | (len(password) > 20):
        errors.append(set_password_validation_rules["char_len"])

    # lowercase check
    lc_regex = re.compile("[a-z]+")
    lc = lc_regex.findall(password)
    if not lc:
        errors.append(set_password_validation_rules["lc"])

    # uppercase check
    uc_regex = re.compile("[A-Z]+")
    uc = uc_regex.findall(password)
    if not uc:
        errors.append(set_password_validation_rules["uc"])

    # digit check
    digit_regex = re.compile("\d")
    isDigit = digit_regex.search(password)

    if not isDigit:
        errors.append(set_password_validation_rules["isDig"])

    # whitespace check
    wsp = password.strip()
    wsp = wsp.replace(" ", "")

    if len(wsp) != len(password):
        errors.append(set_password_validation_rules["wsp"])

    # check password matches
    if password != confirm_password:
        errors.append("Пароли не совпадают")
    return errors


class CustomEmailValidationOnForgotPassword(SetPasswordForm):
    new_password1 = forms.CharField(label="Новый пароль",
                                    widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'}),
                                    help_text=format_html('<ul>{}</ul>', format_html_join('', '<li style="background-color:#f8d7da">{}</li>',
                                                                                          ((help_text,) for help_text in
                                                                                           set_password_validation_rules.values()))))

    new_password2 = forms.CharField(
        label="New password confirmation",
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтверждение нового пароля'}),
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        errors = validate_password(password1, password2)

        if len(errors) > 0:
            raise forms.ValidationError([])

        return password2


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("Электронная почта не существует")

        return email


class LoginForm(forms.Form):
    username = forms.CharField(label="")
    password = forms.CharField(label="", widget=forms.PasswordInput)


class SignupForm(forms.ModelForm):
    company_name = forms.CharField(label='Наименование компании',widget=forms.TextInput(attrs={'placeholder': 'Наименование компании', 'class': 'form-control'}))
    company_business_number = forms.CharField(label='ИИН/БИН',widget=forms.TextInput(attrs={'placeholder': 'ИИН/БИН', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль...'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите пароль...'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Телефон'}))


    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        errors = validate_password(password, confirm_password)

        if len(errors) > 0:
            raise forms.ValidationError(errors)

        return confirm_password

    def clean(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise ValidationError("Такой Username уже существует")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Такой Email уже существует")
        return self.cleaned_data


class UserEditForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Номер телефона', 'class': 'myclass'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control class', }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)


class UserEditForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Номер телефона', 'class': 'myclass'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control class', }))

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',

        )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'tarif', 'dob', 'company_name', 'company_business_number')
        # fields = "__all__"


class TarifEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'tarif',
        )
        exclude = ('user', 'dob',)
