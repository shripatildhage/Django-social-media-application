from django import forms

from users.forms import validate_image
from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("content", "image")
        widgets = {"content": forms.Textarea(attrs={"rows": 3, "placeholder": "What's on your mind?"})}

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if not content:
            raise forms.ValidationError("Post cannot be empty.")
        return content

    def clean_image(self):
        image = self.cleaned_data.get("image")
        return validate_image(image)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {"content": forms.TextInput(attrs={"placeholder": "Write a comment..."})}
