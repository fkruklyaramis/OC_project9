from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .forms import TicketForm, ReviewForm
from itertools import chain
from operator import attrgetter
from .models import Ticket, Review


def index(request):
    """Vue pour la page d'accueil avec formulaires de connexion et d'inscription"""
    return render(request, 'litrevu/index.html')


def register(request):
    """Fonction pour gérer l'inscription des utilisateurs"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé avec succès pour {username}')
            # Connecte automatiquement l'utilisateur après inscription
            login(request, user)
            return redirect('flux')  # Rediriger vers la page de flux après inscription
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
    else:
        form = UserCreationForm()

    return render(request, 'litrevu/register.html', {'form': form})


def user_login(request):
    """Fonction pour gérer la connexion des utilisateurs"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('flux')  # Rediriger vers la page de flux après connexion
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')

    return redirect('index')  # Rediriger vers la page d'accueil en cas d'échec de connexion


def user_logout(request):
    """Fonction pour gérer la déconnexion des utilisateurs"""
    auth_logout(request)
    return redirect('index')


@login_required
def flux(request):
    """Vue principale pour afficher le flux des critiques et tickets"""
    return render(request, 'litrevu/flux.html')


@login_required
def create_ticket(request):
    """Vue pour créer un nouveau ticket"""
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('flux')
    else:
        form = TicketForm()

    return render(request, 'litrevu/create_ticket.html', {'form': form})


@login_required
def create_review(request):
    if request.method == 'POST':
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
        ticket_form = TicketForm()
        review_form = ReviewForm()

    return render(request, 'litrevu/create_review.html', {
        'ticket_form': ticket_form,
        'review_form': review_form
    })


@login_required
def posts(request):
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

    return render(request, 'litrevu/posts.html', {'posts': posts})


@login_required
def update_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = TicketForm(instance=ticket)

    return render(request, 'litrevu/update_ticket.html', {'form': form, 'ticket': ticket})


@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        ticket.delete()
        return redirect('posts')

    return render(request, 'litrevu/delete_ticket.html', {'ticket': ticket})


@login_required
def update_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'litrevu/update_review.html', {'form': form, 'review': review})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review.delete()
        return redirect('posts')

    return render(request, 'litrevu/delete_review.html', {'review': review})
