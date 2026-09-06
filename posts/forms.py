from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    new_tags = forms.CharField(
        required=False,
        label="New tags",
        help_text="Comma-separated. Created if they don't exist yet.",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "sunset, roadtrip"}),
    )

    class Meta:
        model = Post
        fields = ["description"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "What's on your mind?",
                    "rows": 4,
                }
            ),
        }

    def clean_new_tags(self):
        raw = self.cleaned_data.get("new_tags", "")
        names = {name.strip().lower() for name in raw.split(",")}
        names.discard("")

        too_long = [name for name in names if len(name) > 100]
        if too_long:
            raise forms.ValidationError("Tag names must be 100 characters or fewer.")

        return sorted(names)
