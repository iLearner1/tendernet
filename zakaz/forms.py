from django import forms


class Pko(forms.Form):
    CHOICES = (('Ответ 1', 'Ответ 1'), ('Ответ 2', 'Ответ 2'),
               ('Ответ 3', 'Ответ 3'), ('Ответ 4', 'Ответ 4'))
    field = forms.ChoiceField(choices=CHOICES, label="Вопрос 1 :")
    field2 = forms.ChoiceField(choices=CHOICES, label="Вопрос 2:")
    field3 = forms.ChoiceField(choices=CHOICES, label="Вопрос 3:")
    Phone = forms.CharField(max_length=18, label="Ваш номер:")

    def __str__(self):
        return self.Phone


class Iso(forms.Form):

    CHOICES1 = (('Да', 'Да'), ('Нет', 'Нет'))

    CHOICES3 = (('1-10 человек3', '1-10 человек3'), ('11-50 человек3', '11-50 человек3'), ("51-100 человек", "51-100 человек"), ("Более 100 человек", "Более 100 человек"))

    field = forms.ChoiceField(
        choices=CHOICES1, label="Вопрос 1. Имеет ли Ваша компания, какие либо сертификаты ISO?")

    field2 = forms.CharField(max_length=255, label="Вопрос 2. Вид деятельности Вашей компании")

    field3 = forms.ChoiceField(
        choices=CHOICES3, label="Вопрос 3. Численность работников в Вашей компании?")

    field4 = forms.CharField(max_length=255, label="Вопрос 4. Какой сертификат Вам нужен?")

    # field4 = forms.ChoiceField(choices=CHOICES4, label="Вопрос 4. Какой сертификат Вам нужен?")
    Phone = forms.CharField(max_length=18, label="Hомер телефона:",  widget=forms.TextInput(
        attrs={
            'class': 'form-control class',
            'placeholder': 'Введите номер телефона'
        }))

    def __str__(self):
        return self.Phone
