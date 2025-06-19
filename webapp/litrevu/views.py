from django.db.models import Value, CharField
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .forms import TicketForm, ReviewForm
from itertools import chain
from operator import attrgetter
from .models import Ticket, Review, UserFollows
from django.contrib.auth.models import User
from .constants import ERROR_MESSAGES, SUCCESS_MESSAGES, MAX_RATING


def index(request):
    """
    Vue pour la page d'accueil avec formulaires de connexion et d'inscription.

    Affiche la page principale du site qui permet aux utilisateurs de se connecter
    ou de s'inscrire sur la plateforme.

    Args:
        request (HttpRequest): L'objet requête HTTP

    Returns:
        HttpResponse: Rendu de la page d'accueil avec les formulaires
    """
    return render(request, 'litrevu/index.html')


def register(request):
    """
    Fonction pour gérer l'inscription des nouveaux utilisateurs.

    Traite les demandes d'inscription, valide les données soumises,
    crée un nouvel utilisateur et connecte automatiquement l'utilisateur
    après une inscription réussie.

    Args:
        request (HttpRequest): L'objet requête HTTP

    Returns:
        HttpResponse: Rendu de la page d'inscription ou redirection vers le flux
                     si l'inscription est réussie
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, SUCCESS_MESSAGES['ACCOUNT_CREATED'].format(username=username))
            # Connecte automatiquement l'utilisateur après inscription
            login(request, user)
            return redirect('flux')  # Rediriger vers le flux après inscription
        # Si le formulaire n'est pas valide, les erreurs seront affichées dans le template
    else:
        form = UserCreationForm()
    return render(request, 'litrevu/register.html', {'form': form})


def user_login(request):
    """
    Fonction pour gérer la connexion des utilisateurs.

    Authentifie les utilisateurs en vérifiant leurs identifiants,
    établit une session si l'authentification réussit et redirige
    vers le flux principal.

    Args:
        request (HttpRequest): L'objet requête HTTP contenant les identifiants

    Returns:
        HttpResponse: Redirection vers le flux si connexion réussie,
                     ou vers la page d'accueil en cas d'échec
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('flux')  # Rediriger vers la page de flux après connexion
        else:
            messages.error(request, ERROR_MESSAGES['LOGIN_FAILED'])

    return redirect('index')  # Rediriger vers la page d'accueil en cas d'échec de connexion


def user_logout(request):
    """
    Fonction pour gérer la déconnexion des utilisateurs.

    Termine la session de l'utilisateur et le redirige vers la page d'accueil.

    Args:
        request (HttpRequest): L'objet requête HTTP

    Returns:
        HttpResponse: Redirection vers la page d'accueil après déconnexion
    """
    auth_logout(request)
    return redirect('index')


@login_required
def create_ticket(request):
    """
    Vue pour créer un nouveau ticket de demande de critique.

    Permet à un utilisateur connecté de soumettre un nouveau ticket
    avec un titre, une description et éventuellement une image.

    Args:
        request (HttpRequest): L'objet requête HTTP

    Returns:
        HttpResponse: Formulaire de création de ticket ou redirection
                     vers le flux si le ticket est créé avec succès
    """
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, SUCCESS_MESSAGES['TICKET_CREATED'])
            return redirect('flux')
    else:
        form = TicketForm()

    return render(request, 'litrevu/create_ticket.html', {'form': form})


@login_required
def create_review(request, ticket_id=None):
    """
    Crée une critique soit pour un ticket existant, soit avec un nouveau ticket.

    Cette vue permet deux scénarios:
    1. Répondre à un ticket existant avec une critique
    2. Créer simultanément un ticket et sa critique

    Args:
        request (HttpRequest): L'objet requête HTTP
        ticket_id (int, optional): L'ID du ticket à critiquer, si applicable

    Returns:
        HttpResponse: Formulaire de création de critique ou redirection
                     vers le flux si la critique est créée avec succès

    Notes:
        - Vérifie si l'utilisateur a déjà posté une critique pour le ticket
        - Gère deux formulaires lorsqu'un nouveau ticket est créé avec la critique
    """
    # Déterminer si on répond à un ticket existant ou si on crée un nouveau
    existing_ticket = None
    if ticket_id:
        existing_ticket = get_object_or_404(Ticket, id=ticket_id)
        # Vérifier si l'utilisateur a déjà posté une critique pour ce ticket
        if Review.objects.filter(ticket=existing_ticket, user=request.user).exists():
            messages.error(request, ERROR_MESSAGES['ALREADY_REVIEWED'])
            return redirect('flux')

    if request.method == 'POST':
        # Si on répond à un ticket existant, on n'utilise pas le formulaire de ticket
        if existing_ticket:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.ticket = existing_ticket
                review.save()
                return redirect('flux')
        else:
            # Création d'un nouveau ticket et d'une critique
            ticket_form = TicketForm(request.POST, request.FILES)
            review_form = ReviewForm(request.POST)
            if ticket_form.is_valid() and review_form.is_valid():
                # Créer le ticket
                ticket = ticket_form.save(commit=False)
                ticket.user = request.user
                ticket.save()

                # Créer la critique associée au ticket
                review = review_form.save(commit=False)
                review.user = request.user
                review.ticket = ticket
                review.save()

                return redirect('flux')
    else:
        review_form = ReviewForm()
        ticket_form = None if existing_ticket else TicketForm()

    return render(request, 'litrevu/create_review.html', {
        'ticket_form': ticket_form,
        'review_form': review_form,
        'existing_ticket': existing_ticket
    })


