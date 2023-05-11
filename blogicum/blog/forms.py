from django import forms

from .models import Comment, Post, User


class BlogForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'created_at', 'is_published')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
