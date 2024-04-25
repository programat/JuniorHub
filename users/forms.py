# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'bio', 'location', 'birth_date', 'profile_image')


class CustomUserChangeForm(UserChangeForm):
    username = forms.CharField(max_length=150, min_length=2, required=True)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    password = None

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'location', 'birth_date', 'profile_image')

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username