@login_required
def posts(request):
    """
    Affiche tous les posts (tickets et critiques) créés par l'utilisateur connecté.

    Récupère et combine les tickets et critiques de l'utilisateur,
    les trie par date de création (du plus récent au plus ancien)
    et les prépare pour l'affichage.

    Args:
        request (HttpRequest): L'objet requête HTTP

    Returns:
        HttpResponse: Rendu de la page contenant tous les posts de l'utilisateur
    """
    # Récupérer les tickets de l'utilisateur
    user_tickets = Ticket.objects.filter(user=request.user)
    # Pour chaque ticket, ajouter un attribut content_type
    for ticket in user_tickets:
        ticket.content_type = 'TICKET'

    # Récupérer les critiques de l'utilisateur
    user_reviews = Review.objects.filter(user=request.user)
    # Pour chaque critique, ajouter un attribut content_type
    for review in user_reviews:
        review.content_type = 'REVIEW'

    # Combiner les deux querysets
    posts = sorted(
        chain(user_tickets, user_reviews),
        key=attrgetter('time_created'),
        reverse=True
    )

    return render(request, 'litrevu/posts.html', {
        'posts': posts,
        'MAX_RATING': MAX_RATING
    })


@login_required
def update_ticket(request, ticket_id):
    """
    Permet à un utilisateur de modifier un ticket qu'il a créé.

    Récupère le ticket spécifié si l'utilisateur en est l'auteur,
    et traite le formulaire de modification si soumis.

    Args:
        request (HttpRequest): L'objet requête HTTP
        ticket_id (int): L'ID du ticket à modifier

    Returns:
        HttpResponse: Formulaire de modification ou redirection vers les posts
                     si la modification est réussie
    Raises:
        Http404: Si le ticket n'existe pas ou n'appartient pas à l'utilisateur
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, SUCCESS_MESSAGES['TICKET_UPDATED'])
            return redirect('posts')
    else:
        form = TicketForm(instance=ticket)

    return render(request, 'litrevu/update_ticket.html', {'form': form, 'ticket': ticket})


@login_required
def delete_ticket(request, ticket_id):
    """
    Permet à un utilisateur de supprimer un ticket qu'il a créé.

    Récupère le ticket spécifié si l'utilisateur en est l'auteur,
    et le supprime après confirmation.

    Args:
        request (HttpRequest): L'objet requête HTTP
        ticket_id (int): L'ID du ticket à supprimer

    Returns:
        HttpResponse: Page de confirmation de suppression ou redirection
                     vers les posts si la suppression est confirmée

    Raises:
        Http404: Si le ticket n'existe pas ou n'appartient pas à l'utilisateur
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        ticket.delete()
        messages.success(request, SUCCESS_MESSAGES['TICKET_DELETED'])
        return redirect('posts')

    return render(request, 'litrevu/delete_ticket.html', {'ticket': ticket})


@login_required
def update_review(request, review_id):
    """
    Permet à un utilisateur de modifier une critique qu'il a créée.

    Récupère la critique spécifiée si l'utilisateur en est l'auteur,
    et traite le formulaire de modification si soumis.

    Args:
        request (HttpRequest): L'objet requête HTTP
        review_id (int): L'ID de la critique à modifier

    Returns:
        HttpResponse: Formulaire de modification ou redirection vers les posts
                     si la modification est réussie

    Raises:
        Http404: Si la critique n'existe pas ou n'appartient pas à l'utilisateur
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, SUCCESS_MESSAGES['REVIEW_UPDATED'])
            return redirect('posts')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'litrevu/update_review.html', {'form': form, 'review': review})


@login_required
def delete_review(request, review_id):
    """
    Permet à un utilisateur de supprimer une critique qu'il a créée.

    Récupère la critique spécifiée si l'utilisateur en est l'auteur,
    et la supprime après confirmation.

    Args:
        request (HttpRequest): L'objet requête HTTP
        review_id (int): L'ID de la critique à supprimer

    Returns:
        HttpResponse: Page de confirmation de suppression ou redirection
                     vers les posts si la suppression est confirmée

    Raises:
        Http404: Si la critique n'existe pas ou n'appartient pas à l'utilisateur
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review.delete()
        messages.success(request, SUCCESS_MESSAGES['REVIEW_DELETED'])
        return redirect('posts')

    return render(request, 'litrevu/delete_review.html', {'review': review})


