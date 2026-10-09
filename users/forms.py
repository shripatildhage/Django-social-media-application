from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile

MAX_IMAGE_MB = 5


def validate_image(f):
    if f and f.size > MAX_IMAGE_MB * 1024 * 1024:
        raise forms.ValidationError(f"Image must be under {MAX_IMAGE_MB} MB.")
    return f


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("bio", "profile_picture", "cover_photo", "location", "website", "is_private")
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}

    def clean_profile_picture(self):
        return validate_image(self.cleaned_data.get("profile_picture"))

    def clean_cover_photo(self):
        return validate_image(self.cleaned_data.get("cover_photo"))
