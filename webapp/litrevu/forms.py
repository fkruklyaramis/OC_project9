from django import forms
from .models import Ticket, Review
from .constants import MAX_RATING


class TicketForm(forms.ModelForm):
    """
    Formulaire pour créer ou modifier un ticket.

    Permet aux utilisateurs de créer une demande de critique pour un livre ou un article
    avec un titre, une description et une image de couverture optionnelle.
    """
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
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


class ReviewForm(forms.ModelForm):
    """
    Formulaire pour créer ou modifier une critique.

    Permet aux utilisateurs de rédiger une critique en réponse à un ticket,
    avec un titre, un texte de critique et une note de 0 à 5 étoiles.
    """
    RATING_CHOICES = [(i, str(i)) for i in range(MAX_RATING + 1)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input me-1'}),
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
            'headline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de votre critique'}),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Rédigez votre critique ici'
            }),
        }
