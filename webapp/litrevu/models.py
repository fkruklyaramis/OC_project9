from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Ticket(models.Model):
    """Modèle pour les demandes de critique (tickets)"""
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (par {self.user.username})"


class Review(models.Model):
    """Modèle pour les critiques en réponse aux tickets"""
    ticket = models.ForeignKey(
        to=Ticket,
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(settings.MAX_RATING)]
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review: {self.headline} (note: {self.rating})"


class UserFollows(models.Model):
    """Modèle pour gérer les abonnements entre utilisateurs"""
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followed_by'
    )

    class Meta:
        # Garantit qu'un utilisateur ne peut suivre un autre utilisateur qu'une seule fois
        unique_together = ('user', 'followed_user')
        
    def __str__(self):
        return f"{self.user.username} is following {self.followed_user.username}"