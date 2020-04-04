from django import forms

class Pko(forms.Form):


    CHOICES = (('Ответ 1', 'Ответ 1'),('Ответ 2', 'Ответ 2'),('Ответ 3', 'Ответ 3'),('Ответ 4', 'Ответ 4'))
    field = forms.ChoiceField(choices=CHOICES,label="Вопрос1 :")
    field2 = forms.ChoiceField(choices=CHOICES, label="Вопрос2:")
    field3 = forms.ChoiceField(choices=CHOICES, label="Вопрос3:")
    Phone = forms.CharField(max_length=18, label="Ваш номер:")
    def __str__(self):
        return self.Phone

class Iso(forms.Form):
    CHOICES = (('Ответ 1', 'Ответ 1'),('Ответ 2', 'Ответ 2'),('Ответ 3', 'Ответ 3'),('Ответ 4', 'Ответ 4'))
    field = forms.ChoiceField(choices=CHOICES,label="Вопрос:")
    field2 = forms.ChoiceField(choices=CHOICES, label="Вопрос2:")
    field3 = forms.ChoiceField(choices=CHOICES, label="Вопрос3:")
    Phone = forms.CharField(max_length=18,label="Ваш номер:",  widget=forms.TextInput(
        attrs={
        'class':'form-control class',
        'placeholder':'Username'
        }))

    def __str__(self):
        return self.Phone