@login_required
def subscriptions(request):
    """
    Gère les abonnements de l'utilisateur : suivi et ajout d'utilisateurs.

    Cette vue permet à l'utilisateur de:
    1. Voir les utilisateurs qu'il suit
    2. Voir les utilisateurs qui le suivent
    3. Rechercher et suivre de nouveaux utilisateurs

    Args:
        request (HttpRequest): L'objet requête HTTP

    Returns:
        HttpResponse: Rendu de la page des abonnements avec les listes
                     d'abonnés et d'abonnements
    """
    # Obtenir les utilisateurs suivis par l'utilisateur connecté
    followed_users = UserFollows.objects.filter(user=request.user)

    # Obtenir les utilisateurs qui suivent l'utilisateur connecté
    followers = UserFollows.objects.filter(followed_user=request.user)

    error_message = None
    success_message = None

    # Traitement du formulaire de recherche d'utilisateur
    if request.method == 'POST':
        username = request.POST.get('username')

        if username:
            # Vérifier si l'utilisateur cherche à se suivre lui-même
            if username == request.user.username:
                error_message = ERROR_MESSAGES['CANNOT_FOLLOW_SELF']
            else:
                try:
                    user_to_follow = User.objects.get(username=username)

                    # Vérifier si l'utilisateur suit déjà cet utilisateur
                    if UserFollows.objects.filter(user=request.user, followed_user=user_to_follow).exists():
                        error_message = ERROR_MESSAGES['ALREADY_FOLLOWING'].format(username=username)
                    else:
                        # Créer la relation de suivi
                        UserFollows.objects.create(
                            user=request.user,
                            followed_user=user_to_follow
                        )
                        success_message = SUCCESS_MESSAGES['NOW_FOLLOWING'].format(username=username)

                except User.DoesNotExist:
                    error_message = ERROR_MESSAGES['USER_NOT_FOUND'].format(username=username)

    context = {
        'followed_users': followed_users,
        'followers': followers,
        'error_message': error_message,
        'success_message': success_message
    }

    return render(request, 'litrevu/subscriptions.html', context)


@login_required
def unfollow_user(request, user_id):
    """
    Supprime un utilisateur de la liste des suivis.

    Permet à l'utilisateur connecté de cesser de suivre un autre utilisateur
    qu'il suivait précédemment.

    Args:
        request (HttpRequest): L'objet requête HTTP
        user_id (int): L'ID de l'utilisateur à ne plus suivre

    Returns:
        HttpResponse: Redirection vers la page des abonnements avec un message
                     de confirmation ou d'erreur
    """
    try:
        # Trouver la relation de suivi
        user_follow = UserFollows.objects.get(
            user=request.user,
            followed_user__id=user_id
        )
        # Récupérer le nom d'utilisateur pour le message
        username = user_follow.followed_user.username
        # Supprimer la relation
        user_follow.delete()
        messages.success(request, SUCCESS_MESSAGES['UNFOLLOWED'].format(username=username))
    except UserFollows.DoesNotExist:
        # Si la relation n'existe pas, ajouter un message d'erreur
        messages.error(request, ERROR_MESSAGES['FOLLOW_RELATION_NOT_FOUND'])

    return redirect('subscriptions')


@login_required
def flux(request):
    """
    Affiche le flux principal avec les posts intéressants pour l'utilisateur.

    Ce flux montre:
    1. Les tickets et critiques des utilisateurs suivis
    2. Les propres tickets et critiques de l'utilisateur
    3. Les critiques en réponse aux tickets de l'utilisateur

    Pour chaque ticket, la vue vérifie si l'utilisateur y a déjà répondu
    avec une critique pour adapter l'affichage en conséquence.

    Args:
        request (HttpRequest): L'objet requête HTTP

    Returns:
        HttpResponse: Rendu de la page de flux avec tous les posts pertinents
    """
    # 1. Obtenir les utilisateurs suivis par l'utilisateur connecté
    followed_users = UserFollows.objects.filter(user=request.user).values_list('followed_user', flat=True)

    # 2. Récupérer les tickets des utilisateurs suivis + tickets de l'utilisateur connecté
    tickets = Ticket.objects.filter(
        Q(user__in=followed_users) | Q(user=request.user)
    ).annotate(content_type=Value('TICKET', CharField()))

    # 3. Récupérer les critiques qui:
    #    - Sont des utilisateurs suivis
    #    - Ou sont de l'utilisateur connecté
    #    - Ou répondent à un ticket de l'utilisateur connecté
    reviews = Review.objects.filter(
        Q(user__in=followed_users) |
        Q(user=request.user) |
        Q(ticket__user=request.user)
    ).annotate(content_type=Value('REVIEW', CharField()))

    # 4. Combiner et trier les posts par date de création (les plus récents d'abord)
    posts = sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )

    # 5. Pour chaque ticket, déterminer si une critique a déjà été postée par l'utilisateur connecté
    for post in posts:
        if hasattr(post, 'content_type') and post.content_type == 'TICKET':
            post.has_review_from_user = Review.objects.filter(
                ticket=post,
                user=request.user
            ).exists()

    return render(request, 'litrevu/flux.html', {
        'posts': posts,
        'MAX_RATING': MAX_RATING
    })
