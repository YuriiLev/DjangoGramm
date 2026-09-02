from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "bio", "avatar"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your full name"}
            ),
            "bio": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Tell us about yourself", "rows": 4}
            ),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
