from django.db import models
from django.conf import settings
from .constants import MAX_RATING
from django.core.validators import MinValueValidator, MaxValueValidator


class Ticket(models.Model):
    """
    Modèle représentant une demande de critique (ticket).

    Un ticket est créé par un utilisateur qui souhaite recevoir des critiques
    sur un livre ou un article. Il comporte un titre, une description optionnelle
    et peut inclure une image de couverture.

    Attributes:
        title (CharField): Titre du livre ou de l'article (128 caractères max)
        description (TextField): Description détaillée du contenu (2048 caractères max, optionnel)
        user (ForeignKey): Référence à l'utilisateur qui a créé le ticket
        image (ImageField): Image de couverture du livre (optionnelle)
        time_created (DateTimeField): Date et heure de création du ticket, générées automatiquement
    """
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Représentation textuelle du ticket.

        Returns:
            str: Le titre du ticket suivi du nom d'utilisateur de son créateur
        """
        return f"{self.title} (par {self.user.username})"


class Review(models.Model):
    """
    Modèle représentant une critique en réponse à un ticket.

    Une critique est publiée par un utilisateur en réponse à un ticket existant.
    Elle comprend un titre (headline), un corps de texte, et une note entre 0 et MAX_RATING.

    Attributes:
        ticket (ForeignKey): Référence au ticket auquel cette critique répond
        rating (PositiveSmallIntegerField): Note attribuée, entre 0 et MAX_RATING (défini dans constants.py)
        user (ForeignKey): Référence à l'utilisateur qui a créé la critique
        headline (CharField): Titre/en-tête de la critique (128 caractères max)
        body (TextField): Corps de la critique (8192 caractères max, optionnel)
        time_created (DateTimeField): Date et heure de création de la critique, générées automatiquement
    """
    ticket = models.ForeignKey(
        to=Ticket,
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_RATING)]
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Représentation textuelle de la critique.

        Returns:
            str: Le titre de la critique suivi de sa note
        """
        return f"Review: {self.headline} (note: {self.rating})"


class UserFollows(models.Model):
    """
    Modèle gérant les relations d'abonnement entre utilisateurs.

    Permet à un utilisateur de suivre d'autres utilisateurs pour voir leurs publications.
    Les relations sont unidirectionnelles (si A suit B, B ne suit pas automatiquement A).

    Attributes:
        user (ForeignKey): L'utilisateur qui suit (abonné)
        followed_user (ForeignKey): L'utilisateur qui est suivi (abonnement)

    Note:
        Une contrainte d'unicité est définie sur la paire (user, followed_user)
        pour empêcher des abonnements dupliqués.
    """
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
        """
        Représentation textuelle de la relation d'abonnement.

        Returns:
            str: Description de la relation d'abonnement entre deux utilisateurs
        """
        return f"{self.user.username} is following {self.followed_user.username}"
