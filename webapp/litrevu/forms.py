from django import forms
from .models import Ticket, Review
from django.conf import settings


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'image': 'Image'
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du livre/article'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Décrivez le livre ou l\'article que vous souhaitez faire critiquer'
            }),
            'image': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': 'image/*'
            }),
        }


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(settings.MAX_RATING + 1)]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(),
        label='Note'
    )

    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']
        labels = {
            'headline': 'Titre',
            'body': 'Commentaire',
        }
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
        }
