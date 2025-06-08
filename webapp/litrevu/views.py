from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .forms import TicketForm


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