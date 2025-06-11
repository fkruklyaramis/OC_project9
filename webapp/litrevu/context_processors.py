from django.conf import settings


def rating_settings(request):
    """
    Ajoute des constantes liées aux notations à tous les templates.
    """
    return {
        'MAX_RATING': settings.MAX_RATING,
    }
