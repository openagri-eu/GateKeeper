from django import forms

from .models import DefaultAuthUserExtend
from .utils.validators import validate_password


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_password],
        label="Password",
        help_text="Password must be at least 8 characters long."
    )

    class Meta:
        model = DefaultAuthUserExtend
        fields = ["first_name", "last_name", "username", "email", "password", "contact_no"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if DefaultAuthUserExtend.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class UserLoginForm(forms.Form):
    login = forms.CharField(
        max_length=100,
        help_text="Username or Email",
        label="Login"
    )
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
