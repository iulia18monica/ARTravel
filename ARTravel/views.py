from django.http import HttpResponse
from django.template import loader
from .models import Locatie
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from .models import Locatie, Favorit, Review, SavedRoute
import urllib.parse

def index(request):
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def attractions(request):
    return render(request,'attractions.html')

def instructions(request):
    return render(request, 'instructions.html')

def reviews(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            content = request.POST.get('content')
            rating = request.POST.get('rating')
            
            # Creăm și salvăm recenzia în baza de date
            Review.objects.create(
                user=request.user,
                content=content,
                rating=rating
            )
            return redirect('reviews') # Reîncărcăm pagina ca să apară noua recenzie
        else:
            return redirect('login') # Dacă nu e logat, îl trimitem la login

    # 2. Luăm toate recenziile din baza de date, cele mai noi primele
    all_reviews = Review.objects.all().order_by('-created_at')

    return render(request, 'reviews.html', {'reviews': all_reviews})

@login_required
def journey(request):
    # Luăm ID-urile locațiilor favorite ale userului
    favorite_ids = Favorit.objects.filter(user=request.user).values_list('locatie_id', flat=True)
    # Luăm obiectele Locatie efective
    favoritele_mele = Locatie.objects.filter(id__in=favorite_ids)
    
    # Le trimitem în HTML sub numele de 'favorite'
    return render(request, 'journey.html', {'favorite': favoritele_mele})

def register(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        email = request.POST.get('email')
        passw = request.POST.get('password')

        if User.objects.filter(username=u_name).exists():
            messages.error(request, "Numele de utilizator există deja.")
        else:
            # Creăm utilizatorul cu parola criptată
            User.objects.create_user(username=u_name, email=email, password=passw)
            messages.success(request, f'Cont creat pentru {u_name}! Te poți loga.')
            return redirect('login')
    return render(request, 'accounts/register.html')

def login(request):
    if request.method == 'POST':
        u_name = request.POST.get('username') # Preluăm username-ul din câmpul 'name="username"'
        passw = request.POST.get('password')
        
        user = authenticate(request, username=u_name, password=passw)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Date de logare incorecte.")
    return render(request, 'login.html')

def category_view(request, category_name):
    # 1. Luăm locațiile
    locatii = Locatie.objects.filter(categorie=category_name)
    
    # 2. Pregătim lista de favorite (inițial goală)
    user_favorites_ids = []
    
    # 3. Dacă e logat, umplem lista cu ID-urile favoritelor LUI
    if request.user.is_authenticated:
        user_favorites_ids = list(Favorit.objects.filter(user=request.user).values_list('locatie_id', flat=True))

    # 4. Trimitem datele către HTML (inclusiv lista de ID-uri!)
    return render(request, 'location_list.html', {
        'locatii': locatii,
        'category': category_name,
        'user_favorites_ids': user_favorites_ids # <--- ASTA LIPSEA
    })

@login_required
def toggle_favorite(request, locatie_id):
    locatie = get_object_or_404(Locatie, id=locatie_id)
    # Verificăm dacă există deja la favorite
    favorit_existent = Favorit.objects.filter(user=request.user, locatie=locatie)
    
    if favorit_existent.exists():
        favorit_existent.delete() # Ștergem dacă există (un-favorite)
    else:
        Favorit.objects.create(user=request.user, locatie=locatie) # Adăugăm dacă nu există
        
    return redirect(request.META.get('HTTP_REFERER', 'attractions'))

@login_required
def favorite_list(request):
    # Luăm toate favoritele utilizatorului și le filtrăm pe categorii
    fave_user = Favorit.objects.filter(user=request.user)
    
    context = {
        'art_faves': fave_user.filter(locatie__categorie='art'),
        'food_faves': fave_user.filter(locatie__categorie='food'),
        'selfcare_faves': fave_user.filter(locatie__categorie='selfcare'),
    }
    return render(request, 'favorites.html', context)

@login_required
def generate_route(request):
    if request.method == 'POST':
        puncte_traseu_nume = []  # Pentru URL-ul Google Maps
        nume_locatii_simple = [] # Pentru descrierea text (ex: "Muzeu, Parc, Restaurant")
        
        # Iterăm prin cele 6 input-uri
        for i in range(1, 7):
            loc_id = request.POST.get(f'point_{i}')
            
            if loc_id:
                try:
                    locatie = Locatie.objects.get(id=loc_id)
                    
                    # 1. Construim numele pentru URL
                    nume_cautare = f"{locatie.nume}, Cluj-Napoca"
                    puncte_traseu_nume.append(urllib.parse.quote(nume_cautare))
                    
                    # 2. Păstrăm numele simplu pentru descriere
                    nume_locatii_simple.append(locatie.nume)
                    
                except Locatie.DoesNotExist:
                    continue

        if not puncte_traseu_nume:
            return redirect('journey')
        
        # Construim URL-ul Google Maps
        base_url = "https://www.google.com/maps/dir/"
        destinations_str = "/".join(puncte_traseu_nume)
        # Formatul // asigură pornirea de la locația curentă
        maps_url = f"{base_url}/{destinations_str}"

        # --- VERIFICĂM CE BUTON A APĂSAT UTILIZATORUL ---
        action = request.POST.get('action')

        if action == 'save':
            # Dacă vrea să salveze, preluăm numele rutei
            nume_ruta = request.POST.get('route_name')
            
            # Dacă nu a pus nume, generăm unul default
            if not nume_ruta:
                nume_ruta = f"Traseu {len(nume_locatii_simple)} locații"

            # Creăm descrierea (lista de locații separate prin virgulă)
            descriere = ", ".join(nume_locatii_simple)

            # Salvăm în baza de date
            SavedRoute.objects.create(
                user=request.user,
                nume_ruta=nume_ruta,
                descriere_locatii=descriere,
                google_maps_url=maps_url
            )
            
            # Redirecționăm către lista de rute salvate (routes.html)
            return redirect('routes')

        else:
            # Dacă e doar "Generate", deschidem Google Maps direct
            return redirect(maps_url)

    return redirect('journey')

@login_required
def routes_list(request):
    # Luăm rutele userului
    rute = SavedRoute.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'routes.html', {'rute': rute})

@login_required
def delete_route(request, route_id):
    # Ștergem ruta exact ca la favorite
    ruta = get_object_or_404(SavedRoute, id=route_id, user=request.user)
    
    if request.method == 'POST':
        ruta.delete()
        
    return redirect('routes')