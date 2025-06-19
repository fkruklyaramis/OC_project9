# CONSTANTES

# Nombre maximum de critiques par ticket
MAX_RATING = 5

# Messages d'erreur
ERROR_MESSAGES = {
    'PASSWORD_MISMATCH': 'Les deux mots de passe ne correspondent pas.',
    'USERNAME_EXISTS': 'Ce nom d\'utilisateur existe déjà.',
    'LOGIN_FAILED': "Nom d'utilisateur ou mot de passe incorrect. Veuillez réessayer.",
    'CANNOT_FOLLOW_SELF': 'Vous ne pouvez pas vous suivre vous-même.',
    'ALREADY_FOLLOWING': 'Vous suivez déjà {username}.',
    'USER_NOT_FOUND': 'L\'utilisateur {username} n\'existe pas.',
    'FOLLOW_RELATION_NOT_FOUND': 'Cette relation de suivi n\'existe pas.',
    'ALREADY_REVIEWED': 'Vous avez déjà posté une critique pour ce ticket.',
}

# Messages de succès
SUCCESS_MESSAGES = {
    'ACCOUNT_CREATED': 'Compte créé avec succès pour {username}',
    'NOW_FOLLOWING': 'Vous suivez maintenant {username}.',
    'UNFOLLOWED': 'Vous ne suivez plus {username}.',
    'REVIEW_CREATED': 'Votre critique a été publiée avec succès.',
    'TICKET_CREATED': 'Votre ticket a été publié avec succès.',
    'TICKET_UPDATED': 'Votre ticket a été mis à jour avec succès.',
    'REVIEW_UPDATED': 'Votre critique a été mise à jour avec succès.',
    'TICKET_DELETED': 'Votre ticket a été supprimé avec succès.',
    'REVIEW_DELETED': 'Votre critique a été supprimée avec succès.',
}
