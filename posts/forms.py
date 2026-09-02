from django import forms

from .models import Post, PostImage, Tag


class PostForm(forms.ModelForm):
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


class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ["image"]
        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }


PostImageFormSet = forms.modelformset_factory(PostImage, form=PostImageForm, extra=3, max_num=10)


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tag name"}),
        }


class PostTagForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
