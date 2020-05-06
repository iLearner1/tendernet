from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError
import re

class LoginForm(forms.Form):
    username = forms.CharField(label="")
    password = forms.CharField(label="", widget=forms.PasswordInput)


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль...'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите пароль...'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Телефон'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        # password length check
        if (len(password) < 8) | (len(password) > 20):
            raise forms.ValidationError("Пароль должен содержать от 8 до 20 символов")

        # lowercase check
        lc_regex = re.compile("[a-z]+")
        lc = lc_regex.findall(password)
        if not lc:
            raise forms.ValidationError("Должен включать строчные буквы")

        # uppercase check
        uc_regex = re.compile("[A-Z]+")
        uc = uc_regex.findall(password)
        if not uc:
            raise forms.ValidationError("Должен включать заглавные буквы")

        # digit check
        digit_regex = re.compile("\d")
        isDigit = digit_regex.search(password)

        if not isDigit:
            raise forms.ValidationError("Должен включать заглавные буквы")

        # whitespace check
        wsp = password.strip()
        wsp = wsp.replace(" ", "")

        if len(wsp) != len(password):
            raise forms.ValidationError("Пароль не может содержать пробелы")

        # check password matches
        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")
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
    username = forms.CharField(widget=forms.TextInput(attrs={ 'placeholder': 'Номер телефона','class': 'myclass'}))
    email = forms.CharField(widget=forms.TextInput(attrs={ 'class':'form-control class',}))

    

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
        exclude = ('user', 'tarif','dob',)


class TarifEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'tarif',
        )
        exclude = ('user', 'dob',)
