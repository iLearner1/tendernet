from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError

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
