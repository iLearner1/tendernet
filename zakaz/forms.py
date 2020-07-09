from django import forms


class Pko(forms.Form):
    CHOICES = (('Выберите значение','Выберите значение'),('Да', 'Да'), ('Нет', 'Нет'))
    CHOICES2 = (('Выберите значение','Выберите значение'),('Товар', 'Товар'), ('Работа', 'Работа'), ('Услуги', 'Услуги'))
    CHOICES3 = (('Выберите значение','Выберите значение'),('А1-А2  (закупки до 125 млн. тг.)', 'А1-А2  (закупки до 125 млн. тг.)'), ('В1-В2  (закупки до 600 млн. тг.)', 'В1-В2  (закупки до 600 млн. тг.)'), ('С1-С2 (закупки свыше 600 млн. тг.)', 'С1-С2 (закупки свыше 600 млн. тг.)'))
    field = forms.ChoiceField(choices=CHOICES, label="Вопрос  1. Проходила ли Ваша компания ПКО ранее?")
    field2 = forms.ChoiceField(choices=CHOICES2, label="Вопрос 2. Вид деятельности Вашей компании:")
    field3 = forms.ChoiceField(choices=CHOICES3, label="Вопрос 3. Выберите интересующую Вас анкету:")
    Phone = forms.CharField(max_length=18, label="Ваш номер:")

    def __str__(self):
        return self.Phone


class Iso(forms.Form):
    CHOICES = (('Выберите значение','Выберите значение'),('Да', 'Да'), ('Нет', 'Нет'))

    CHOICES2 = (('Выберите значение','Выберите значение'),('Комментарий', 'Комментарий'), ('Комментарий', 'Комментарий'))

    CHOICES3 = (('Выберите значение','Выберите значение'),('1-10 человек', '1-10 человек'), ('11-50 человек', '11-50 человек'),
                ('51-100 человек', '51-100 человек'), ('Более 100 человек', 'Более 100 человек'))

    CHOICES4 = (('Выберите значение','Выберите значение'),('Комментарий', 'Комментарий'), ('Комментарий', 'Комментарий'))

    field = forms.ChoiceField(
        choices=CHOICES, label="Вопрос 1. Имеет ли Ваша компания, какие либо сертификаты ISO?")
    field2 = forms.ChoiceField(
        choices=CHOICES2, label="Вопрос 2. Вид деятельности Вашей компании")
    field3 = forms.ChoiceField(
        choices=CHOICES3, label="Вопрос 3. Численность работников в Вашей компании?")
    field4 = forms.ChoiceField(choices=CHOICES4, label="Вопрос 4. Какой сертификат Вам нужен?")
    Phone = forms.CharField(max_length=18, label="Ваш номер:",  widget=forms.TextInput(
        attrs={
            'class': 'form-control class',
            'placeholder': 'Введите номер телефона'
        }))

    def __str__(self):
        return self.Phone
