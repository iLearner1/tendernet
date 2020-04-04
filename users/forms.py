from django import forms
from django.contrib.auth.models import User
from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField(label="")
    password = forms.CharField(label="", widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password Here...'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password...'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Телефон'}))

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',

        )

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Password Mismatch")
        return confirm_password


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
