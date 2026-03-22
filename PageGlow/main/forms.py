from django import forms
from django.core.validators import MinLengthValidator

from django_ckeditor_5.widgets import CKEditor5Widget
from .models import *


class AddPostForm(forms.ModelForm):
    cat = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label='Не выбрано',
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    content = forms.CharField(
        label='Статья',
        widget=CKEditor5Widget(config_name='default'),
        initial='<h1></h1>'
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=TagPost.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    post_type = forms.ChoiceField(
        choices=Post.PostType.choices,
        initial=Post.PostType.POST,
        label='Тип публикации',
        widget=forms.RadioSelect(attrs={'class': 'post-type-selector'})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].required = False

    class Meta:
        model = Post
        fields = ['content', 'photo', 'is_published', 'cat', 'tags', 'post_type']
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class':'form-control'}),
            'is_published': forms.Select(attrs={'class':'form-control'}),
            'post_type': forms.RadioSelect(attrs={'class': 'post-type-selector'}),
        }

    def clean_content(self):
        content = self.cleaned_data['content']
        # Проверяем наличие заголовка
        if content and not ('<h1>' in content or '<h2>' in content):
            content = '<h1>Заголовок</h1>' + content
        return content

class PostUpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'photo', 'is_published', 'cat', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'id': 'file',
            }),
            'cat': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select',
            }),
            'is_published':forms.Select(attrs={
                'class':'form-control'
            })
        }

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Файл',widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 1, 'class': "form-control",}),
        }

class AddQuestionForm(forms.ModelForm):
    """Форма создания обсуждения"""
    cat = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label='Не выбрано',
        label='Категория',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=TagPost.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Теги'
    )

    class Meta:
        model = Discussion
        fields = ['title', 'content', 'cat', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок темы'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Опишите ваш вопрос подробнее...',
                'rows': 5
            }),
        }


class DiscussionCommentForm(forms.ModelForm):
    """Форма комментария к обсуждению"""
    class Meta:
        model = DiscussionComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Напишите ваш ответ...'
            }),
        }