import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField( label='Пароль' ,widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField( label='Пароль' ,widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField( label='Повторите пароль' ,widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'email': 'E-mail',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Такой email уже существует!')
        return email

class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    email = forms.CharField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))

    class Meta:
        model = get_user_model()
        fields = ['photo', 'username', 'email', 'first_name', 'last_name', 'about_me', 'data_birth', 'phone_namber', 
                  'banner_gradient_start', 'banner_gradient_end', 'banner_image']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'data_birth': 'Дата рождения',
            'phone_namber': 'Номер телефона',
            'about_me': 'О себе',
            'banner_gradient_start': 'Начальный цвет градиента',
            'banner_gradient_end': 'Конечный цвет градиента',
            'banner_image': 'Изображение баннера',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваша фамилия'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'about_me': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Расскажите немного о себе...', 'maxlength': 255}),
            'data_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'format': '%Y-%m-%d'}),
            'phone_namber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (___) ___-__-__', 'type': 'tel', 'id': 'phone-input'}),
            'banner_gradient_start': forms.TextInput(attrs={'class': 'form-control', 'type': 'color', 'style': 'height: 50px; cursor: pointer;'}),
            'banner_gradient_end': forms.TextInput(attrs={'class': 'form-control', 'type': 'color', 'style': 'height: 50px; cursor: pointer;'}),
            'banner_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def clean_data_birth(self):
        data = self.cleaned_data.get('data_birth')
        if data and isinstance(data, str):
            from datetime import datetime
            try:
                data = datetime.strptime(data, '%Y-%m-%d').date()
            except ValueError:
                try:
                    data = datetime.strptime(data, '%d.%m.%Y').date()
                except ValueError:
                    raise forms.ValidationError('Неверный формат даты. Используйте ГГГГ-ММ-ДД')
        return data
    
    def clean_phone_namber(self):
        phone = self.cleaned_data.get('phone_namber')
        if phone:
            # Удаляем все лишние символы, оставляем только цифры
            cleaned = ''.join(filter(lambda x: x.isdigit(), phone))
            
            # Если номер начинается с 8, заменяем на 7
            if cleaned.startswith('8'):
                cleaned = '7' + cleaned[1:]
            
            # Если не начинается с 7, добавляем 7
            if not cleaned.startswith('7'):
                cleaned = '7' + cleaned
            
            # Ограничиваем 11 цифрами
            cleaned = cleaned[:11]
            
            return cleaned
        return phone


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))