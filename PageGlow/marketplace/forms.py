from django import forms
from . import models


class ProjectForm(forms.ModelForm):
    """Форма для создания/редактирования проекта"""
    
    class Meta:
        model = models.Project
        fields = [
            'title',
            'description',
            'required_skills',
            'category',
            'difficulty',
            'budget_min',
            'budget_max',
            'budget_type',
            'deadline',
            'is_urgent',
            'attachments',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название проекта',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Полное описание задачи',
                'rows': 6,
            }),
            'required_skills': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-select',
            }),
            'budget_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'От',
                'step': '100',
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'До',
                'step': '100',
            }),
            'budget_type': forms.RadioSelect(),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'is_urgent': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class BidForm(forms.ModelForm):
    """Форма для создания предложения"""
    
    class Meta:
        model = models.Bid
        fields = [
            'proposed_price',
            'estimated_days',
            'cover_letter',
        ]
        widgets = {
            'proposed_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Предлагаемая цена',
                'step': '0.01',
            }),
            'estimated_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Предполагаемое количество дней',
                'min': '1',
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Почему вы подходите для этого проекта?',
                'rows': 5,
            }),
        }


class FreelancerProfileForm(forms.ModelForm):
    """Форма для профиля фрилансера"""
    
    class Meta:
        model = models.FreelancerProfile
        fields = [
            'role',
            'bio',
            'avatar',
            'years_experience',
            'skills',
            'portfolio_url',
            'github_url',
            'linkedin_url',
            'hourly_rate',
            'is_available',
        ]
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-select',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Расскажите о себе (макс. 1000 символов)',
                'rows': 4,
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'years_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.5',
            }),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com',
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username',
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/username',
            }),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Почасовая ставка',
                'step': '0.01',
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'is_available': 'Доступен для новых проектов',
            'hourly_rate': 'Почасовая ставка (USD)',
            'years_experience': 'Опыт работы (в годах)',
            'portfolio_url': 'Ссылка на портфолио',
            'github_url': 'Ссылка на GitHub',
            'linkedin_url': 'Ссылка на LinkedIn',
            'bio': 'О себе',
            'skills': 'Навыки (через запятую)',
            'avatar': 'Аватар',
            'role': 'Роль',
        }


class CompanyProfileForm(forms.ModelForm):
    """Форма для профиля компании"""
    
    class Meta:
        model = models.CompanyProfile
        fields = [
            'company_name',
            'company_description',
            'logo',
            'website',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название компании',
            }),
            'company_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание компании',
                'rows': 4,
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com',
            }),
        }


class MilestoneForm(forms.ModelForm):
    """Форма для этапа проекта"""
    
    class Meta:
        model = models.Milestone
        fields = [
            'title',
            'description',
            'amount',
            'deadline',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название этапа',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание этапа',
                'rows': 3,
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Стоимость этапа',
                'step': '0.01',
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }


class ReviewForm(forms.ModelForm):
    """Форма для отзыва"""
    
    class Meta:
        model = models.Review
        fields = [
            'rating',
            'comment',
            'quality',
            'communication',
            'deadline_adherence',
            'professionalism',
        ]
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select',
                'choices': [(i, f'{i}⭐') for i in range(1, 6)],
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш отзыв',
                'rows': 4,
            }),
            'quality': forms.Select(attrs={
                'class': 'form-select',
            }),
            'communication': forms.Select(attrs={
                'class': 'form-select',
            }),
            'deadline_adherence': forms.Select(attrs={
                'class': 'form-select',
            }),
            'professionalism': forms.Select(attrs={
                'class': 'form-select',
            }),
        }


class DisputeForm(forms.ModelForm):
    """Форма для создания спора"""
    
    class Meta:
        model = models.Dispute
        fields = [
            'subject',
            'description',
        ]
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема спора',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Подробное описание проблемы',
                'rows': 6,
            }),
        }
